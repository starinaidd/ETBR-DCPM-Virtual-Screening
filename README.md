# ETBR-PermMol Virtual Screening

Code, processed datasets, molecular representations, trained models, and supporting files for the study:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

This repository provides the data and code required to reproduce the machine-learning component of the ETBR virtual-screening study and to apply the trained ETBR PermMol-DNN model to new molecules.

---

## 1. Repository Structure

```text
ETBR-PermMol-Virtual-Screening/
├── 01_ML_Datasets/
│   ├── ETBR_split/
│   └── ETBR_PermMol_features/
│
├── 02_Trained_Models/
│   └── ETBR_models/
│
├── 03_Pharmacophore/
│
├── 04_Code/
│   ├── training/
│   └── screening/
│
├── 05_Docking_and_Candidates/
│
├── reproduction_demo/
│
└── README.md
```

The main files required for reproducing ETBR PermMol-DNN prediction are:

```text
01_ML_Datasets/ETBR_split/ETB_test.csv

01_ML_Datasets/ETBR_PermMol_features/
└── ETB_test_permmol.pkl

02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
├── model_fold_0.pth
├── model_fold_1.pth
├── model_fold_2.pth
├── model_fold_3.pth
└── model_fold_4.pth

04_Code/screening/
├── ml_screener_dnn.py
└── dnn_torch_utils.py
```

---

## 2. ETBR Dataset

The curated ETBR dataset contains 1,803 compounds:

```text
Total compounds:    1803
Active compounds:    721
Inactive compounds: 1082
```

The final split contains:

```text
Training set: 1623 compounds
Test set:      180 compounds
```

The CSV files are located at:

```text
01_ML_Datasets/ETBR_split/ETB_train.csv
01_ML_Datasets/ETBR_split/ETB_test.csv
```

The CSV format is:

```text
smiles,activity
```

where:

- `smiles` is the molecular SMILES string.
- `activity` is the binary activity label.
- `1` represents active.
- `0` represents inactive.

---

## 3. PermMol Molecular Representations

PermMol is used to convert each molecule into a 1536-dimensional molecular representation.

Precomputed PermMol features for the ETBR dataset are provided in:

```text
01_ML_Datasets/ETBR_PermMol_features/
├── ETB_train_permmol.pkl
└── ETB_test_permmol.pkl
```

Feature dimensions:

```text
ETB_train_permmol.pkl : (1623, 1536)
ETB_test_permmol.pkl  : (180, 1536)
```

The row order of each `.pkl` file corresponds to the row order of its associated CSV file.

For example:

```text
ETB_test.csv row 1
        ↓
ETB_test_permmol.pkl row 1
```

Therefore, the CSV and PermMol feature files should not be independently reordered.

---

## 4. Environment

Two environments are used because PermMol feature extraction is based on MindSpore, whereas the downstream ETBR DNN model is implemented in PyTorch.

### 4.1 PermMol feature extraction

The PermMol feature extraction workflow was verified with:

```text
Python       3.9.13
PermMol      0.1.0.dev0
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

PermMol takes a CSV file containing a `smiles` column and generates a pickle file containing a 1536-dimensional representation for each molecule.

### 4.2 ETBR DNN prediction

The downstream DNN prediction workflow was verified with:

```text
Python          3.9.18
PyTorch         1.13.1+cu117
NumPy           1.26.1
pandas          2.3.3
scikit-learn    1.0.2
RDKit           2025.09.2
```

---

## 5. Quick Start

The simplest way to test the repository is to use the provided PermMol features and pretrained ETBR DNN checkpoint.

The screening script is:

```text
04_Code/screening/ml_screener_dnn.py
```

The model definition used by the script is:

```text
04_Code/screening/dnn_torch_utils.py
```

The pretrained fold-0 model is:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth
```

---

## 6. Screen Molecules with the ETBR PermMol-DNN Model

### 6.1 Prepare the input CSV

The input CSV must contain a column named:

```text
smiles
```

For example:

```csv
smiles,activity
CCO,0
CCN,1
CCC,0
```

The `activity` column is optional when screening new unlabeled compounds.

### 6.2 Prepare the PermMol feature file

The PermMol feature file must:

1. have the same basename as the CSV file;
2. be located in the same directory;
3. contain one 1536-dimensional vector for each molecule;
4. preserve exactly the same molecular order as the CSV file.

For example:

```text
demo_100.csv
demo_100.pkl
```

For 100 molecules:

```text
demo_100.pkl shape = (100, 1536)
```

The screening script automatically obtains the feature filename from the CSV filename:

```text
demo_100.csv
      ↓
demo_100.pkl
```

Therefore, the `.pkl` file does not need to be specified separately on the command line.

---

## 7. Run ETBR PermMol-DNN Screening

From the repository root, run:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file reproduction_demo/demo_100.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir reproduction_demo
```

Arguments:

| Argument | Description |
|---|---|
| `--file` | Input CSV containing SMILES |
| `--models` | Trained DNN checkpoint |
| `--prop` | Classification probability threshold |
| `--out_dir` | Directory used to save screening results |

The default screening threshold used here is:

```text
0.5
```

The script performs:

```text
PermMol feature
      ↓
