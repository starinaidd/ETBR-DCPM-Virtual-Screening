# DCPM-ETBR Virtual Screening

Code, data, trained models, and structure-based screening resources associated with the study:

**Discovery of novel endothelin B receptor antagonists through DCPM-enabled multistage virtual screening of ultra-large commercial libraries**

## Overview

This repository provides the computational resources for a multistage virtual-screening workflow developed to discover novel endothelin B receptor (ETBR) antagonists.

The workflow integrates **DCPM**, an in-house small-molecule foundation model, with machine-learning classification, energy-based pharmacophore screening, molecular docking, and experimental validation.

DCPM was pretrained on approximately 100 million unlabeled small molecules and converts standardized molecular SMILES into fixed-length **1 × 1536 molecular embeddings**. These representations are used as input features for downstream molecular-property prediction, ETBR activity classification, and large-scale virtual screening.

DCPM was evaluated on **7 MoleculeNet datasets** and **17 MUV virtual-screening tasks**. For ETBR activity prediction, the DCPM+DNN model achieved an AUC-ROC of **0.988** on the independent test set.

The complete screening workflow reduced more than **16 million commercially available compounds to 9 compounds for experimental evaluation**.

## Workflow

```text
>16 million commercial compounds
              │
              ▼
          DCPM + DNN
              │
              ▼
        173,435 compounds
              │
              ▼
      e-Pharmacophore
              │
              ▼
         25,751 compounds
              │
              ▼
     Glide HTVS → SP → XP
              │
              ▼
           928 compounds
              │
              ▼
       Expert inspection
              │
              ▼
          20 candidates
              │
              ▼
    Commercial availability
              │
              ▼
      9 compounds tested
              │
              ▼
     FLIPR functional assay
```

## Installation

### Machine-learning environment

Create the environment from the supplied YAML file:

```bash
conda env create -f environment.yml
conda activate etbr-dnn
```

### DCPM feature-extraction environment

The DCPM feature-extraction workflow was verified using:

```text
Python       3.9.13
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

Install the supplied DCPM package:

```bash
pip install --no-deps 04_Code/DCPM/permmol-0.1.0.dev0-py3-none-any.whl
pip install wget==3.2
```

A compatible MindSpore environment is required for DCPM feature extraction.

## Data and Models

### ETBR dataset

ETBR activity data were collected from ChEMBL and BindingDB using IC50 as the primary activity endpoint.

Compounds were classified according to:

```text
IC50 < 1,000 nM       Active
IC50 > 10,000 nM      Inactive
1,000–10,000 nM       Excluded
```

The final curated ETBR dataset contains:

| Class | Number of compounds |
|---|---:|
| Active | 721 |
| Inactive | 1,082 |
| Total | 1,803 |

The final split contains:

| Dataset | Number of compounds |
|---|---:|
| Training set | 1,623 |
| Test set | 180 |

### Benchmark datasets

Seven MoleculeNet classification datasets were used:

```text
BACE
BBBP
HIV
ClinTox
SIDER
Tox21
ToxCast
```

The MUV benchmark contains **17 highly imbalanced virtual-screening tasks**.

Six molecular representations were evaluated:

```text
DCPM
ECFP4
MACCS
PubChem
RDKFingerprint
Atom Pairs
```

Both random forest (**RF**) and deep neural network (**DNN**) classifiers were investigated.

### ETBR prediction performance

The DCPM+DNN model was selected as the primary activity prediction model for subsequent ETBR virtual screening.

Performance on the independent ETBR test set:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988 |
| Sensitivity | 0.889 |
| Specificity | 0.963 |
| Accuracy | 0.933 |
| MCC | 0.861 |

## Usage

### DCPM feature extraction

DCPM converts standardized SMILES into **1536-dimensional molecular representations**.

Input CSV files must contain a column named:

```text
smiles
```

The feature-extraction script reads CSV files from `csv/` and writes pickle feature files to `sar/feats/`.

```bash
cd 04_Code/DCPM

mkdir -p csv
mkdir -p sar/feats

cp <input.csv> csv/

python extract_feat.py
```

For an input file:

```text
csv/example.csv
```

the corresponding DCPM representation is written as:

```text
sar/feats/example.pkl
```

with feature dimension:

```text
N × 1536
```

where `N` is the number of molecules.

---

### ETBR DCPM+DNN model

The DCPM representations of the ETBR training and test sets are provided with the repository.

Run the DCPM+DNN training workflow from the repository root:

```bash
python -u 04_Code/training/dnn_dcpm.py
```

The DNN contains three fully connected hidden layers with ReLU activation and dropout regularization.

Hyperparameters including learning rate, dropout rate, and hidden-layer dimensions are optimized using Hyperopt.

Five-fold model development generates checkpoints of the form:

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

---

### ETBR ECFP4+RF baseline

A conventional molecular-fingerprint baseline can be reproduced using ECFP4 and random forest:

```bash
python -u 04_Code/training/rf_ecfp4.py
```

ECFP4 fingerprints are generated directly from molecular SMILES and used as input to the RF classifier.

---

### MoleculeNet benchmark

DCPM was evaluated on seven MoleculeNet molecular-property prediction datasets and compared with conventional molecular fingerprints.

A representative verified DCPM+DNN workflow using the **BACE** dataset can be run with:

```bash
python -u 04_Code/training/dnn_dcpm_bace.py
```

Across the seven MoleculeNet tasks, DCPM achieved the best performance on:

```text
BBBP
ClinTox
ToxCast
```

corresponding to **3 of the 7 benchmark tasks**.

---

### MUV virtual-screening benchmark

The repository contains all **17 MUV benchmark tasks** used to evaluate molecular representations under highly imbalanced virtual-screening conditions.

A representative verified DCPM+DNN workflow using **MUV_859** can be run with:

```bash
python -u 04_Code/training/dnn_dcpm_muv859.py
```

Across the 17 MUV tasks, the DCPM+DNN combination achieved the best AUC-ROC performance on **5 tasks**.

---

### ETBR large-scale virtual screening

The initial screening library contained more than **16 million commercially available compounds** collected from:

```text
ChemDiv
Specs
TopScience
```

All compounds were standardized, deduplicated, and converted into DCPM molecular representations.

The optimized DCPM+DNN model was applied using:

```text
P(active) > 0.5
```

as the screening threshold.

This step retained:

```text
173,435 compounds
```

The DNN screening script is provided under:

```text
04_Code/screening/
```

Example:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file <input.csv> \
    --models <model_checkpoint.pth> \
    --prop 0.5 \
    --smiles_col smiles \
    --out_dir <output_directory>
```

