# 06 - SHACL constraints

SHACL constraints tell VANILLA which nodes of the graph break a domain rule. This page explains the layout
of the constraints folder, what a shape file contains, how to write your own, and how the normalization
step interprets a shape.

## Folder layout

```
KG_Normalization/
├── Constraints/
│   └── <constraints_folder>/               ← value of "constraints_folder" in input.json
│       └── <constraints_folder>.ttl        ← the shapes: the only file you write
└── Output/
    └── <KG>/                               ← value of "KG"; created by the run
        ├── validation/
        │   ├── validationReport.ttl
        │   ├── stats.txt
        │   ├── targets_valid.log
        │   ├── targets_violated.log
        │   ├── traces.csv
        │   └── validation.log
        └── transformed/                    ← the normalized KGs
```

Rules for the constraints folder:

1. **It contains shape files only.** TravSHACL loads *every* `.ttl` file found under it.
2. **The shapes the normalization step reads must be in `<constraints_folder>.ttl`**, named after the
   folder. Other `.ttl` files in the folder are still validated, but only this one is used to work out how
   to rewrite triples.
3. **Nothing is written into it.** Validation results go to `Output/<KG>/validation/`.

### Why results are kept outside the constraints folder

Earlier versions of the code wrote the results to `Constraints/<name>/result_<KG>/`. That folder contains a
`validationReport.ttl`, and TravSHACL parsed it as if it were a shape file on the next run, failing with a
syntax error such as:

```
Bad syntax (Prefix ":" not bound) ... "b'@prefix sh: <http://www.w3.org/ns/shacl#> ..."
```

Separating inputs from outputs removes this whole class of failure: a run can be repeated any number of
times against the same constraints folder. The benchmark folders committed in the repository still contain
old `result_*` subfolders from earlier runs. If you want to use one of those constraint folders directly,
delete or move its `result_*` subfolder first, or copy the `.ttl` shape file into a fresh folder.

## What a shape file contains

Here is the shape shipped for French Royalty, annotated:

```turtle
@prefix ex:  <http://FrenchRoyalty.org/> .          # namespace of the KG
@prefix exS: <http://FrenchRoyalty.org/shapes/> .   # namespace for shape names
@prefix sh:  <http://www.w3.org/ns/shacl#> .

exS:FatherWithChildConstraint a sh:NodeShape ;      # shape name and type
    sh:sparql [ sh:select """
     SELECT ($this AS ?this)                        # returns the violating node
            WHERE {
                $this <http://FrenchRoyalty.org/child> ?child .
                ?child <http://FrenchRoyalty.org/mother> ?mother .
                FILTER EXISTS {
                    $this <http://FrenchRoyalty.org/spouse> ?mother .
                }
            }
""" ] ;
    sh:targetClass ex:Person .                      # nodes to check
```

| Part | Purpose |
|---|---|
| `@prefix ex:` | Must equal the KG namespace, so `ex:Person` is the class used in the graph. |
| `exS:...` | The shape's identifier. Each shape needs its own. It appears in the validation report as `sh:sourceShape`. |
| `a sh:NodeShape` | Required. The normalization step only considers `sh:NodeShape` subjects. |
| `sh:sparql [ sh:select "..." ]` | The constraint, as a SPARQL query. **Rows returned are violations.** |
| `sh:targetClass ex:Person` | Which nodes are checked. Every node with `rdf:type ex:Person` is a *target*. |

Inside `sh:select`:

- `$this` is the target node being checked.
- The query must return `$this` as `?this` (`SELECT ($this AS ?this)`).
- Predicate IRIs are written in full, in angle brackets. Prefixes are not declared inside the query.

Reading the example above: a person `$this` is a violation if they have a child whose mother is also their
spouse.

The number of targets is what `stats.txt` reports as `all targets`. For the French Royalty variant with
2,211 `type Person` triples this was 2,211.

## How normalization reads a shape

`extract_triple_patterns` in `Normalization_transform.py` does not execute the query. It reads the query
*text* with regular expressions, so a shape has to follow a restricted form.