1536-dimensional input
      ↓
ETBR DNN
      ↓
sigmoid probability
      ↓
probability >= 0.5
      ↓
predicted active compound
```

The output file is named automatically, for example:

```text
demo_100_screen_new_0.5.csv
```

The output contains the SMILES of compounds classified as active by the model.

---

## 8. Reproduction Example

A 100-molecule example is provided under:

```text
reproduction_demo/
```

Recommended files:

```text
reproduction_demo/
├── demo_100.csv
├── demo_100.pkl
└── demo_100_screen_new_0.5.csv
```

`demo_100.csv` contains the first 100 molecules from the ETBR independent test set.

`demo_100.pkl` was independently regenerated with PermMol.

The regenerated PermMol feature matrix has shape:

```text
(100, 1536)
```

The regenerated features were compared with the corresponding first 100 rows of the original ETBR test features.

Result:

```text
maximum absolute difference = 0.0
allclose = True
```

This confirms exact agreement between the regenerated and stored PermMol representations for these 100 molecules.

The regenerated features were then screened using:

```text
model_fold_0.pth
```

with a threshold of:

```text
0.5
```

Expected output:

```text
Number of molecules:       100
Predicted active:           33
Predicted active fraction: 33.0%
```

A successful run should end with output similar to:

```text
共有 100 个分子需要筛选
100
screen 33
screen precent 33.0 %
```

---

## 9. Reproduce the ETBR Test-Set Performance

The independent ETBR test set contains 180 compounds.

The required files are:

```text
01_ML_Datasets/ETBR_split/ETB_test.csv

01_ML_Datasets/ETBR_PermMol_features/
└── ETB_test_permmol.pkl

02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
└── model_fold_0.pth
```

The fold-0 DNN architecture is:

```text
1536 -> 64 -> 128 -> 64 -> 1
```

The fold-0 dropout ratio is:

```text
0.20112391936365895
```

The output of the network is transformed using a sigmoid function.

Using a classification threshold of 0.5, the reproduced independent-test results are:

| Metric | Reproduced value |
|---|---:|
| AUC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

These values reproduce the stored fold-0 ETBR PermMol-DNN evaluation results.

---

## 10. Generate PermMol Features for New Molecules

To screen a new molecular library, first prepare a CSV file containing a `smiles` column.

For example:

```text
new_library.csv
```

The file must contain:

```csv
smiles
SMILES_1
SMILES_2
SMILES_3
...
```

Use the provided PermMol feature-extraction script in the PermMol/MindSpore environment.

The PermMol extraction settings used in this study are:

```text
max_len   = 301
batch_size = 256
SMILES column = smiles
```

The resulting feature matrix must contain:

```text
number of rows = number of molecules
number of columns = 1536
```

For example:

```text
new_library.csv
new_library.pkl
```

Before screening, verify that the number of molecules and feature vectors is identical.

The resulting pair can then be supplied to `ml_screener_dnn.py`.

---

## 11. Screening a New Compound Library

For a new compound library:

```text
new_library.csv
new_library.pkl
```

run:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file path/to/new_library.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir path/to/output
```

For large compound libraries, the input can be divided into multiple CSV files and the corresponding PermMol feature files generated separately.

The molecular order between each CSV file and its corresponding `.pkl` file must always be preserved.

---

## 12. Training Code

Model-training scripts are available under:

```text
04_Code/training/
```

The repository contains scripts for different molecular representations, including:

```text
PermMol
ECFP4
MACCS
RDKit fingerprint
AtomPairs
PubChem fingerprint
```

and machine-learning methods including:

```text
DNN
Random Forest
```

The PermMol DNN training script is:

```text
04_Code/training/dnn_permmol.py
```

The provided pretrained checkpoints are recommended when reproducing the reported ETBR screening results.

---

## 13. Trained Models

ETBR trained models are stored under:

```text
02_Trained_Models/ETBR_models/
```

The PermMol-DNN models are located at:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
```

Five fold checkpoints are provided:

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

For the reproduction example described above, use:

```text
model_fold_0.pth
```

---

## 14. Pharmacophore and Docking Files

Files associated with the downstream structure-based screening steps are provided in:

```text
03_Pharmacophore/
```

and:

```text
05_Docking_and_Candidates/
```

These directories contain the supporting files used for pharmacophore screening, molecular docking, and candidate selection described in the accompanying manuscript.

---

## 15. Notes

When running PermMol-DNN screening:

- Do not reorder the CSV after generating the corresponding PermMol feature file.
- The CSV and `.pkl` files must contain the same number of molecules.
- PermMol features must have 1536 dimensions.
- The ETBR checkpoint architecture must match the feature dimension.
- The screening threshold used in the provided example is 0.5.
- `model_fold_0.pth` is used for the supplied reproduction example.

---

## 16. Data Availability

This repository contains the processed ETBR datasets, precomputed molecular representations, trained machine-learning models, code, and supporting files used in the computational study.

The complete ultra-large commercial compound library is not redistributed because of data volume and source/licensing restrictions.

---

## 17. Citation

If you use the code, processed data, molecular representations, or trained models from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**