A single trained checkpoint is specified through `--models`.

For example:

```text
model_fold_0.pth
```

can be used for a single-checkpoint screening run.

## e-Pharmacophore Screening

An energy-based pharmacophore model was constructed from the crystal structure of human ETBR in complex with Bosentan:

```text
PDB ID:       5XPR
Ligand:       Bosentan
Resolution:   3.60 Å
```

The final pharmacophore contains seven features:

```text
A D N R R R R
```

corresponding to:

```text
1 hydrogen-bond acceptor
1 hydrogen-bond donor
1 negative-charge feature
4 aromatic-ring features
```

The pharmacophore validation dataset contains:

```text
40 active compounds
1,893 decoys
```

The model retaining compounds matching at least **5 of the 7 pharmacophore features** was selected for large-scale screening.

Validation performance:

| Metric | Value |
|---|---:|
| EF1% | 10.17 |
| BEDROC | 0.23 |
| AUAC | 0.55 |

Application of the pharmacophore model reduced the DCPM+DNN screening set from:

```text
173,435
   ↓
25,751 compounds
```

The pharmacophore model, prepared receptor and ligand, receptor grid, redocking results, feature table, and validation datasets are provided under:

```text
03_Pharmacophore/
```

## Molecular Docking

The 25,751 compounds retained after pharmacophore screening were subjected to hierarchical molecular docking using **Schrödinger Glide**.

The docking protocol consisted of:

```text
HTVS
 ↓ retain 50%

SP
 ↓ retain 40%

XP
 ↓ retain 20%
```

After hierarchical docking and XP-score-based prioritization:

```text
928 compounds
```

were retained for further inspection.

Expert inspection focused on interactions with key ETBR residues:

```text
Asp154
Lys182
Phe240
Lys273
His340
Arg343
```

Hydrogen bonding, ionic interactions, π–π stacking, and overall receptor–ligand binding compatibility were considered during compound prioritization.

This process yielded:

```text
928 docked compounds
        ↓
20 expert-selected candidates
        ↓
9 commercially available compounds
```

Docking results, expert-selected compounds, and binding-mode files are provided under:

```text
05_Docking_and_Candidates/
```

Schrödinger Maestro/Glide is proprietary software and is not distributed with this repository.

## Experimental Validation

Nine selected compounds were evaluated for ETBR antagonistic activity using a **FLIPR calcium mobilization assay**.

Five compounds showed more than 50% inhibition of ET-1-induced calcium signaling at 10 μM:

```text
C1
C2
C7
C8
C9
```

The experimental hit rate was:

```text
55.6%
```

Concentration-response experiments produced the following IC50 values:

| Compound | IC50 (μM) |
|---|---:|
| C1 | 3.67 |
| C2 | 16.06 |
| C7 | 36.28 |
| C8 | **0.66** |
| C9 | 2.78 |
| BQ-788 | 0.0625 |

Among the newly identified compounds, **C8 showed the strongest ETBR antagonistic activity**, reaching the submicromolar range with an IC50 of **0.66 μM**.

## Available Resources

| Resource | Content |
|---|---|
| ETBR activity data | Curated active/inactive dataset |
| ETBR train/test split | 1,623 training and 180 test compounds |
| DCPM representations | 1536-dimensional molecular embeddings |
| MoleculeNet | Seven molecular-property benchmark datasets |
| MUV | Seventeen virtual-screening benchmark tasks |
| Trained models | RF and DNN checkpoints |
| Evaluation results | Model evaluation logs |
| DCPM feature extraction | DCPM package and extraction script |
| Pharmacophore | 5XPR-Bosentan e-pharmacophore and validation data |
| Molecular docking | Glide docking outputs |
| Candidate compounds | Expert-selected and experimentally tested compounds |
| Binding-mode analysis | Docking poses and interaction analysis of active hits |

## Data Availability

The repository provides the curated ETBR datasets, benchmark datasets, molecular representations, trained models, model evaluation results, feature-extraction code, pharmacophore resources, docking results, candidate compounds, and analysis scripts associated with this study.

The complete commercial compound libraries containing more than **16 million compounds** from ChemDiv, Specs, and TopScience are not redistributed because of their size and source/licensing restrictions.

## Citation

If you use the data, models, or workflow provided in this repository, please cite the corresponding publication.

```text
Citation information will be added upon publication.
```
