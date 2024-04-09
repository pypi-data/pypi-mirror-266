# Tmmpred 

Tmmpred can be used to identify sequences belonging to a subgroup of flavine-containing monooxygenases defined by bacterial trimethylamine monooxygenases (Tmms; [Goris et al. 2020](https://doi.org/10.1128/AEM.02105-20)). The tool is built on a set of manually curated profile HMMs and is implemented in Python using the [PyHMMER module](https://pyhmmer.readthedocs.io/).


## Installation

The Tmmpred can be installed from [PyPI](https://pypi.org/project/tmmpred/):
```
$ pip install tmmpred
```

## Run Tmmpred

Tmmpred installs as a script that can be run from the command line:
```
$ tmmpred -h
usage: tmmpred [-h] [-q] [-d] [-c CUTOFF] [-n] [--html] [-v] sequence_file

Predict Tmm sequences (FMO subfamily with trimethylamine monooxidase activity).

positional arguments:
  sequence_file         FASTA-formated protein sequences.

options:
  -h, --help            show this help message and exit
  -q, --quick           Search with Tmm HMM profile only and use trusted score cutoff: 272.0.
  -d, --deep            Search with Tmm HMM profile using noise score cutoff 40.0 and filter using all FMO-like HMM profiles.
  -c CUTOFF, --cutoff CUTOFF
                        Score cutoff [float, default=40.0 (noise score cutoff)].
  -n, --nofilter        Do not filter using other FMO-like HMM profiles.
  --html                Format results as HTML.
  -v, --verbose         Show details about running tmmpred.
```