# ETBR-PermMol Virtual Screening

This repository provides the code, processed data, molecular representations, trained models, and supporting computational files used in:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

We developed a multistage virtual-screening strategy for endothelin B receptor (ETBR) antagonists by integrating PermMol molecular representations, machine-learning prediction, structure-based pharmacophore screening, molecular docking, and experimental validation.

For the machine-learning stage, PermMol encodes each molecule as a 1536-dimensional representation and is combined with a deep neural network (DNN) for ETBR activity prediction. The curated ETBR dataset contains 1,803 compounds, including 721 actives and 1,082 inactives.

The repository also contains files associated with the downstream pharmacophore, docking, and candidate-selection stages of the study.

---

## Installation

Two environments are used for PermMol feature extraction and ETBR DNN prediction.

### PermMol feature extraction

The feature-extraction workflow was verified with:

```text
Python       3.9.13
PermMol      0.1.0.dev0
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

### ETBR DNN prediction

The ETBR PermMol-DNN workflow was verified with:

```text
Python          3.9.18
PyTorch         1.13.1+cu117
NumPy           1.26.1
pandas          2.3.3
scikit-learn    1.0.2
RDKit           2025.09.2
```

---

## Data and pretrained models

The ETBR dataset is provided as:

```text
01_ML_Datasets/ETBR_split/ETB_train.csv
01_ML_Datasets/ETBR_split/ETB_test.csv
```

The final split contains:

```text
Training set: 1623 compounds
Test set:      180 compounds
```

Precomputed PermMol representations are provided as:

```text
01_ML_Datasets/ETBR_PermMol_features/ETB_train_permmol.pkl
01_ML_Datasets/ETBR_PermMol_features/ETB_test_permmol.pkl
```

with dimensions:

```text
ETB_train_permmol.pkl    (1623, 1536)
ETB_test_permmol.pkl      (180, 1536)
```

The molecular order in each `.pkl` file is identical to that in the corresponding CSV file.

Five pretrained ETBR PermMol-DNN checkpoints are provided in:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
```

including:

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

---

## Usage

### 1. Generate PermMol representations

PermMol feature extraction is performed with the provided `extract_feat.py`.

The input file must contain a column named:

```text
smiles
```

Set the input and output directories in `extract_feat.py` and run:

```bash
python extract_feat.py
```

The extraction settings used in this study are:

```text
max_len = 301
batch_size = 256
```

Each molecule is represented by a 1536-dimensional PermMol vector and saved as a `.pkl` file.

For example:

```text
input:
example.csv

output:
example.pkl
```

For `N` molecules, the expected feature shape is:

```text
(N, 1536)
```

---

### 2. Screen molecules with the pretrained ETBR DNN

The screening script is:

```text
04_Code/screening/ml_screener_dnn.py
```

For PermMol screening, the input CSV and PermMol feature file must have the same basename and must preserve the same molecular order.

For example:

```text
example.csv
example.pkl
```

Run:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file path/to/example.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir path/to/output
```

The script automatically reads the corresponding PermMol feature file:

```text
example.csv -> example.pkl
```

and applies the pretrained ETBR DNN model.

The fold-0 model uses:

```text
Input dimension: 1536
Hidden layers:   64 -> 128 -> 64
Output:          1
Dropout:         0.20112391936365895
```

The model output is converted to a probability using a sigmoid function.

Compounds with:

```text
predicted probability >= 0.5
```

are retained as predicted ETBR actives.

The screened SMILES are written to:

```text
example_screen_new_0.5.csv
```

---

## Reproducibility

### ETBR independent test set

Using the provided ETBR test set, precomputed PermMol representations, and `model_fold_0.pth`, the following results were reproduced:

| Metric | Value |
|---|---:|
| AUC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

### PermMol feature extraction

PermMol representations were independently regenerated for the first 100 compounds of the ETBR test set.

The regenerated feature matrix had shape:

```text
(100, 1536)
```

Comparison with the corresponding stored representations gave:

```text
maximum absolute difference = 0.0
allclose = True
```

The regenerated representations were subsequently passed through the pretrained fold-0 ETBR DNN model.

At a classification threshold of 0.5:

```text
100 molecules tested
33 molecules predicted as active
```

This verifies the complete inference path from molecular SMILES to PermMol representation and ETBR activity prediction.

---

## Model training

Training scripts for the molecular representations and machine-learning models evaluated in this study are available under:

```text
04_Code/training/
```

The study evaluates PermMol and conventional molecular fingerprints with random forest and deep neural network models.

The pretrained checkpoints supplied in this repository can be used directly to reproduce the reported ETBR prediction results without retraining.

---

## Pharmacophore and molecular docking

Supporting files for the structure-based screening stages are provided in:

```text
03_Pharmacophore/
05_Docking_and_Candidates/
```

These files correspond to the pharmacophore screening, Glide docking, and candidate-selection procedures described in the accompanying manuscript.

Running the Schrödinger-based pharmacophore and docking stages requires an appropriate Schrödinger installation and license.

---

## Data availability

The processed ETBR datasets, molecular representations, trained models, and supporting computational files used in this study are included in this repository.

The complete ultra-large commercial compound library is not redistributed because of its size and source/licensing restrictions.

---

## Citation

If you use the code, processed data, PermMol representations, or trained models from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**
