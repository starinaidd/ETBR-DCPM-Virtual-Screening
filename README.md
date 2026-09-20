# ETBR-PermMol Virtual Screening

This repository contains the datasets, molecular representations, trained models, and scripts used in the study:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

The repository focuses on machine-learning prediction of endothelin B receptor (ETBR) activity using PermMol molecular representations and provides the files required to reproduce the ETBR PermMol-DNN results reported in the study.

## Repository Contents

| Directory | Description |
|---|---|
| `01_ML_Datasets/` | ETBR datasets and molecular representations |
| `02_Trained_Models/` | Trained ETBR machine-learning models |
| `03_Pharmacophore/` | Pharmacophore-related files |
| `04_Code/` | Model training and virtual-screening scripts |
| `05_Docking_and_Candidates/` | Docking and candidate-selection files |

The ETBR dataset contains 1,803 compounds, including 721 active and 1,082 inactive compounds.

The provided split contains:

- 1,623 training compounds
- 180 independent test compounds

The corresponding PermMol representation has 1,536 dimensions per molecule.

## Environment

Two environments are used for PermMol feature extraction and downstream DNN prediction.

### PermMol feature extraction

The following package versions were used for the verified PermMol feature extraction:

```text
Python              3.9.13
PermMol             0.1.0.dev0
MindSpore           2.0.0a0
NumPy               1.21.6
pandas              1.3.4
RDKit               2023.03.1
wget                3.2
```

### ETBR DNN prediction

The ETBR PermMol-DNN model was verified with:

```text
Python              3.9.18
PyTorch             1.13.1+cu117
NumPy               1.26.1
pandas              2.3.3
scikit-learn        1.0.2
RDKit               2025.09.2
```

## Data

The ETBR train/test split is provided in:

```text
01_ML_Datasets/ETBR_split/ETB_train.csv
01_ML_Datasets/ETBR_split/ETB_test.csv
```

Precomputed PermMol representations are provided in:

```text
01_ML_Datasets/ETBR_PermMol_features/ETB_train_permmol.pkl
01_ML_Datasets/ETBR_PermMol_features/ETB_test_permmol.pkl
```

Each row of a PermMol feature file corresponds to the molecule at the same row position in the corresponding CSV file.

## Pretrained ETBR Models

The pretrained PermMol-DNN checkpoints are located in:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
```

Five model checkpoints are provided:

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

For fold 0, the DNN architecture is:

```text
1536 -> 64 -> 128 -> 64 -> 1
```

with a dropout ratio of:

```text
0.20112391936365895
```

The model outputs a logit, followed by a sigmoid transformation for activity probability prediction.

## Virtual Screening

The DNN screening script is located at:

```text
04_Code/screening/ml_screener_dnn.py
```

The input CSV must contain a `smiles` column.

For PermMol screening, a PermMol feature file with the same basename must be placed in the same directory as the input CSV.

For example:

```text
demo_100.csv
demo_100.pkl
```

where `demo_100.pkl` contains a feature matrix of shape:

```text
(100, 1536)
```

Run the ETBR PermMol-DNN screening using:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file path/to/demo_100.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir path/to/output
```

`--prop 0.5` specifies the classification threshold.

The output file contains the SMILES of compounds predicted as active by the model.

## Reproducibility

The provided fold-0 PermMol-DNN checkpoint was evaluated on the complete 180-compound ETBR independent test set.

| Metric | Value |
|---|---:|
| AUC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

A separate feature-extraction check was also performed using the first 100 compounds of the ETBR test set.

The independently generated PermMol feature matrix had the expected shape:

```text
(100, 1536)
```

Comparison with the corresponding stored PermMol features gave:

```text
maximum absolute difference: 0.0
allclose: True
```

The newly generated features were subsequently passed through the provided fold-0 ETBR DNN checkpoint. At a probability threshold of 0.5, 33 of the 100 compounds were classified as active.

## Additional Machine-Learning Models

Scripts for other molecular representations and machine-learning models are available under:

```text
04_Code/training/
```

The study includes molecular representations such as:

- PermMol
- ECFP4
- MACCS
- RDKit fingerprint
- AtomPairs
- PubChem fingerprint

combined with random forest and deep neural network models.

## Data Availability

Processed ETBR datasets, molecular representations, trained models, and supporting computational files are included in this repository.

The complete ultra-large commercial compound library is not redistributed because of its size and source/licensing restrictions.

## Citation

If you use the code, datasets, or trained models in this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**
