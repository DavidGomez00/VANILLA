# Changelog

Changes made to the code and documentation after the benchmark release. Dates are in ISO format. None of
these changes are committed yet.

## 2026-09-21

### Added

- **`KG_Normalization/tsv_to_nt.py`**: converts a tab-separated triples file into N-Triples.
  Command line and importable `convert()` function. See [07](07-tsv-to-nt.md).
- **`docs/`**: this documentation.

### Changed

- **Validation results are written outside the constraints folder.**
  - Before: `Constraints/<constraints_folder>/result_<KG>/`.
  - Now: `Validation_results/<KG>/`.
  - Reason: TravSHACL parses every `.ttl` file under the constraints folder. A `validationReport.ttl`
    produced by an earlier run was parsed as a shape file on the next run and made it fail.
    With inputs and outputs in separate folders, runs can be repeated safely.
- **`Validation.py`**: `travshacl(enrichedKG, constraints, kg)` is now
  `travshacl(enrichedKG, constraints, output_dir)`. It creates `output_dir` if it does not exist.
- **`Symbolic_predictions.py`**: `initialize()` also returns `validation_folder` (`Validation_results/<KG>`),
  logs it, and the main block passes it to `travshacl` and `transform`. The shapes file given to `transform`
  is derived from `constraints_folder`.
- **`Normalization_transform.py`**: `transform(enriched_kg, kg_name=None)` is now
  `transform(enriched_kg, kg_name=None, shapes_file=None, validation_dir=None)`.
  - Before: the shapes and report were looked up at `Constraints/<kg_name>/<kg_name>.ttl` and
    `Constraints/<kg_name>/result_<kg_name>/validationReport.ttl`, so `constraints_folder` in `input.json`
    only had an effect on validation, not on normalization.
  - Now: the paths are passed in. If omitted, they default to `Constraints/<kg_name>/<kg_name>.ttl` and
    `Validation_results/<kg_name>/validationReport.ttl`.
- **`KG_Normalization/README.md`**: output list updated to mention `Validation_results/<KG>/`.
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
  `Validation_results/<kg_name>/`.
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
- The bundled `KG/FrenchRoyalty/french_royalty.nt` uses the namespace `http://FrenchRoaylty.org/`, while
  `Constraints/FrenchRoyalty/FrenchRoyalty.ttl` uses `http://FrenchRoyalty.org/`.
- `Validated_KG_Completion/README.md` refers to `input.json`; the scripts read `input_KGC.json` and
  `input_KGC_hpo.json`.
