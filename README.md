[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# VANILLA: Validated Knowledge Graph Completion- A Normalization-based Framework for Integrity, Link Prediction, and Logical Accuracy

![VANILLA](https://raw.githubusercontent.com/SDM-TIB/VANILLA/main/images/GraphicalAbstractVANILLA.png "VANILLA")
## 🔍 Overview

VANILLA is a comprehensive framework designed to enhance **Knowledge Graph Completion (KGC)** by validating inferred facts using **logical constraints** derived from domain knowledge and normalizing the exisiting anomalies in KGs. Unlike traditional methods that rely solely on vector embeddings, VANILLA integrates **symbolic reasoning** with numerical learning to ensure logical **validity**, **integrity**, and **accuracy** of predictions. The framework uses **SHACL constraints** to validate predictions and supports **symbolic rule mining**, **constraint checking**, and **KGC evaluation** with state-of-the-art embedding models.
## 📚 Documentation

Full documentation (installation, configuration, data formats, pipeline internals, SHACL constraints, running on your own graph, troubleshooting) is in [docs/](docs/README.md).

## 📁 Repository Structure

```
.
├── KG_Normalization/
│   ├── KG/<KG>/                    # Benchmark knowledge graph (.nt) and its symbolic rules (.csv)
│   ├── Constraints/<KG>/           # SHACL constraints
│   ├── Output/<KG>/                # Output: predictions, enriched, validation, transformed
│   ├── input.json                  # Configuration of a run
│   ├── Symbolic_predictions.py     # Entry point
│   ├── Normalization_transform.py
│   ├── Validation.py
│   ├── tsv_to_nt.py
│   └── nt_to_tsv.py
├── Validated_KG_Completion/
│   ├── input_KGC.json
│   ├── KGC.py
│   ├── input_KGC_hpo.json
│   └── KGC_hpo.py
├── docs/
├── LICENSE.txt
└── requirements.txt
```
---
## 📊 Benchmark Statistics

| **KG Size** | **Benchmark**     | **#Triples** | **#Entities** | **#Relations** |
|-------------|-------------------|--------------|----------------|----------------|
| **Large**   | DB100K            | 695,572      | 99,604         | 470            |
|             | SynthLC-10000     | 106,549      | 10,000         | 9              |
| **Medium**  | YAGO3-10          | 1,080,264    | 123,086        | 37             |
|             | SGKG              | 54,585       | 36,450         | 6              |
| **Small**   | French Royalty    | 10,526       | 2,601          | 12             |
|             | SynthLC-1000      | 10,668       | 1,000          | 9              |

| **KG Size** | **Benchmark**     | **#Constraints** | **#Valid** | **#Invalid** |
|-------------|-------------------|------------------|------------|--------------|
| **Large**   | DB100K            | 6                | 390,351    | 62,024       |
|             | SynthLC-10000     | 25               | 223,523    | 26,477       |
| **Medium**  | YAGO3-10          | 4                | 393,205    | 58,719       |
|             | SGKG              | 5                | 156,965    | 12,150       |
| **Small**   | French Royalty    | 2                | 1,922      | 298          |
|             | SynthLC-1000      | 25               | 22,335     | 2,665        |

> The French Royalty rows describe the original benchmark graph. `KG_Normalization/KG/FrenchRoyalty/` now bundles a simplified variant (8,633 triples, 8 relations); see [docs/01-overview.md](docs/01-overview.md).

---
## ⚙️ Setup Instructions

1. **Clone the repository**
   ```bash
   git clone git@github.com:SDM-TIB/VANILLA.git
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **KG_Normalization**

Navigate to `KG_Normalization` folder and follow the steps in README of that folder

4. **Validated_KG_Completion**

Navigate to `Validated_KG_Completion` folder and follow the steps in README of that folder

## 📈 Evaluation Metrics

We evaluate KG completion using embedding models:
- **TransE**, **TransH**, **TransD**
- **RotatE**, **ComplEx**, **TuckER**
- **CompGCN**

Metrics reported:
- Hits@1, Hits@3, Hits@5, Hits@10
- Mean Reciprocal Rank (MRR)

---

## 🧠 Graphical Summary

The VANILLA framework integrates **symbolic rules**, **domain constraints**, and **neural embeddings** for high-quality knowledge graph completion. It identifies valid and invalid triples using evolving logical constraints and employs numerical models to infer missing links, ensuring semantic consistency and logical soundness in the normalized KG.

---

## 📄 License

This project is licensed under the terms of the [LICENSE.txt](LICENSE.txt).

## Authors
VANILLA has been developed by members of the Scientific Data Management Group at TIB, as an ongoing research effort.
The development is co-ordinated and supervised by Maria-Esther Vidal.
We strongly encourage you to report any issues you have with VANILLA.
Please, use the GitHub issue tracker to do so.
VANILLA has been implemented in joint work by Disha Purohit, and Yashrajsinh Chudasama.
