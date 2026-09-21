# 10 - Code reference

Reference for the functions of part 1. Paths are relative to `Normalization/`. Signatures reflect the
current code, including the changes listed in the [CHANGELOG](CHANGELOG.md).

## Symbolic_predictions.py

Entry point of the pipeline.

### `load_graph(file) -> Graph`

Reads an N-Triples file line by line into an `rdflib.Graph`. A line that fails to parse is reported
(`Error parsing line N: ...`) and skipped.

### `detect_rule_type(rules_df) -> 'constant' | 'variable'`

Samples up to 10 rules. Returns `'constant'` if any body atom's object, or the head's object, does not start
with `?`; otherwise `'variable'`.

### `rdflib_query_without_constants(rule_df, prefix_query, rdf_data, head_val, predictions_folder) -> DataFrame`

For each rule builds and runs a SPARQL query returning the subject and object bindings of the head atom that
are not yet in the graph. Returns a DataFrame with columns `subject`, `predicate`, `object` (names without
the namespace). Returns an empty DataFrame with those columns when nothing is found.

| Parameter | Meaning |
|---|---|
| `rule_df` | Rules for one head predicate (columns `functional_variable`, `body`, `head`, ...) |
| `prefix_query` | Namespace used for `PREFIX ex:` |
| `rdf_data` | Path to the `.nt` graph (re-read for each rule) |
| `head_val` | Head predicate name, written into the `predicate` column |
| `predictions_folder` | Accepted for symmetry; not used by this function |

### `rdflib_query_with_constants(...) -> DataFrame`

Same signature and output. Used when the head's object is a constant. Only the subject is selected, and
the object column is the constant from the rule head.

### `process_rules(file, prefix, rdf_data, predictions_folder, kg, pca_threshold) -> (DataFrame, Graph)`

Runs stage 1. Filters rules, runs the queries per head predicate, writes
`<predictions_folder>/<predicate>.tsv` files, builds the enriched graph and writes it to
`Output/<kg>/enriched/<kg>_enriched.nt`. Returns the predictions and the enriched graph.
Raises `ValueError` if any required lowercase column (`body`, `head`, `pca_confidence`, `std_confidence`,
`functional_variable`) is missing.

### `initialize(input_config) -> tuple`

Reads the JSON configuration and returns, in this order:

| # | Name | Value |
|---|---|---|
| 1 | `prefix` | `input["prefix"]` |
| 2 | `rules` | `KG/<KG>/<rules_file>` |
| 3 | `rdf` | `KG/<KG>/<rdf_file>` |
| 4 | `path` | `KG/<KG>` |
| 5 | `predictions_folder` | `Output/<KG>/predictions` |
| 6 | `constraints` | `Constraints/<constraints_folder>` |
| 7 | `validation_folder` | `Output/<KG>/validation` (**added**) |
| 8 | `transformed_folder` | `Output/<KG>/transformed` (**added**) |
| 9 | `kg` | `input["KG"]` |
| 10 | `pca_threshold` | `input["pca_threshold"]` |

### Main block

Sets up logging, calls `initialize`, `process_rules`, `travshacl` and `transform`. The shapes file passed to
`transform` is `<constraints>/<basename of constraints>.ttl`.

## Validation.py

### `travshacl(enrichedKG, constraints, output_dir)`

Validates the enriched graph against the SHACL shapes with TravSHACL.

| Parameter | Meaning |
|---|---|
| `enrichedKG` | The enriched `rdflib.Graph`, used as the SPARQL endpoint |
| `constraints` | Folder with the SHACL shape files. Every `.ttl` under it is parsed. |
| `output_dir` | Folder for the results. Created if missing. Must not be inside `constraints`. |

Returns the result of `ShapeSchema.validate()`. Signature change: the third parameter used to be `kg`, with
the output at `<constraints>/result_<kg>`.

## Normalization_transform.py

### `class TriplePattern(predicate, object_value, in_filter=False, is_not_exists=False)`

A predicate/object pattern extracted from a SHACL query. `object_value` is `None` for variables.
`in_filter` marks patterns from inside the `FILTER [NOT] EXISTS` block; `is_not_exists` marks `NOT EXISTS`.

### `extract_triple_patterns(query_text) -> List[TriplePattern]`

Regex-based extraction of `$this <p> <o|?v>` and `?x <p> ?y` patterns from the main part and from the first
filter block. See [06](06-shacl-constraints.md#how-normalization-reads-a-shape).

### `process_shacl_shapes(shacl_file) -> Dict[str, List[TriplePattern]]`

Parses the Turtle file and, for each `sh:NodeShape` with an `sh:sparql`/`sh:select`, returns the patterns
keyed by the shape's IRI. Shapes without extractable patterns are omitted.

### `process_validation_report(report_file) -> List[Tuple[str, str]]`

Prepends common prefixes to the report text, parses it, and returns `(focus node, source shape)` for each
`sh:ValidationResult`.

### `check_pattern_match(graph, subject, pattern) -> bool`

True if `subject` has a triple with the pattern's predicate (and object, when given). The result is
negated if the pattern is a `NOT EXISTS` pattern.

### `transform_predicate_with_object(enriched_kg) -> (Graph, Dict[str, str])`

Replaces every triple's predicate `p` with `p_<local name of the object>`. Returns the new graph and a
mapping from new predicates to the original ones.

### `transform_triple(triple, patterns, predicate_mapping) -> Optional[Tuple]`

For a triple whose original predicate matches a filter pattern (and whose object matches, if the pattern
names one), returns the rewritten triple: a `No` prefix on the object's name for `FILTER EXISTS` patterns,
an empty prefix (no change) for `FILTER NOT EXISTS`. Returns `None` if no pattern matches.

### `transform(enriched_kg, kg_name=None, shapes_file=None, validation_dir=None) -> Graph`

Runs stage 3.

| Parameter | Default | Meaning |
|---|---|---|
| `enriched_kg` | - | Enriched graph |
| `kg_name` | current directory name | Names the outputs |
| `shapes_file` | `Constraints/<kg_name>/<kg_name>.ttl` | Shapes to analyse (**added**) |
| `validation_dir` | `Output/<kg_name>/validation` | Folder containing `validationReport.ttl` (**added**) |
| `output_dir` | `Output/<kg_name>/transformed` | Folder receiving the transformed KGs (**added**) |

Writes `<output_dir>/<kg_name>_expanded.nt` (after predicate-object expansion) and
`<output_dir>/<kg_name>_normalized.nt` (final graph). The three added parameters replace hard-coded paths
(`Constraints/<kg_name>/...` for the shapes, which ignored `constraints_folder`, and the validation and output
folders).

## tsv_to_nt.py

### `to_iri(term, prefix) -> str`

Returns `<term>` if it already starts with `http://` or `https://`, otherwise `<prefix + percent-encoded term>`.

### `convert(tsv_path, nt_path, prefix, type_predicate="type") -> (int, int)`

Converts a TSV file to N-Triples. Returns `(written, skipped)`. See [07](07-tsv-to-nt.md).

## nt_to_tsv.py

### `from_term(term, prefix) -> str`

Turns one N-Triples term into a bare TSV value: strips `prefix` from IRIs and percent-decodes them, keeps
blank nodes, and reduces literals to their lexical form.

### `convert(nt_path, tsv_path, prefix="", type_predicate="type") -> (int, int)`

Converts an N-Triples file to TSV. Returns `(written, skipped)`. See [07](07-tsv-to-nt.md).
