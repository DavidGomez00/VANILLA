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
pandasql
TravSHACL
SQLAlchemy==1.4.41
```

## Version pins that matter

`pandasql` is not compatible with recent `pandas` releases. With `pandas` 2.x the first rule-filtering query
fails with:

```
AttributeError: 'Connection' object has no attribute 'cursor'
```

This is why `SQLAlchemy` is pinned to 1.4.41. If you hit that error, install an older pandas:

```bash
pip install "pandas<2" "numpy<2"
```

This combination (`pandas<2`, `numpy<2`, `SQLAlchemy==1.4.41`, `rdflib` 7.x, `TravSHACL` 1.9) was used to run
the full normalization pipeline successfully.

## Extra packages for part 2

`Validated_KG_Completion/KGC.py` imports `torch` and `matplotlib`, which are not in `requirements.txt`.
`pykeen` normally installs `torch`, but `matplotlib` may need to be installed separately:

```bash
pip install matplotlib
```

## Checking the installation

From `KG_Normalization/`:

```bash
python -c "import rdflib, pandas, pandasql, TravSHACL; print('ok')"
```

If this prints `ok`, part 1 can run.
