import sys
import re
from importlib import resources
import pyhmmer

HMM_FILE = resources.files('tmmpred.data').joinpath('fmo_bvmo.hmm')
HMM = 'Tmm'
NOISE_CUTOFF = 40.0 # Pfam NC
TRUSTED_CUTOFF = 272.0 # Pfam TC
HMM_LENGTH = 455
FAD = 'GaGPsG'
NAD = 'Gssysa'
HMM_NEIGHBOUR = 'FMO2'

class TmmHit:
    def __init__(self, name, sequence):
        self.name = name
        self.sequence = sequence
        self.coverage = -1.0
        self.score = -1.0
        self.d_score = float('inf')
        self.d_name = ''
        self.fad_motif = ''
        self.nad_motif = ''

    def __repr__(self):
        reprlist = [self.name,
                    str(len(self.sequence)),
                    str(f'{self.coverage:.1f}'),
                    str(f'{self.score:.1f}'), 
                    str(f'{self.d_score:.1f}'), 
                    self.d_name, 
                    self.fad_motif, 
                    self.nad_motif]
        return '\t'.join(reprlist)

    def format(self):
        return self.__repr__()

    def format_quick(self):
        reprlist = [self.name,
                    str(len(self.sequence)),
                    str(f'{self.coverage:.1f}'),
                    str(f'{self.score:.1f}'),
                    self.fad_motif, 
                    self.nad_motif]
        return '\t'.join(reprlist)

class TmmHits:
    def __init__(self, sequences, raw_results, quick=False, sorted_=True, filter_=True, verbose=False):
        self.names = []
        self.tmmhits = []
        self._scores = []
        self._d_scores = []

        self._quick = quick
        self._filter = filter_
        self._verbose = verbose

        self._initialise_tmmhits(sequences)
        self._parse_results(raw_results)
        if sorted_: self._sort()


    def __repr__(self):
        return ', '.join(self.names)

    def _initialise_tmmhits(self, sequences):
        for seq in sequences:
            tmmhit = TmmHit(seq.name.decode(), seq.textize().sequence)
            self.names.append(tmmhit.name)
            self.tmmhits.append(tmmhit)
            self._scores.append(-1)
            self._d_scores.append(-1)

    def _parse_results(self, raw_results):
        for hit in raw_results[HMM]:
            name = hit.name.decode()
            i = self.names.index(name)
            tmmhit = self.tmmhits[i]
            tmmhit.coverage = (hit.best_domain.alignment.hmm_to - hit.best_domain.alignment.hmm_from)/HMM_LENGTH*100
            tmmhit.score = hit.best_domain.score
            tmmhit.fad_motif = self._format_motif('FAD', FAD, hit.best_domain.alignment, tmmhit.sequence)
            tmmhit.nad_motif = self._format_motif('NAD', NAD, hit.best_domain.alignment, tmmhit.sequence)

        for hmm in raw_results.keys():
            if hmm == HMM: continue
            for hit in raw_results[hmm]:
                name = hit.name.decode()
                i = self.names.index(name)
                tmmhit = self.tmmhits[i]
                d_score = tmmhit.score - hit.best_domain.score
                if d_score < tmmhit.d_score:
                    tmmhit.d_score = d_score
                    tmmhit.d_name = hmm

    def _format_motif(self, name, motif, alignment, sequence):
        motif_hit = re.search(motif, alignment.hmm_sequence)
        if motif_hit:
            motif_hmm = alignment.hmm_sequence[motif_hit.start():motif_hit.end()]
            motif = alignment.target_sequence[motif_hit.start():motif_hit.end()]
            motif_target = re.search(motif, sequence)
            if not motif_target:
                return f'{name}: ({motif_hmm}): [incomplete: {motif}]'
            motif_start, motif_end = motif_target.start(), motif_target.end()
            return f'{name} ({motif_hmm}): {motif_start}-{motif}-{motif_end}'
        else:
            return f'{name}: -'

    def _format_html(self, results):
        html = '''
<style>
    .df tbody tr:nth-child(odd) { background-color: lightgray; }
</style>
<table class="df">
'''
        heading = True
        lines = results.split('\n')
        for line in lines:
            elements = line.split('\t')
            if heading:
                html += '''
<thead>
<tr style="text-align: right;">
'''
                for element in elements:
                    html += f'<th>{element}</th>\n'
                html += '''
</tr>
</thead>
</tbody>
'''
                heading = False
            else:
                html += '<tr>\n'
                for element in elements:
                    html += f'<td>{element}</td>\n'
                html += '</tr>\n'
        html += '''
</tbody>
</table>
'''
        return html

    def format_results(self, html=False):
        count = 0
        results = ''
        formated_hits = []

        if not self.names:
            return 'No hits.'
        
        if self._quick:
            results += 'Query\tLength\tCoverage\tScore\tFAD motif\tNAD motif\n'
            for tmmhit in self.tmmhits:
                if self._filter and tmmhit.d_score <= 0:
                    continue
                else:
                     formated_hits.append(tmmhit.format_quick())
                count += 1
        else:
            results += 'Query\tLength\tCoverage\tScore\tDelta score\tD name\tFAD motif\tNAD motif\n'
            for tmmhit in self.tmmhits:
                if self._filter and (tmmhit.d_score <= 0 or tmmhit.d_score == float('inf')):
                    continue
                else:
                    if tmmhit.d_score != float('inf'):
                        formated_hits.append(tmmhit.format())
                count += 1
        results += '\n'.join(formated_hits)

        if self._verbose: 
            if not self._quick and self._filter:
                eprint(f'Predicted Tmm sequences after filtering: {count:,}')
            else:
                eprint(f'Predicted Tmm sequences: {count:,}')

        if html:
            return self._format_html(results)
        else:
            return results

    def _sort(self):
        for i in range(len(self.tmmhits)):
            self._scores[i] = self.tmmhits[i].score
            self._d_scores[i] = self.tmmhits[i].d_score
        self._scores, self._d_scores, self.names, self.tmmhits = zip(*sorted(zip(self._scores, self._d_scores, self.names, self.tmmhits), reverse=True))

