# VANILLA Documentation

VANILLA is a framework for **Validated Knowledge Graph Completion**. It combines symbolic rules, SHACL
constraints and embedding models so that the facts a knowledge graph (KG) gains, and the anomalies it
already contains, are checked against domain knowledge.

This folder documents the whole project: what each part does, how to run it, how to bring your own graph,
and how the code works internally.

## Where to start

| If you want to... | Read |
|---|---|
| Understand what VANILLA does and how the parts fit together | [01 - Overview and architecture](01-overview.md) |
| Set up Python and install dependencies | [02 - Installation](02-installation.md) |
| Know every option in `input.json` | [03 - Configuration reference](03-configuration.md) |
| Prepare a KG, a rules file and SHACL shapes | [04 - Data formats](04-data-formats.md) |
| Understand each stage of the normalization pipeline | [05 - The normalization pipeline](05-normalization-pipeline.md) |
| Write or fix SHACL constraints and understand the constraints folder | [06 - SHACL constraints](06-shacl-constraints.md) |
| Convert a `.tsv` triples file to N-Triples | [07 - tsv_to_nt.py](07-tsv-to-nt.md) |
| Normalize your own graph, start to finish | [08 - Normalizing your own graph](08-normalizing-your-own-graph.md) |
| Train link-prediction models on the normalized KG | [09 - Validated KG completion](09-validated-kg-completion.md) |
| Look up a function or its parameters | [10 - Code reference](10-code-reference.md) |
| Fix an error message | [11 - Troubleshooting](11-troubleshooting.md) |
| See what changed in the code and docs | [CHANGELOG](CHANGELOG.md) |

## Repository map

```
VANILLA/
├── README.md                       Project summary, benchmark statistics
├── LICENSE.txt
├── requirements.txt                Python dependencies
├── docs/                           This documentation
├── images/                         Figures used by the READMEs
├── .data/                          Local, git-ignored working data (your own graphs, rules, ...)
│
├── KG_Normalization/               Part 1: symbolic normalization pipeline
│   ├── input.json                  Configuration of one run
│   ├── Symbolic_predictions.py     Entry point: rules -> predictions -> validation -> normalization
│   ├── Validation.py               SHACL validation with TravSHACL
│   ├── Normalization_transform.py  Rewrites triples that violate constraints
│   ├── tsv_to_nt.py                Utility: TSV triples -> N-Triples
│   ├── KG/<KG>/                    Input graph (.nt) and rules (.csv)
│   ├── Constraints/<name>/         Input SHACL shapes (.ttl only)
│   └── Output/<KG>/                Output: predictions/, enriched/, validation/ and transformed/
│
└── Validated_KG_Completion/        Part 2: link prediction on the normalized KG
    ├── KGC.py, input_KGC.json      Train and evaluate embedding models
    └── KGC_hpo.py, input_KGC_hpo.json   Same, with hyperparameter optimization
```

All commands in this documentation are run from inside `KG_Normalization/` (or
`Validated_KG_Completion/`), because the scripts use relative paths.

## Conventions used in these docs

- **KG name**: the value of `"KG"` in `input.json`. It names the input folder, the output folders and the
  output files.
- **Namespace / prefix**: the IRI prefix that turns a bare name such as `Louis_IX` into
  `http://FrenchRoyalty.org/Louis_IX`. The KG, the rules and the SHACL shapes must all agree on it.
- Paths are relative to the directory the command runs from unless they start with `/`.
