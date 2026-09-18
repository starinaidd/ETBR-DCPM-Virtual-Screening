# ETBR-PermMol Virtual Screening

Code, data, trained models, pharmacophore models, docking results, and candidate-compound files associated with:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

> This repository is being prepared as the publication repository for the study. Environment setup and end-to-end reproduction instructions will be added after final reproducibility testing.

---

## Overview

This study uses the molecular representation model **PermMol** together with machine-learning models and structure-based virtual screening to identify novel endothelin B receptor (ETBR) antagonists.

The study contains three major components:

1. Benchmark evaluation of PermMol on MoleculeNet and MUV datasets.
2. ETBR activity prediction and ultra-large virtual screening using PermMol-based molecular representations.
3. Structure-based screening and experimental validation, including e-pharmacophore screening, Glide docking, expert inspection, and FLIPR assays.

---

## Workflow

```text
MoleculeNet / MUV benchmark evaluation
                ↓
ETBR activity dataset construction
                ↓
Molecular representation generation
                ↓
RF / DNN model training
                ↓
PermMol + DNN ETBR prediction model
                ↓
>16 million commercial compounds
                ↓
AI-based virtual screening
                ↓
173,435 compounds
                ↓
e-Pharmacophore screening
                ↓
25,751 compounds
                ↓
Glide HTVS → SP → XP docking
                ↓
928 compounds
                ↓
Expert inspection
                ↓
20 candidates
                ↓
Final compounds for experimental testing
                ↓
FLIPR validation and binding-mode analysis
```

---

## Repository structure

```text
ETBR-PermMol-Virtual-Screening/
├── 01_ML_Datasets/
│   ├── ETBR_dataset/
│   ├── ETBR_split/
│   ├── ETBR_PermMol_features/
│   ├── MoleculeNet/
│   └── MUV/
├── 02_Trained_Models/
│   ├── ETBR_models/
│   ├── ETBR_logs/
│   ├── MoleculeNet_models/
│   └── MUV_models/
├── 03_Pharmacophore/
│   ├── 5XPR_model/
│   └── Validation_set/
├── 04_Code/
│   ├── PermMol/
│   ├── preprocessing/
│   ├── training/
│   ├── screening/
│   └── analysis/
├── 05_Docking_and_Candidates/
│   ├── Docking_results/
│   ├── Expert_Selected_20/
│   ├── Final_10_Candidates/
│   └── Active_Hits_Binding_Modes/
└── README.md
```

---

## Data

### ETBR dataset

ETBR activity data were collected from **ChEMBL** and **BindingDB** using IC50 as the activity endpoint.

| Class | Number of compounds |
|---|---:|
| Active | 721 |
| Inactive | 1082 |
| Total | 1803 |

Activity thresholds:

```text
IC50 < 1000 nM      → active
IC50 > 10000 nM     → inactive
1000–10000 nM       → excluded
```

Final split:

```text
Training set: 1623 compounds
Test set:      180 compounds
```

### MoleculeNet

Seven benchmark datasets are included:

- BACE
- BBBP
- HIV
- ClinTox
- SIDER
- Tox21
- ToxCast

These datasets were used to compare PermMol with conventional molecular representations on molecular-property prediction tasks.

Some historical MoleculeNet files existed in multiple preprocessing versions. `_pro` files generally correspond to standardized-SMILES preprocessing; redundant historical copies do not need to be retained in the final public repository.

### MUV

The repository contains the 17 MUV virtual-screening benchmark tasks.

Large regenerable intermediate feature files may be omitted when they can be reproduced from the supplied input data and feature-extraction workflow.

---

## Molecular representations and models

Six molecular representations were evaluated:

- PermMol
- ECFP4
- MACCS
- PubChem
- RDKFingerprint
- Atom Pairs

RF and DNN classifiers were used for the ETBR prediction task.

PermMol produces a **1536-dimensional molecular representation** used as input to downstream models.

The main ETBR screening model is:

```text
PermMol + DNN
```

Trained model checkpoints and evaluation logs are stored under:

```text
02_Trained_Models/
```

Some historical MUV model directories contain fewer saved folds because individual training runs were manually stopped. The available historical checkpoints are preserved as-is.

---

## Virtual screening

The initial screening library contained more than **16 million commercially available compounds** from:

