# 07 - tsv_to_nt.py and nt_to_tsv.py

`Normalization/tsv_to_nt.py` converts a file of tab-separated triples into an N-Triples file, which is
the format the normalization pipeline reads.

## Usage

```bash
cd Normalization

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

- No literals and no blank nodes. (`nt_to_tsv.py` reads them, see below, but `tsv_to_nt.py` cannot write them.)
- The whole set of distinct triples is kept in memory for de-duplication, which is fine for graphs of some
  millions of triples but not for much larger ones.

---

# nt_to_tsv.py

`Normalization/nt_to_tsv.py` does the reverse: it converts an N-Triples file into a file of tab-separated
triples (subject, predicate, object, no header). Use it, for example, to turn a normalized `.nt` into the
TSV that Part 2 needs.

## Usage

```bash
cd Normalization

python nt_to_tsv.py <input.nt> <output.tsv> [--prefix <namespace>] [--type-predicate NAME]
```

Example:

```bash
python nt_to_tsv.py Output/FrenchRoyalty/transformed/FrenchRoyalty_normalized.nt \
    ../.data/french_royalty/french_royalty_normalized.tsv \
    --prefix http://FrenchRoyalty.org/
```

| Argument | Required | Default | Meaning |
|---|---|---|---|
| `nt` | yes | - | Input N-Triples file. |
| `tsv` | yes | - | Output file. Missing parent folders are created. |
| `--prefix` | no | empty | Namespace stripped from the start of IRIs. Empty keeps full IRIs. |
| `--type-predicate` | no | `type` | Name written for `rdf:type`. Pass `''` to keep the full IRI. |

## Conversion rules

| Input | Output |
|---|---|
| `<{prefix}Louis_IX>` | `Louis_IX` |
| IRI outside the prefix | Full IRI, without `<>` |
| `<http://www.w3.org/1999/02/22-rdf-syntax-ns#type>` predicate | `--type-predicate` (default `type`) |
| Percent-encoded characters (`%C3%A9`) | Decoded (`é`) |
| Blank node `_:b1` | Kept as `_:b1` |
| Literal `"male"@en` or `"1"^^xsd:integer` | Lexical form only (`male`, `1`); language tag and datatype are dropped. Tabs and newlines become spaces. |
| Comment or blank line | Ignored |
| Line that is not a valid statement | Skipped, with a warning on stderr |
| Duplicate row | Written once |

`nt_to_tsv.py` reverses `tsv_to_nt.py` when both use the same prefix and type predicate. A round trip
through both scripts gives the original file, apart from duplicates and ordering.

## Using it from Python

```python
from nt_to_tsv import convert

written, skipped = convert(
    nt_path="Output/FrenchRoyalty/transformed/FrenchRoyalty_normalized.nt",
    tsv_path="../.data/french_royalty/french_royalty_normalized.tsv",
    prefix="http://FrenchRoyalty.org/",
)
```

`convert` returns `(triples_written, lines_skipped)`.

## Limitations

- Literal language tags and datatypes are lost.
- The normalization step can produce predicates such as `rdf-syntax-ns#type_Person`. These are not the plain
  `rdf:type` IRI, so they are written as ordinary predicates and not mapped to `type`.
- Every distinct row is kept in memory for de-duplication.
