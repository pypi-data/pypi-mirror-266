import os
import argparse
from tmmpred import tmmpred

NOISE_CUTOFF = tmmpred.NOISE_CUTOFF
TRUSTED_CUTOFF = tmmpred.TRUSTED_CUTOFF

def main():
    description = 'Predict Tmm sequences (FMO subfamily with trimethylamine monooxidase activity).'
    parser = argparse.ArgumentParser(prog='tmmpred',
                                     description=description)
    parser.add_argument('sequence_file', type=argparse.FileType('rb'), help='FASTA-formated protein sequences.')
    parser.add_argument('-q', '--quick', action='store_true', help=f'Search with Tmm HMM profile only and use trusted score cutoff: {TRUSTED_CUTOFF}.')
    parser.add_argument('-d', '--deep', action='store_true', help=f'Search with Tmm HMM profile using noise score cutoff {NOISE_CUTOFF} and filter using all FMO-like HMM profiles.')
    parser.add_argument('-c', '--cutoff', type=float, help=f'Score cutoff [float, default={NOISE_CUTOFF} (noise score cutoff)].', default=NOISE_CUTOFF)
    parser.add_argument('-n', '--nofilter', action='store_true', help='Do not filter using other FMO-like HMM profiles.')
    parser.add_argument('--html', action='store_true', help='Format results as HTML.')
    parser.add_argument('-v', '--verbose', action='store_true', help='Show details about running tmmpred.')
    args = parser.parse_args()
    try:
        tmmhits = tmmpred.run(args.sequence_file, cutoff=args.cutoff, quick=args.quick, deep=args.deep, filter_=not args.nofilter, verbose=args.verbose)
    except Exception as e:
        raise SystemExit(e)

    print(tmmhits.format_results(args.html))

if __name__ == '__main__':
    main()
