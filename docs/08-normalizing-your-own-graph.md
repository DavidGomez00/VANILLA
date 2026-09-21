# 08 - Normalizing your own graph

This is a start-to-finish walkthrough for a graph that exists as a `.tsv` file of triples. It uses the
French Royalty variant kept at `.data/french_royalty/french_royalty.tsv` as the running example; replace the
names with your own.

## What you need before you start

| # | Item | Where it ends up |
|---|---|---|
| 1 | Triples as a TSV | `.data/<name>/<name>.tsv` (any location works) |
| 2 | The same triples as N-Triples | `KG_Normalization/KG/<KG>/<name>.nt` |
| 3 | Rules with PCA confidence between the threshold and 1 | `KG_Normalization/Rules/<rules>.csv` |
| 4 | SHACL shapes for the relations of your graph | `KG_Normalization/Constraints/<constraints>/<constraints>.ttl` |
| 5 | A matching `input.json` | `KG_Normalization/input.json` |

## Step 1 - Look at the graph

Count the relations, because rules and shapes only make sense for relations that exist:

```bash
cut -f2 .data/french_royalty/french_royalty.tsv | sort | uniq -c
```

For the French Royalty variant this shows `child` (1,897), `father` (658), `mother` (534), `parent` (1,239),
`predecessor` (471), `spouse` (1,152), `successor` (471) and `type` (2,211).

Decide the namespace now, for example `http://FrenchRoyalty.org/`. Everything else must use it.

## Step 2 - Convert the TSV to N-Triples

```bash
cd KG_Normalization
python tsv_to_nt.py ../.data/french_royalty/french_royalty.tsv \
    KG/FrenchRoyaltyTSV/french_royalty.nt --prefix http://FrenchRoyalty.org/
```

See [07](07-tsv-to-nt.md).

## Step 3 - Get suitable rules

The rules file must:

