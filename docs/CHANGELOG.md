# Changelog

Changes made to the code and documentation after the benchmark release. Dates are in ISO format.

## 2026-09-21

### Added

- **`KG_Normalization/tsv_to_nt.py`**: converts a tab-separated triples file into N-Triples.
  Command line and importable `convert()` function. See [07](07-tsv-to-nt.md).
- **`docs/`**: this documentation.

### Changed

- **`pandasql` removed from `Symbolic_predictions.py`.** The two `sqldf` queries in `process_rules` are now
  `pandas` filtering and sorting with the same result. Reason: `pandasql` fails with `pandas` 2.2 or newer
  and `SQLAlchemy` 1.4 (`'Connection' object has no attribute 'cursor'`). `pandasql` is also removed from
  `requirements.txt`.
- **`input.json` and `KG_Normalization/README.md`:** `FrenchRoaylty` corrected to `FrenchRoyalty` in `prefix`
  and `constraints_folder`. The old values produced 0 predictions and a "no shapes" error.
- **One output folder per KG for all results.**
  - Before: validation results in `Constraints/<constraints_folder>/result_<KG>/`, transformed KGs in
    `Transformed_<KG>/`, predictions in `Predictions/`.
  - Now: `Output/<KG>/validation/`, `Output/<KG>/transformed/`, `Output/<KG>/predictions/` and
    `Output/<KG>/enriched/`.
  - Existing `Transformed_<Benchmark>/` folders in the repository are earlier results and are not touched.
  - Reason: TravSHACL parses every `.ttl` file under the constraints folder. A `validationReport.ttl`
    produced by an earlier run was parsed as a shape file on the next run and made it fail.
    With inputs and outputs in separate folders, runs can be repeated safely.
- **Output files share one naming convention, `<KG>_<stage>`, in lowercase.**

  | Before | Now |
  |---|---|
  | `Predictions/<KG>_predictions/<predicate>.tsv` | `Output/<KG>/predictions/<predicate>.tsv` |
  | `Predictions/<KG>_EnrichedKG/<KG>_Enriched_KG.nt` | `Output/<KG>/enriched/<KG>_enriched.nt` |
  | `Transformed_<KG>/InitialTransformedKG_<KG>.nt` | `Output/<KG>/transformed/<KG>_expanded.nt` |
  | `Transformed_<KG>/TransformedKG_<KG>.nt` | `Output/<KG>/transformed/<KG>_normalized.nt` |

  Everything a run writes for a KG is now under `Output/<KG>/` (`predictions/`, `enriched/`, `validation/`,
  `transformed/`). The `Predictions/` folders of the other benchmarks are earlier results and are not moved.
  "Expanded" is the graph after predicate-object expansion, "normalized" the final graph. The files written
  by TravSHACL in `validation/` keep their names. Benchmark results already committed under the old names
  are not renamed.
- **`Validation.py`**: `travshacl(enrichedKG, constraints, kg)` is now
  `travshacl(enrichedKG, constraints, output_dir)`. It creates `output_dir` if it does not exist.
- **`Symbolic_predictions.py`**: `initialize()` also returns `validation_folder` (`Output/<KG>/validation`)
  and `transformed_folder` (`Output/<KG>/transformed`), logs them, and the main block passes them to
  `travshacl` and `transform`. The shapes file given to `transform`
  is derived from `constraints_folder`.
- **`Normalization_transform.py`**: `transform(enriched_kg, kg_name=None)` is now
  `transform(enriched_kg, kg_name=None, shapes_file=None, validation_dir=None, output_dir=None)`.
  - Before: the shapes and report were looked up at `Constraints/<kg_name>/<kg_name>.ttl` and
    `Constraints/<kg_name>/result_<kg_name>/validationReport.ttl`, so `constraints_folder` in `input.json`
    only had an effect on validation, not on normalization.
  - Now: the paths are passed in. If omitted, they default to `Constraints/<kg_name>/<kg_name>.ttl` and
    `Output/<kg_name>/validation/validationReport.ttl`. Transformed KGs are written to `output_dir`
    (default `Output/<kg_name>/transformed`).
- **`KG_Normalization/README.md`**: output list updated to mention `Output/<KG>/validation/`.
- **Rules CSV columns are now lowercase only.** `Symbolic_predictions.py` requires `body`, `head`,
  `pca_confidence`, `std_confidence` and `functional_variable`.
  - Before: `Body`, `Head`, `PCA_Confidence` or `Pca_Confidence`, `Std_Confidence` or `Standard_Confidence`,
    `Functional_variable`.
  - A file missing any of them stops with `ValueError: Missing required column(s) in rules file: ...`.
  - The headers of the bundled files `Rules/DB100K.csv`, `SGKG4-0.3.csv`, `synLC_1000.csv`,
    `synLC_10000.csv` and `YAGO3-10.csv` were converted to lowercase snake_case
    (`Head Coverage`/`Head_Coverage` to `head_coverage`, `Support` to `positive_examples`,
    `Body Size`/`Body_Size` to `body_size`, `Pca Body Size`/`Pca_Body_Size` to `pca_body_size`). Only the
    header line changed.

### Migration notes

- Existing `Constraints/<Benchmark>/result_<Benchmark>/` folders are untouched and still contain earlier
  results. They are not read by the current code. If you point a run at one of those constraint folders,
  delete or move its `result_*` subfolder first (TravSHACL would parse the report inside).
- Code calling `travshacl(..., kg)` must pass an output directory instead of the KG name.
- Code calling `transform(...)` with the default arguments now expects the report under
  `Output/<kg_name>/validation/`, and writes its results to `Output/<kg_name>/transformed/`.
- Rules files from other sources must be converted to the lowercase column names; see
  [04](04-data-formats.md#column-names-from-other-tools).
- The normalization step still expects the shapes in `Constraints/<constraints_folder>/<constraints_folder>.ttl`.

### Behaviour documented (not changed)

These were found while writing the documentation and are unchanged in the code:

- `FILTER NOT EXISTS` shapes produce violations but do not change the normalized graph
  ([06](06-shacl-constraints.md#what-gets-rewritten)).
- Rules with PCA confidence exactly `1.0` are never used ([03](03-configuration.md#pca_threshold)).
- `log_level` in `input.json` is ignored.
- The graph is re-read from disk for every rule, which dominates the run time on large graphs.
- `Validated_KG_Completion/README.md` refers to `input.json`; the scripts read `input_KGC.json` and
  `input_KGC_hpo.json`.
