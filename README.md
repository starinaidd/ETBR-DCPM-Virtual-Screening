# ETBR-PermMol Virtual Screening

Repository for the study:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

This project combines the molecular representation model **PermMol**, machine-learning classifiers, e-pharmacophore screening, molecular docking, and experimental validation for the discovery of novel endothelin B receptor (ETBR) antagonists.

---

## Highlights

- PermMol was evaluated on **7 MoleculeNet datasets** and **17 MUV virtual-screening tasks**.
- A curated ETBR dataset containing **721 active** and **1082 inactive** compounds was constructed from ChEMBL and BindingDB.
- Six molecular representations were evaluated with RF and DNN classifiers.
- The **PermMol + DNN** model achieved a test AUC of approximately **0.988** for ETBR activity prediction.
- More than **16 million** commercially available compounds were screened through a multistage virtual-screening strategy.
- Experimental validation identified **five active compounds**: C1, C2, C7, C8, and C9.

---

## ETBR dataset

ETBR activity data were collected from **ChEMBL** and **BindingDB** using IC50 as the activity endpoint.

| Class | Compounds |
|---|---:|
| Active | 721 |
| Inactive | 1082 |
| Total | 1803 |

Activity labels were defined as:

```text
IC50 < 1000 nM      active
IC50 > 10000 nM     inactive
1000–10000 nM       excluded
```

The final dataset was split into:

```text
Training set: 1623 compounds
Test set:      180 compounds
```

---

## Molecular representations and prediction models

The following molecular representations were evaluated:

- PermMol
- ECFP4
- MACCS
- PubChem
- RDKFingerprint
- Atom Pairs

Random forest (**RF**) and deep neural network (**DNN**) classifiers were used for ETBR activity prediction.

PermMol produces a **1536-dimensional molecular representation** for downstream modeling.

The principal model used for large-scale ETBR screening was:

```text
PermMol + DNN
```

For the ETBR test set, the PermMol + DNN model achieved approximately:

| Metric | Value |
|---|---:|
| AUC | 0.988 |
| Sensitivity | 0.889 |
| Specificity | 0.963 |
| Accuracy | 0.933 |
| MCC | 0.861 |

---

## Benchmark datasets

### MoleculeNet

Seven MoleculeNet datasets were used for molecular-property prediction benchmarks:

- BACE
- BBBP
- HIV
- ClinTox
- SIDER
- Tox21
- ToxCast

### MUV

Seventeen MUV tasks were used to evaluate molecular representations under highly imbalanced virtual-screening conditions.

---

## Virtual screening

The screening library contained more than **16 million commercially available compounds** from ChemDiv, Specs, and TopScience.

The successive screening stages retained:

| Stage | Number of compounds |
|---|---:|
| Initial commercial library | >16 million |
| PermMol + DNN screening | 173,435 |
| e-Pharmacophore screening | 25,751 |
| Glide docking | 928 |
| Expert selection | 20 |
| Experimental candidates | 9 |

---

## Pharmacophore screening

The e-pharmacophore model was constructed from the human ETBR–Bosentan complex.

```text
PDB ID: 5XPR
Ligand: Bosentan
Docking box: 26 × 26 × 26 Å
Redocking RMSD: 1.74 Å
```

The selected pharmacophore contains seven features:

```text
A D N R R R R
```

The pharmacophore validation set contains:

```text
40 active compounds
1893 decoys
```

Performance was evaluated using **EF1%**, **BEDROC**, and **AUAC**.

---

## Molecular docking

Molecular docking was performed with **Schrödinger Glide** using a hierarchical protocol:

```text
HTVS → SP → XP
```

Docking poses, candidate structures, and receptor–ligand interaction files are included in the repository.

---

## Experimental validation

Five compounds showed more than 50% inhibition at 10 μM:

- C1
- C2
- C7
- C8
- C9

Measured IC50 values:

| Compound | IC50 (μM) |
|---|---:|
| C1 | 3.67 |
| C2 | 16.06 |
| C7 | 36.28 |
| C8 | 0.66 |
| C9 | 2.78 |
| BQ-788 | 0.0625 |

Binding-mode analysis files for the active compounds are also provided.

---

## Code

The repository provides scripts for:

- ChEMBL and BindingDB data preprocessing
- SMILES standardization and deduplication
- train/test splitting
- PermMol feature extraction
- RF and DNN training
- large-library virtual screening
- molecular similarity analysis

The PermMol package used in this study is included together with the feature-extraction script.

The screening scripts `ml_screener_dnn.py` and `ml_screener_rf.py` are configurable for different molecular representations and trained models.

---

## Requirements

The computational workflow uses:

- Python
- PyTorch
- scikit-learn
- RDKit
- PermMol
- Schrödinger Maestro / Glide 2021

Detailed environment configuration and reproducible execution commands will be provided together with the finalized reproduction setup.

---

## Data availability

Curated ETBR datasets, benchmark datasets, trained model checkpoints, evaluation logs, pharmacophore files, docking results, candidate-compound files, and analysis scripts are provided in this repository.

Raw commercial compound libraries from ChemDiv, Specs, and TopScience are not redistributed.

---

## Citation

Citation information will be added upon publication.
