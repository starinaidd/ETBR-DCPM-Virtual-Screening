# DCPM-ETBR Virtual Screening

Code, data, trained models, and structure-based screening resources associated with the study:

**Discovery of novel endothelin B receptor antagonists through DCPM-enabled multistage virtual screening of ultra-large commercial libraries**

## Overview

This repository provides the computational resources for a multistage virtual-screening workflow developed to discover novel endothelin B receptor (ETBR) antagonists.

The workflow integrates **DCPM**, an in-house small-molecule foundation model, with machine-learning classification, energy-based pharmacophore screening, molecular docking, and experimental validation.

DCPM was pretrained on approximately 100 million unlabeled small molecules and converts standardized molecular SMILES into fixed-length **1 × 1536 molecular embeddings**. These representations are used as input features for downstream molecular-property prediction, ETBR activity classification, and large-scale virtual screening.

DCPM was evaluated on **7 MoleculeNet datasets** and **17 MUV virtual-screening tasks**. For ETBR activity prediction, the DCPM+DNN model achieved an AUC-ROC of **0.988** on the independent test set.

The complete screening workflow reduced more than **16 million commercially available compounds to 9 compounds for experimental evaluation**.

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
pip install --no-deps 04_Code/DCPM/DCPM-0.1.0.dev0-py3-none-any.whl
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

| **Class** | **Number of compounds** |
|---|---:|
| Active | 721 |
| Inactive | 1,082 |
| Total | 1,803 |

The final split contains:

| **Dataset** | **Number of compounds** |
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

| **Metric** | **Value** |
|---|---:|
| AUC-ROC | 0.988 |
| Sensitivity | 0.889 |
| Specificity | 0.963 |
| Accuracy | 0.933 |
| MCC | 0.861 |

## Usage

### DCPM feature extraction

DCPM converts standardized SMILES into **1536-dimensional molecular representations**.

Input CSV files must contain a column named `smiles`.

The feature-extraction script reads CSV files from `csv/` and writes the corresponding DCPM representations to `sar/feats/`.

```bash
cd 04_Code/DCPM

mkdir -p csv
mkdir -p sar/feats

cp /path/to/input.csv csv/

python extract_feat.py
```

### ETBR DCPM+DNN model

The DCPM representations of the ETBR training and test sets are provided with the repository.

Run the DCPM+DNN training workflow from the repository root:

```bash
python -u 04_Code/training/dnn_dcpm.py
```

The DNN contains three fully connected hidden layers with ReLU activation and dropout regularization.

Hyperparameters including learning rate, dropout rate, and hidden-layer dimensions are optimized using Hyperopt.

### ETBR ECFP4+RF baseline

A conventional molecular-fingerprint baseline can be reproduced using ECFP4 and random forest:

```bash
python -u 04_Code/training/rf_ecfp4.py
```

ECFP4 fingerprints are generated directly from molecular SMILES and used as input to the RF classifier.

### MoleculeNet benchmark

DCPM was evaluated on seven MoleculeNet molecular-property prediction datasets and compared with conventional molecular fingerprints.

For example, the DCPM+DNN workflow for the **BACE** dataset can be run with:

```bash
python -u 04_Code/training/dnn_dcpm_bace.py
```

### MUV virtual-screening benchmark

The repository contains all **17 MUV benchmark tasks** used to evaluate molecular representations under highly imbalanced virtual-screening conditions.

For example, the DCPM+DNN workflow for **MUV_859** can be run with:

```bash
python -u 04_Code/training/dnn_dcpm_muv859.py
```

### ETBR large-scale virtual screening

The DNN screening script is provided under:

```text
04_Code/screening/
```

After DCPM representation generation, compounds can be screened using a trained ETBR DCPM+DNN checkpoint.

Example:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file /path/to/input.csv \
    --models /path/to/model_fold_0.pth \
    --prop 0.5 \
    --smiles_col smiles \
    --out_dir ./screening_output
```

The screening threshold used in the study was `P(active) > 0.5`.

## e-Pharmacophore Screening

The e-pharmacophore model and validation files are provided under:

```text
03_Pharmacophore/
```

The model contains seven pharmacophore features:

```text
ADNRRRR
```

Compounds matching at least **5 of the 7 features** were retained in the study.

The supplied pharmacophore files can be inspected and applied using Schrödinger Maestro/Phase.

## Data Availability

The repository provides the curated ETBR datasets, benchmark datasets, molecular representations, trained models, model evaluation results, feature-extraction code, pharmacophore resources, docking results, candidate compounds, and analysis scripts associated with this study.

The complete commercial compound libraries containing more than **16 million compounds** from ChemDiv, Specs, and TopScience are not redistributed because of their size and source/licensing restrictions.

## Citation

If you use the data, models, or workflow provided in this repository, please cite the corresponding publication.

```text
Citation information will be added upon publication.
```
