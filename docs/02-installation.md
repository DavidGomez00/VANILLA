# 02 - Installation

## Requirements

- Python 3.10 (the version this documentation was tested with; the repository's `.python-version` file is
  local and git-ignored).
- Git.
- Optional: a CUDA-capable GPU for part 2 (embedding training). Part 1 needs no GPU.
- Optional: Java, only if you mine rules yourself with AMIE (see [08](08-normalizing-your-own-graph.md)).

## Steps

```bash
git clone git@github.com:SDM-TIB/VANILLA.git
cd VANILLA

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
```

`requirements.txt` lists:

```
pandas
numpy
pykeen
rdflib
TravSHACL
SQLAlchemy==1.4.41
```

## Version pins that matter

`SQLAlchemy` is pinned to 1.4.41. The rule filtering in `Symbolic_predictions.py` no longer uses `pandasql`,
so the pipeline runs with current `pandas` and `numpy` 2.x. The combination `pandas` 2.3, `numpy` 2.2,
`SQLAlchemy` 1.4.41, `rdflib` 7.6 and `TravSHACL` was used to run the full normalization pipeline
successfully (Python 3.10).

Earlier versions of the script used `pandasql`, which fails with `pandas` 2.2 or newer combined with
`SQLAlchemy` 1.4. See [11](11-troubleshooting.md) if you are running an older copy of the script.

## Extra packages for part 2

`Validated_KG_Completion/KGC.py` imports `torch` and `matplotlib`, which are not in `requirements.txt`.
`pykeen` normally installs `torch`, but `matplotlib` may need to be installed separately:

```bash
pip install matplotlib
```

## Checking the installation

From `KG_Normalization/`:

```bash
python -c "import rdflib, pandas, TravSHACL; print('ok')"
```

If this prints `ok`, part 1 can run.
