# 07 - tsv_to_nt.py

`KG_Normalization/tsv_to_nt.py` converts a file of tab-separated triples into an N-Triples file, which is
the format the normalization pipeline reads.

## Usage

```bash
cd KG_Normalization

python tsv_to_nt.py <input.tsv> <output.nt> --prefix <namespace> [--type-predicate NAME]
```

Example, using the French Royalty TSV stored in the local `.data` folder:

```bash
python tsv_to_nt.py ../.data/french_royalty/french_royalty.tsv \
    KG/FrenchRoyaltyTSV/french_royalty.nt \
    --prefix http://FrenchRoyalty.org/
```

Output:

```
Wrote 8633 triples to KG/FrenchRoyaltyTSV/french_royalty.nt (0 lines skipped)
```

## Arguments

| Argument | Required | Default | Meaning |
|---|---|---|---|
| `tsv` | yes | - | Input file. Three tab-separated columns: subject, predicate, object. No header. |
| `nt` | yes | - | Output file. Missing parent folders are created. |
| `--prefix` | yes | - | Namespace prepended to every bare name. Use the namespace of your SHACL shapes. |
| `--type-predicate` | no | `type` | Predicate name that is mapped to `rdf:type`. Pass `''` to disable. |

## Conversion rules

| Input | Output |
|---|---|
| Bare name `Louis_IX` | `<{prefix}Louis_IX>` |
| Term starting with `http://` or `https://` | Kept as it is: `<http://...>` |
| Predicate equal to `--type-predicate` | `<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>` |
| Any character other than letters, digits and `_ - . ~ : ( )` (spaces, quotes, commas, apostrophes, `/`, accented letters, ...) | Percent-encoded as UTF-8, e.g. `é` becomes `%C3%A9`. |
| Line without exactly 3 non-empty fields | Skipped, with a warning on stderr |
| Blank line | Ignored |
| Duplicate triple | Written once |

The subject and the object are always converted to IRIs. There is no literal support: an object such as
`male` becomes `<{prefix}male>`, not `"male"`.

## Using it from Python

```python
from tsv_to_nt import convert

written, skipped = convert(
    tsv_path="../.data/french_royalty/french_royalty.tsv",
    nt_path="KG/FrenchRoyaltyTSV/french_royalty.nt",
    prefix="http://FrenchRoyalty.org/",
    type_predicate="type",
)
```

`convert` returns `(triples_written, lines_skipped)`. Duplicates count as skipped.

## Checking the result

The output should parse without errors:

```python
from rdflib import Graph
g = Graph().parse("KG/FrenchRoyaltyTSV/french_royalty.nt", format="nt")
print(len(g))
```

For the French Royalty variant, the count matches the number of lines of the TSV (8,633), and the 2,211
`type` triples appear as `rdf:type`.

## Limitations

- Only forward conversion (TSV to N-Triples). Part 2 needs a TSV, so the normalized `.nt` has to be turned
  back into a TSV by another means.
- No literals and no blank nodes.
- The whole set of distinct triples is kept in memory for de-duplication, which is fine for graphs of some
  millions of triples but not for much larger ones.