def eprint(*args, **kwargs):
    # print status messages to stderr
    print(*args, file=sys.stderr, **kwargs)

def get_tmm_candidates(sequences, hits, alphabet, score_threshold=0):
    filtered_hits = []
    tmm_candidates = pyhmmer.easel.DigitalSequenceBlock(alphabet)
    tmm_candidate_ids = []
    for hit in hits:
        if hit.best_domain.score >= score_threshold:
            tmm_candidate_ids.append(hit.best_domain.alignment.target_name)
            filtered_hits.append(hit)
    while tmm_candidate_ids:
        seq = sequences.pop()
        if seq.name in tmm_candidate_ids:
            tmm_candidate_ids.remove(seq.name)
            tmm_candidates.append(seq)
    return tmm_candidates, filtered_hits
            
def run(sequences, cutoff=NOISE_CUTOFF, quick=False, deep=False, filter_=True, verbose=False):
    if quick: # Override cutoff and filter_
        cutoff = TRUSTED_CUTOFF
        filter_ = False

    # Set up pipeline
    alphabet = pyhmmer.easel.Alphabet.amino()
    background = pyhmmer.plan7.Background(alphabet)
    pipeline = pyhmmer.plan7.Pipeline(alphabet, background=background)
    
    # Read query sequences
    try:
        with pyhmmer.easel.SequenceFile(sequences, digital=True, alphabet=alphabet) as seq_file:
            sequences = seq_file.read_block()
    except ValueError as e:
        if isinstance(sequences, str):
            name = sequences # If file path is provided
        else:
            name = sequences.name # If file object is given 
        raise Exception(f"Not a valid FASTA-formated protein sequence file: '{name}'")
            

    # Initial HMM search
    if verbose: eprint(f'Running hmmsearch using Tmm profile: { HMM}.')
    if verbose: eprint(f'Searching {len(sequences):,} sequences.')
    with pyhmmer.plan7.HMMFile(HMM_FILE) as hmms:
        for hmm in hmms:
            if hmm.name.decode() == HMM:
                hits = pipeline.search_hmm(query=hmm, sequences=sequences)
                sequences, filtered_hits = get_tmm_candidates(sequences, hits, alphabet, score_threshold=cutoff)
                break
    if verbose: eprint(f'Hits above cutoff ({cutoff}): {len(filtered_hits):,}.')
    raw_results = {}
    raw_results[hmm.name.decode()] = filtered_hits

    # Additional HMM searches for filtering results
    # Quick: do not search additional HMM profiles
    # Deep: search all additional HMM profiles
    # Else: only search the first additional HMM profile
    if not quick:
        if deep:
            if verbose: eprint(f'Running hmmsearch using other FMO-like profiles:')
        else:
            if verbose: eprint(f'Running hmmsearch using nearest neighbour FMO-like profile:')

        with pyhmmer.plan7.HMMFile(HMM_FILE) as hmms:
            for hmm in hmms:
                if hmm.name.decode() != HMM:
                    if verbose: eprint(f'  {hmm.name.decode()}')
                    hits = pipeline.search_hmm(query=hmm, sequences=sequences)
                    raw_results[hmm.name.decode()] = hits
                    if not deep: break
    
    # Compile, get, and return results                
    return TmmHits(sequences, raw_results, quick=quick, filter_=filter_, verbose=verbose)

