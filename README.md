# ETBR-PermMol Virtual Screening

This repository contains the data, code, pretrained models, and supporting files for:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

In this study, PermMol molecular representations were combined with machine-learning models for ETBR activity prediction and subsequently integrated with pharmacophore screening and molecular docking for large-scale virtual screening.

The curated ETBR dataset contains 1,803 compounds, including 721 actives and 1,082 inactives. PermMol represents each molecule as a 1,536-dimensional embedding.

## Requirements

### PermMol feature extraction

```text
Python 3.9.13
PermMol 0.1.0.dev0
MindSpore 2.0.0a0
NumPy 1.21.6
pandas 1.3.4
RDKit 2023.03.1
wget 3.2
```

### ETBR DNN

```text
Python 3.9.18
PyTorch 1.13.1+cu117
NumPy 1.26.1
pandas 2.3.3
scikit-learn 1.0.2
RDKit 2025.09.2
```

## Data and Models

The ETBR train/test split is provided in:

```text
01_ML_Datasets/ETBR_split/
├── ETB_train.csv
└── ETB_test.csv
```

The corresponding PermMol embeddings are provided in:

```text
01_ML_Datasets/ETBR_PermMol_features/
├── ETB_train_permmol.pkl
└── ETB_test_permmol.pkl
```

Their dimensions are:

```text
ETB_train_permmol.pkl   (1623, 1536)
ETB_test_permmol.pkl     (180, 1536)
```

Pretrained ETBR PermMol-DNN checkpoints are provided in:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
```

with five fold models:

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

The molecular order in each PermMol `.pkl` file is identical to that in the corresponding CSV file.

## Usage

### PermMol feature extraction

PermMol representations are generated using `extract_feat.py`.

The extraction settings used in this study are:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

Run:

```bash
python extract_feat.py
```

The output is a `.pkl` file containing the PermMol embeddings.

### ETBR virtual screening

The ETBR screening script is:

```text
04_Code/screening/ml_screener_dnn.py
```

For PermMol screening, the input CSV and its PermMol feature file should have the same basename, for example:

```text
demo_100.csv
demo_100.pkl
```

Run:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file reproduction_demo/demo_100.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir reproduction_demo
```

The fold-0 ETBR DNN uses:

```text
1536 -> 64 -> 128 -> 64 -> 1
```

with dropout:

```text
0.20112391936365895
```

A sigmoid transformation is applied to the model output, and compounds with predicted probability ≥ 0.5 are retained.

## Reproducibility

The provided fold-0 checkpoint reproduces the following results on the 180-compound independent ETBR test set:

| Metric | Value |
|---|---:|
| AUC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

PermMol features were also independently regenerated for the first 100 compounds of the ETBR test set.

```text
Feature shape: (100, 1536)
Maximum absolute difference: 0.0
allclose: True
```

Using these regenerated features and `model_fold_0.pth`, 33 of the 100 compounds were classified as active at a threshold of 0.5.

## Additional Files

Training scripts for the molecular representations and machine-learning models evaluated in the study are available in:

```text
04_Code/training/
```

Pharmacophore and molecular-docking files are available in:

```text
03_Pharmacophore/
05_Docking_and_Candidates/
```

The complete commercial screening library is not redistributed because of data volume and source/licensing restrictions.

## Citation

If you use the code, processed data, molecular representations, or pretrained models from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**
