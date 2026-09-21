# 03 - Configuration reference

Both parts of VANILLA are configured with JSON files. The normalization pipeline reads
`KG_Normalization/input.json`. It is listed in `.gitignore` so local run settings are not tracked by
accident.

## KG_Normalization/input.json

```json
{
  "KG": "FrenchRoyalty",
  "prefix": "http://FrenchRoyalty.org/",
  "rules_file": "french_royalty.csv",
  "rdf_file": "french_royalty.nt",
  "constraints_folder": "FrenchRoyalty",
  "log_level": "INFO",
  "pca_threshold": 0.75
}
```

| Key | Type | Meaning | Used to build |
|---|---|---|---|
| `KG` | string | Name of the run. Names the input folder and all output folders/files. | `KG/<KG>/`, `Output/<KG>/validation/`, `Output/<KG>/transformed/` |
| `prefix` | string | Namespace prepended to bare names when reading rules, and stripped from results. Must end in `/` or `#`. | SPARQL `PREFIX ex:` |
| `rules_file` | string | File name of the rules CSV. It sits next to the graph, in the folder of the KG. | `KG/<KG>/<rules_file>` |
| `rdf_file` | string | File name of the N-Triples graph. | `KG/<KG>/<rdf_file>` |
| `constraints_folder` | string | Name of the folder holding the SHACL shapes. | `Constraints/<constraints_folder>/` |
| `log_level` | string | Present for compatibility. **Currently ignored**: the script always logs at `INFO`. | - |
| `pca_threshold` | number | Lower bound on PCA confidence for a rule to be used. | Rule filter, see below |

### Derived paths

`initialize()` in `Symbolic_predictions.py` turns the configuration into these paths (relative to
`KG_Normalization/`):

| Purpose | Path |
|---|---|
| Input graph | `KG/<KG>/<rdf_file>` |
| Rules | `KG/<KG>/<rules_file>` |
| SHACL shapes | `Constraints/<constraints_folder>/` |
| Shapes file read by the normalization step | `Constraints/<constraints_folder>/<constraints_folder>.ttl` |
| Predictions per predicate | `Output/<KG>/predictions/<predicate>.tsv` |
| Enriched KG | `Output/<KG>/enriched/<KG>_enriched.nt` |
| Validation results | `Output/<KG>/validation/` |
| Normalized KG | `Output/<KG>/transformed/` |
| Log file | `logs/symbolic_predictions_<timestamp>.log` |

### prefix

The prefix links three things that must agree:

1. The IRIs in the `.nt` file.
2. The bare names in the rules (`father`, `spouse`, ...). The pipeline writes them as `ex:father` with
   `PREFIX ex: <prefix>`.
3. The IRIs written inside the SHACL queries.

If the prefix in `input.json` differs from the namespace in the graph, rule queries match nothing and no
predictions are produced. If the SHACL shapes use a different namespace than the graph, validation finds
nothing.

> The bundled `KG/FrenchRoyalty/french_royalty.nt`, the shape in `Constraints/FrenchRoyalty/FrenchRoyalty.ttl`
> and `input.json` all use `http://FrenchRoyalty.org/`. An earlier `input.json` used the misspelling
> `http://FrenchRoaylty.org/`, which produced 0 predictions.

### pca_threshold

Rules are selected with this condition on the PCA confidence column:

```
pca_threshold < pca_confidence < 1
```

Both bounds are exclusive. Rules with a PCA confidence of exactly `1.0` are **not** used: the script treats
them as rules that predict nothing new. If every rule in your file has confidence `1.0`, no rule is selected
and the pipeline prints `No rules found meeting the PCA confidence threshold criteria.` Mine rules with
confidence below 1, or lower the threshold.

## Validated_KG_Completion/input_KGC.json

Read by `KGC.py` (the file name is fixed in the code as `input_KGC.json`).

| Key | Default | Meaning |
|---|---|---|
| `kg_path` | required | Path to the normalized KG as a **tab-separated** file (subject, predicate, object). |
| `results_path` | required | Output directory for splits, models and plots. |
| `models` | `["TransE","TransH","TransD","ComplEx","RotatE","TuckER"]` | PyKEEN model names to train. |
| `num_epochs` | 100 | Training epochs. |
| `embedding_dim` | 50 | Embedding size. |
| `batch_size` | 1024 | Training batch size. |
| `random_seed` | 1235 | Seed for the split and for training. |
| `create_inverse_triples` | false | Add inverse relations to the triples factory. |
| `filtered_negative_sampling` | true | Filter true triples out of negative samples. |
| `save_splits` | true | Write `train` and `test` files to `results_path`. |
| `log_level` | `INFO` | Python logging level. |

## Validated_KG_Completion/input_KGC_hpo.json

Read by `KGC_hpo.py` (fixed file name `input_KGC_hpo.json`).

| Key | Default | Meaning |
|---|---|---|
| `dataset_path` | required | Path to the KG as a tab-separated file. |
| `output_dir` | required | Output directory. |
| `models` | - | PyKEEN models to optimize. |
| `n_trials` | 30 | Number of hyperparameter trials per model. |
| `train_ratio`, `test_ratio`, `val_ratio` | - | Split proportions. |
| `random_state` | - | Seed. |
| `num_epochs` | - | Training epochs per trial. |
| `log_level` | `INFO` | Python logging level. |

> The part-2 README refers to `input.json`. The scripts actually read `input_KGC.json` and
> `input_KGC_hpo.json`.
