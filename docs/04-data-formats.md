# 04 - Data formats

The normalization pipeline needs three inputs, and each has a strict format.

| Input | Format | Location | Set by |
|---|---|---|---|
| Knowledge graph | N-Triples (`.nt`) | `KG_Normalization/KG/<KG>/<rdf_file>` | `KG`, `rdf_file` |
| Rules | CSV, AMIE-style | `KG_Normalization/Rules/<rules_file>` | `rules_file` |
| Constraints | Turtle (`.ttl`) with SHACL-SPARQL shapes | `KG_Normalization/Constraints/<constraints_folder>/` | `constraints_folder` |

## Knowledge graph: N-Triples

One triple per line, every term an IRI, terminated by ` .`:

```
<http://FrenchRoyalty.org/Robert_II_of_Scotland> <http://FrenchRoyalty.org/father> <http://FrenchRoyalty.org/Walter_Stewart_6th_High_Steward_of_Scotland> .
<http://FrenchRoyalty.org/Robert_II_of_Scotland> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://FrenchRoyalty.org/Person> .
```

Points to know:

- **Every object is an IRI.** The rule queries and the normalization step take the object's local name
  (the part after the last `/`). Literal objects are not supported by the pipeline.
- **Class membership uses `rdf:type`.** SHACL shapes typically use `sh:targetClass ex:Person`, which selects
  nodes with `rdf:type ex:Person`. A bare `type` predicate in a TSV must therefore be mapped to
  `rdf:type` when converting (the `tsv_to_nt.py` script does this by default).
- The graph is loaded line by line by `load_graph`, so a malformed line is reported as
  `Error parsing line N` and skipped instead of aborting the run.
- Local names should avoid spaces and the characters `< > " { } | \ ^` and the backtick, which are not
  legal in IRIs.

To create the `.nt` file from a TSV, see [07 - tsv_to_nt.py](07-tsv-to-nt.md).

### Source TSV format

The source triples file that `tsv_to_nt.py` reads has three tab-separated columns, no header:

```
Giovanni_il_Popolano	father	Pierfrancesco_the_Elder
Luitgarde_of_Vermandois	spouse	Theobald_I_Count_of_Blois
Leopold_Duke_of_Lorraine	type	Person
```

## Rules: AMIE-style CSV

One rule per row. The column names below are required *exactly as written*, in lowercase:

| Column | Required | Meaning |
|---|---|---|
| `body` | yes | Rule body: one or more atoms, e.g. `?b  parent  ?a` |
| `head` | yes | Rule head: one atom, e.g. `?a  successor  ?b` |
| `pca_confidence` | yes | PCA confidence. |
| `std_confidence` | yes | Standard confidence. |
| `functional_variable` | yes | Which head variable is functional: `?a` or `?b`. |
| `rule`, `head_coverage`, `positive_examples`, `body_size`, `pca_body_size` | no | Kept for reference. |

Example:

```csv
body,head,head_coverage,std_confidence,pca_confidence,positive_examples,body_size,pca_body_size,functional_variable
?b  parent  ?a   ,?a  successor  ?b,0.31920904,0.119450317,0.478813559,113,946,236,?a
```

### Atoms

An atom is `subject predicate object` separated by whitespace. Variables start with `?`. Predicates are bare
names (`father`), not IRIs; the pipeline adds the `ex:` prefix. A body with several atoms lists them one
after another, and the code splits the text on whitespace into groups of three:

```
?b predecessor ?a  ?b spouse ?a
```

is the body `?b predecessor ?a . ?b spouse ?a`.

### Rules with constants

If the object of any atom is not a variable (for example `?a type Person`), the pipeline treats the file as
a *constant* rule set and uses a different query builder (see
[05](05-normalization-pipeline.md#13-rule-types)). The type is detected from a random sample of up to 10 rules.
Do not mix rules with and without constants in the same file.

### Column names from other tools

Only the lowercase names above are accepted; there are no fallbacks. A file with any other spelling
(`Body`, `PCA_Confidence`, `Standard_Confidence`, `Support`, `Body Size`, ...) stops the run with:

```
ValueError: Missing required column(s) in rules file: body, head, pca_confidence, ...
Column names must be lowercase, found: [...]
```

All rule files bundled in `KG_Normalization/Rules/` use the lowercase names. To convert a file from another
tool, rename its columns, for example:

```python
import pandas as pd

df = pd.read_csv("mined_rules.csv")
df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
df = df.rename(columns={
    "standard_confidence": "std_confidence",
    "support": "positive_examples",
})
df.to_csv("KG_Normalization/Rules/my_rules.csv", index=False)
```

Check the result: `body`, `head`, `pca_confidence`, `std_confidence` and `functional_variable` must be present.

## Constraints: SHACL shapes

Constraints are Turtle files containing SHACL-SPARQL shapes. They have their own page:
[06 - SHACL constraints](06-shacl-constraints.md), which also explains the folder layout and why the folder
must contain nothing except shape files.

## Output formats

| Output | Format |
|---|---|
| `Output/<KG>/predictions/<predicate>.tsv` | Tab-separated `subject predicate object`, bare names (prefix removed), no header. One file per head predicate that produced predictions. |
| `Output/<KG>/enriched/<KG>_enriched.nt` | N-Triples: the input graph plus all predictions. |
| `Output/<KG>/validation/validationReport.ttl` | SHACL validation report (Turtle). |
| `Output/<KG>/validation/stats.txt` | Number of valid and invalid targets, query counts and timings. |
| `Output/<KG>/validation/targets_valid.log`, `targets_violated.log` | Lists of valid and violating target nodes. |
| `Output/<KG>/validation/traces.csv`, `validation.log` | Execution trace and log. |
| `Output/<KG>/transformed/<KG>_expanded.nt` | Enriched KG after predicate-object expansion. |
| `Output/<KG>/transformed/<KG>_normalized.nt` | The final normalized KG. |
| `logs/symbolic_predictions_<timestamp>.log` | Run log. |

Part 2 (`KGC.py`) reads **TSV**, not N-Triples, so the normalized `.nt` has to be converted to a
tab-separated file before it is used there. The repository does not ship an `.nt` to TSV converter; some
benchmarks already include a `.tsv` version next to the `.nt`.