1. The first `FILTER EXISTS { ... }` or `FILTER NOT EXISTS { ... }` block is located. Everything before it
   is the *main part*; the content of the block is the *filter part*. Only the **first** block is used.
2. In both parts it looks for two kinds of pattern:
   - Direct: `$this <predicate> <object>` or `$this <predicate> ?variable`
   - Indirect: `?x <predicate> ?y`
3. Main-part patterns become *condition patterns*. Filter-part patterns become *filter patterns*, flagged as
   `NOT EXISTS` if the block used it.

The regular expression for the block is `FILTER (?:NOT )?EXISTS \{([^}]+)\}`, so the content of the block
cannot contain a closing brace. Patterns must use full `<...>` IRIs.

Consequences for shape authors:

| Do | Avoid |
|---|---|
| One `FILTER EXISTS` block | Several filter blocks (only the first is read) |
| Full IRIs in angle brackets | Prefixed names such as `ex:child` inside the query |
| Plain triple patterns | `UNION`, `OPTIONAL`, property paths, sub-selects (they validate, but are not analysed for rewriting) |
| `FILTER EXISTS` when you want triples rewritten | `FILTER NOT EXISTS` when you want triples rewritten (see below) |

### What gets rewritten

For every violating node, all its triples whose predicate matches a **filter pattern** are renamed:

- `FILTER EXISTS { $this <p> ?x }` renames the node's `p` triples to `p_No<Entity>` with object
  `No<Entity>`.
- `FILTER NOT EXISTS { ... }` renames them to themselves, so **nothing changes**. Such a shape still
  produces violations and appears in the counts, but does not affect the normalized graph.

See [05](05-normalization-pipeline.md#33-rewrite-the-violating-nodes) for a worked example.

A violating node is only rewritten if it also satisfies the *condition patterns* in the expanded graph
(after predicate-object expansion).

## Writing constraints for your own graph

1. Decide what an anomaly looks like, e.g. "a person whose child is also their spouse".
2. Write the anomaly as a query that returns `$this`. Put the relations that identify the situation in the
   main part, and the conflicting relation in a `FILTER EXISTS` block.
3. Put the shape in `Constraints/<name>/<name>.ttl`, and set `constraints_folder` to `<name>`.
4. Check the namespace: every IRI in the shape must use the same namespace as the KG.

Example anomaly shapes for a graph with `child`, `parent`, `spouse`, `father`, `mother`:

```turtle
exS:ChildIsSpouse a sh:NodeShape ;
    sh:sparql [ sh:select """
     SELECT ($this AS ?this)
            WHERE {
                $this <http://FrenchRoyalty.org/child> ?c .
                FILTER EXISTS { $this <http://FrenchRoyalty.org/spouse> ?c . }
            }
""" ] ;
    sh:targetClass ex:Person .

exS:FatherIsMother a sh:NodeShape ;
    sh:sparql [ sh:select """
     SELECT ($this AS ?this)
            WHERE {
                $this <http://FrenchRoyalty.org/father> ?p .
                FILTER EXISTS { $this <http://FrenchRoyalty.org/mother> ?p . }
            }
""" ] ;
    sh:targetClass ex:Person .
```

These two shapes are examples of the pattern, not tested constraints that ship with the repository. Test any
new shape on a small graph first, and compare `<KG>_expanded.nt` with
`<KG>_normalized.nt` to see exactly what was rewritten.

Several shapes can be placed in one file. The bundled shapes contain a single shape each, so multi-shape
files are supported by the parser code but were not exercised by the repository's own runs.

## Bundled constraints

`Constraints/<Benchmark>/<Benchmark>.ttl` is provided for DB100K, FrenchRoyalty, SGKG, SynthLC-1000,
SynthLC-10000 and YAGO3-10, along with `result_<Benchmark>/` folders containing results of earlier runs
(`stats.txt`, logs, `validationReport.ttl`). Those result folders were produced before results moved to
`Output/<KG>/validation/` and are kept only as reference.
