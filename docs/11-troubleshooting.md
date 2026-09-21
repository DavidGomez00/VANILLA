# 11 - Troubleshooting

Each entry gives the symptom, the cause, and the fix.

## `AttributeError: 'Connection' object has no attribute 'cursor'`

**Where:** first call to `sqldf` in `process_rules`.
**Cause:** `pandasql` does not work with `pandas` 2.x and `SQLAlchemy` 2.x.
**Fix:** `pip install "pandas<2" "numpy<2" "SQLAlchemy==1.4.41"`. See [02](02-installation.md).

## `ValueError: Missing required column(s) in rules file: ...`

**Cause:** the rules file does not use the required lowercase column names (`body`, `head`,
`pca_confidence`, `std_confidence`, `functional_variable`). Capitalized headers such as `Body` or
`PCA_Confidence`, or variants such as `Standard_Confidence`, are rejected. The message lists the columns that
were found.
**Fix:** rename the columns, see [04](04-data-formats.md#column-names-from-other-tools).

## `No rules found meeting the PCA confidence threshold criteria.`

**Cause:** no rule has `pca_threshold < pca_confidence < 1`. A rules file in which every rule has
confidence `1.0` always triggers this.
**Effect:** no predictions; the run continues with an empty graph, so validation and normalization operate
on nothing. Do not read a "successful" run in this case as a normalized graph.
**Fix:** use rules with confidence between the threshold and 1, or lower `pca_threshold`.

## `Bad syntax (Prefix ":" not bound)` during validation

```
"b'@prefix sh: <http://www.w3.org/ns/shacl#> . \r\n\r\n'^b':report a sh:ValidationReport ; ...
```

**Cause:** the constraints folder contains a stale `validationReport.ttl` (for example in a
`result_<KG>/` subfolder from an old run), and TravSHACL is parsing it as a shape file.
**Fix:** use a constraints folder that contains only shape files. Results are now written to
`Validation_results/<KG>/`, so this does not recur for new runs. Remove any leftover `result_*` folder from
the constraints folder you point at.

## Validation finds 0 violations on a graph that should have some

**Cause A:** the namespace in the shapes differs from the one in the graph, so the shape matches no nodes.
For instance `http://FrenchRoaylty.org/` (graph) vs `http://FrenchRoyalty.org/` (shape).
**Cause B:** `sh:targetClass` names a class that has no `rdf:type` triples in the graph.
**Fix:** align the namespace and check `stats.txt` (`all targets` should be greater than zero).

## Violations are found but the normalized graph equals the initial one

**Cause:** the shapes use `FILTER NOT EXISTS`. Such shapes are validated but the rewrite for them is the
identity. The run prints `Applying N transformations...` regardless.
**Fix:** express the anomaly with `FILTER EXISTS`, see [06](06-shacl-constraints.md#what-gets-rewritten).

## Normalization does not change anything and `Found patterns for 0 shapes`

**Cause:** the shapes file is not found by name, or its shapes have no `sh:NodeShape` type / no extractable
patterns. The normalization step reads `Constraints/<constraints_folder>/<constraints_folder>.ttl`.
**Fix:** name the file after the folder; make sure each shape is `a sh:NodeShape` with `sh:sparql`, and that
predicates are written as `<full IRI>`.

## `FileNotFoundError` for `Validation_results/<KG>/validationReport.ttl`

**Cause:** validation did not complete, so no report exists, or `transform` was called by hand with a
different `validation_dir`.
**Fix:** re-run the whole pipeline, or pass `validation_dir` explicitly to `transform`.

## `Error parsing line N` while loading the graph

**Cause:** a line in the `.nt` file is not valid N-Triples (an unescaped character in an IRI, a missing
` .`, a literal, ...). The line is skipped.
**Fix:** regenerate the file with [tsv_to_nt.py](07-tsv-to-nt.md), which percent-encodes unsafe characters.

## Nothing is predicted for a relation that has rules

**Causes:**
- The head's triples already exist for every binding (the graph is already complete for that relation).
- The rules mention relations your graph does not contain.
- The `prefix` in `input.json` does not match the graph's namespace.
- The rule has a `functional_variable` other than `?a`, which restricts the query (see
  [05](05-normalization-pipeline.md#14-build-and-run-the-sparql-query)).

## The run is slow

The graph is parsed again for every rule. Reduce the number of rules (raise `pca_threshold`) or work on a
smaller graph while developing.

## `input.json` changes have no effect on logging

`log_level` is not read by `Symbolic_predictions.py`; it always logs at `INFO`.

## Part 2: `Configuration file input_KGC.json not found`

`KGC.py` reads `input_KGC.json` and `KGC_hpo.py` reads `input_KGC_hpo.json`, both relative to the current directory. Run the scripts from inside `Validated_KG_Completion/`.