- have the column names listed in [04](04-data-formats.md#rules-amie-style-csv), and
- contain rules with `pca_confidence` **greater than `pca_threshold` and strictly less than 1**, because
  rules at exactly 1.0 are filtered out.

Rules mined with AMIE come as a table with body, head, head coverage, standard confidence, PCA confidence,
positive examples, body size, PCA body size and functional variable. Two situations are common:

1. **Your mining tool wrote other headers** (`Body`, `PCA_Confidence`, `Support`, ...): rename them to the
   lowercase names, see the snippet in [04](04-data-formats.md#column-names-from-other-tools).
2. **Every rule has PCA confidence `1.0`**: the pipeline will select zero rules and predict nothing. Mine
   again with a lower confidence cut-off so that partially reliable rules are included, or accept that the
   run only performs validation and normalization. To check how many rules will be used:

```python
import pandas as pd
r = pd.read_csv("Rules/my_rules.csv")
t = 0.75
print(((r["pca_confidence"] > t) & (r["pca_confidence"] < 1)).sum(), "rules will be used")
```

Rules mined on a different variant of the graph (for example the benchmark, which has `hasSpouse`,
`gender`, `name`) will run, but rules about relations your graph lacks can only produce empty results.

## Step 4 - Write the SHACL shapes

Create a **new** folder, so no old `result_*` directory or other `.ttl` file is in it:

```
KG_Normalization/Constraints/FrenchRoyaltyTSV/FrenchRoyaltyTSV.ttl
```

The file name must equal the folder name. Write one shape per anomaly, using the namespace of your graph and
`FILTER EXISTS` for conditions that should trigger a rewrite. Authoring guidance and examples are in
[06](06-shacl-constraints.md#writing-constraints-for-your-own-graph).

A quick way to start is to copy the bundled shape:

```bash
mkdir -p Constraints/FrenchRoyaltyTSV
cp Constraints/FrenchRoyalty/FrenchRoyalty.ttl Constraints/FrenchRoyaltyTSV/FrenchRoyaltyTSV.ttl
```

The bundled shape uses `http://FrenchRoyalty.org/`, so it matches a graph converted with that prefix.

## Step 5 - Configure the run

Edit `KG_Normalization/input.json`:

```json
{
  "KG": "FrenchRoyaltyTSV",
  "prefix": "http://FrenchRoyalty.org/",
  "rules_file": "my_rules.csv",
  "rdf_file": "french_royalty.nt",
  "constraints_folder": "FrenchRoyaltyTSV",
  "log_level": "INFO",
  "pca_threshold": 0.75
}
```

Checklist:

- `KG/FrenchRoyaltyTSV/french_royalty.nt` exists.
- `Rules/my_rules.csv` exists and has the required columns.
- `Constraints/FrenchRoyaltyTSV/FrenchRoyaltyTSV.ttl` exists.
- `prefix` equals the namespace in the `.nt` and in the shapes.

## Step 6 - Run

```bash
cd KG_Normalization
python Symbolic_predictions.py
```

Watch the console for:

| Message | What to check |
|---|---|
| `Detected rule type: variable` | Matches your rules (variable or constant). |
| `Total number of rules utilized: N` | If `0`, see step 3. |
| `<predicate>: R rules, P predictions` | Which relations gained triples. |
| `Constraint Validation Result saved to Validation_results/<KG>` | Validation ran. |
| `Found N violations` | Number of violation entries in the report. |
| `Applying M transformations...` | Triples that were renamed. |

## Step 7 - Inspect the results

```bash
# What changed between the expanded and the normalized graph
sort Transformed_FrenchRoyaltyTSV/InitialTransformedKG_FrenchRoyaltyTSV.nt > /tmp/a
sort Transformed_FrenchRoyaltyTSV/TransformedKG_FrenchRoyaltyTSV.nt         > /tmp/b
diff /tmp/a /tmp/b | head

# How many targets were valid / invalid
cat Validation_results/FrenchRoyaltyTSV/stats.txt
```

Interpretation:

- `Predictions/<KG>_predictions/*.tsv` lists the new triples that came from rules.
- `stats.txt` gives the numbers of valid and invalid targets.
- In the diff, lines with `No<Entity>` are the triples that were marked as anomalous.
- If the diff is empty and violations were found, your shapes probably use `FILTER NOT EXISTS`, which
  validates but does not rewrite (see [06](06-shacl-constraints.md#what-gets-rewritten)).

## Worked example: what a run on the French Royalty variant produced

A run of the pipeline on the 8,633-triple variant, with the benchmark's rules (85 rules above the
threshold) and the bundled shape, gave:

| Metric | Value |
|---|---|
| Rules used | 85 |
| Predicted triples | 1,067 |
| Total triples after enrichment | 9,221 |
| Targets (nodes of type Person) | 2,211 |
| Valid / invalid targets | 1,931 / 280 |
| Violations processed | 280 |
| Final triples | 9,221 (unchanged; triples renamed, not added or removed) |

Predictions went to `parent`, `father`, `child`, `mother` and `spouse`. No predictions were made for
`successor`, `predecessor`, `hasSpouse` or `gender`. The graph already contains the `successor`/`predecessor`
inverses in full, and `hasSpouse`/`gender` do not exist in this variant.

That run used rules mined on the benchmark version of the graph, not on this variant. Results with rules
mined on your own graph will differ.

## Benchmark graph vs. simplified variant

| | Benchmark (`KG/FrenchRoyalty`) | Simplified variant |
|---|---|---|
| Triples | 10,652 | 8,633 |
| Entities | 2,656 | 2,212 |
| Relations | 12 | 8 |
| Extra relations | `hasSpouse`, `gender`, `name`, `marriedTo` | none |
| Triples in common | 7,211 | 7,211 |
| `successor` with matching `predecessor` | 268 / 354 | 471 / 471 |
| `spouse` mirrored | 662 / 865 | 1,150 / 1,152 |

The simplified variant is already more complete, so fewer triples are left for rules to predict.