- ChemDiv
- Specs
- TopScience

Screening flow:

```text
>16 million compounds
        ↓
PermMol + DNN
        ↓
173,435 compounds
        ↓
e-Pharmacophore
        ↓
25,751 compounds
        ↓
HTVS / SP / XP docking
        ↓
928 compounds
        ↓
Expert inspection
        ↓
20 candidates
        ↓
Final experimental candidates
```

Raw commercial libraries are not necessarily redistributed because of file size and/or redistribution restrictions.

---

## Pharmacophore screening

The e-pharmacophore model was constructed from the human ETBR–Bosentan complex:

```text
PDB ID: 5XPR
Ligand: Bosentan
Grid box: 26 × 26 × 26 Å
Redocking RMSD: 1.74 Å
```

The final pharmacophore contains seven features:

```text
A D N R R R R
```

Validation set:

```text
40 active compounds
1893 decoys
```

Performance was assessed using enrichment metrics including EF1%, BEDROC, and AUAC.

---

## Molecular docking

Docking was performed using **Schrödinger Glide** with a hierarchical protocol:

```text
HTVS
 ↓
SP
 ↓
XP
```

Docking outputs and candidate structures are stored in:

```text
05_Docking_and_Candidates/
```

The `Expert_Selected_20` directory contains compounds retained after expert inspection.

Historical project files also include a 10-compound candidate set, whereas the current manuscript reports nine compounds selected for experimental validation. The historical files are retained for provenance.

---

## Experimental validation

The current manuscript reports five compounds with more than 50% inhibition at 10 μM:

- C1
- C2
- C7
- C8
- C9

Reported IC50 values:

| Compound | IC50 (μM) |
|---|---:|
| C1 | 3.67 |
| C2 | 16.06 |
| C7 | 36.28 |
| C8 | 0.66 |
| C9 | 2.78 |
| BQ-788 | 0.0625 |

Binding-mode analysis files are stored under:

```text
05_Docking_and_Candidates/Active_Hits_Binding_Modes/
```

---

## Code

The code archive is organized as:

```text
04_Code/
├── PermMol/          # PermMol package and feature extraction
├── preprocessing/    # dataset cleaning and preprocessing
├── training/         # RF and DNN training
├── screening/        # large-library screening
└── analysis/         # molecular similarity analysis
```

`ml_screener_dnn.py` and `ml_screener_rf.py` are configurable screening templates. Input dimensions, architecture parameters, model paths, and representation settings should be adjusted according to the trained model being used.

Detailed executable commands will be added after final reproducibility testing.

---

## Environment

**To be completed after reproducibility testing.**

Known information from the original project archive:

- PyTorch
- scikit-learn
- RDKit
- PermMol 0.1.0.dev0
- NumPy 1.21.6 for the original PermMol feature-extraction workflow
- Huawei Ascend 910 NPU for the original PermMol feature extraction
- Schrödinger Maestro / Glide 2021 for pharmacophore modeling and docking

A verified `environment.yml` or `requirements.txt` will be added after the original software versions are checked.

---

## Reproduction

**To be completed after final model reproduction.**

Planned modules:

### 1. PermMol feature extraction

```bash
# command to be added
```

Expected output:

```text
1536-dimensional molecular representations
```

### 2. ETBR model training

```bash
# command to be added
```

### 3. ETBR model evaluation

```bash
# command to be added
```

The current manuscript reports a PermMol + DNN test AUC of approximately **0.988**.

### 4. MoleculeNet benchmark reproduction

```bash
# command to be added
```

### 5. MUV benchmark reproduction

```bash
# command to be added
```

### 6. Large-library virtual screening

```bash
# command to be added
```

The exact environment, executable commands, and expected outputs will be added after the complete workflow has been rerun and verified.

---

## Data and model availability

The repository is intended to include:

- curated ETBR datasets
- ETBR train/test splits
- selected benchmark datasets
- trained model checkpoints
- evaluation logs
- pharmacophore files
- docking results
- candidate-compound files
- preprocessing, training, screening, and analysis scripts

The following may be excluded from public release:

- raw commercial compound libraries
- very large regenerable intermediate feature files
- redundant historical copies
- software-dependent temporary files

---

## Citation

Citation information will be added after publication.

---

## License

License information will be added before public release.

---

## Contact

Contact information will be added before public release.
