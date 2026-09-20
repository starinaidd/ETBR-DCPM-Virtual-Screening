# PermMol-enabled Virtual Screening for ETBR Antagonists

Official repository for the study:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

This study develops a multistage virtual-screening framework for the discovery of endothelin B receptor (ETBR) antagonists. The framework combines molecular representations learned by the small-molecule foundation model **PermMol**, machine-learning activity prediction, energy-based pharmacophore screening, molecular docking, and experimental validation.

PermMol was first benchmarked against conventional molecular representations on molecular-property prediction and virtual-screening tasks. A PermMol-based DNN model was then developed for ETBR activity prediction and applied to an ultra-large commercial compound collection. AI-prioritized molecules were subsequently filtered by pharmacophore screening, hierarchical Glide docking, and expert inspection before experimental validation.

## Results

PermMol was evaluated on:

- 7 MoleculeNet molecular-property prediction datasets
- 17 MUV virtual-screening tasks

For ETBR, six molecular representations were compared using random forest and deep neural network models:

- PermMol
- ECFP4
- MACCS
- PubChem
- RDKFingerprint
- Atom Pairs

The curated ETBR dataset contains 1,803 compounds:

| Dataset | Compounds |
|---|---:|
| Active | 721 |
| Inactive | 1,082 |
| Total | 1,803 |
| Training set | 1,623 |
| Independent test set | 180 |

The PermMol-DNN model achieved the best overall performance on the ETBR test set. The reproduced fold-0 results are:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

The final virtual-screening campaign started from more than 16 million commercially available compounds. Nine compounds were selected for experimental testing, and five showed more than 50% inhibition of ETBR activity at 10 μM.

## Installation

### DNN training and inference

A Conda environment file is provided:

```bash
conda env create -f jkl_environment.yml
conda activate jkl
```

The verified environment includes Python 3.9 and PyTorch 1.13.1.

### PermMol feature extraction

PermMol feature extraction uses a separate MindSpore environment. The workflow was verified with:

```text
Python       3.9.13
PermMol      0.1.0.dev0
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

PermMol produces a 1536-dimensional molecular representation for each input molecule.

## Data and pretrained models

### Benchmark datasets

The repository contains the datasets used for the molecular-representation benchmarks:

```text
01_ML_Datasets/MoleculeNet/
01_ML_Datasets/MUV/
```

MoleculeNet includes the seven tasks evaluated in the study:

```text
BACE
BBBP
HIV
ClinTox
SIDER
Tox21
ToxCast
```

The MUV directory contains the 17 virtual-screening benchmark tasks.

### ETBR dataset

The processed ETBR train/test split is provided in:

```text
01_ML_Datasets/ETBR_split/
```

PermMol representations are provided in:

```text
01_ML_Datasets/ETBR_PermMol_features/
```

The main files are:

```text
ETB_train.csv
ETB_test.csv

ETB_train_permmol.pkl
ETB_test_permmol.pkl
```

The PermMol feature matrices have dimensions:

```text
ETB_train_permmol.pkl   (1623, 1536)
ETB_test_permmol.pkl     (180, 1536)
```

Rows in each PermMol feature file correspond directly to the molecular order in the associated CSV file.

### Pretrained models

ETBR models are provided in:

```text
02_Trained_Models/ETBR_models/
```

The five PermMol-DNN checkpoints are located in:

```text
02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/
```

```text
model_fold_0.pth
model_fold_1.pth
model_fold_2.pth
model_fold_3.pth
model_fold_4.pth
```

Training logs are provided in:

```text
02_Trained_Models/ETBR_logs/
```

## Usage

### PermMol feature extraction

PermMol features can be generated with the provided feature-extraction script:

```text
04_Code/PermMol/extract_feat.py
```

Set the input and output directories in the script and run:

```bash
python 04_Code/PermMol/extract_feat.py
```

The extraction settings used in this study are:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

For an input file containing `N` molecules, the generated feature matrix has shape:

```text
(N, 1536)
```

### ETBR screening with the pretrained PermMol-DNN

The screening script is:

```text
04_Code/screening/ml_screener_dnn.py
```

The CSV file and its PermMol feature file must have the same basename and contain molecules in the same order, for example:

```text
demo_100.csv
demo_100.pkl
```

Run the pretrained ETBR model with:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file reproduction_demo/demo_100.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir reproduction_demo
```

The fold-0 PermMol-DNN architecture is:

```text
1536 → 64 → 128 → 64 → 1
```

The model output is converted to an activity probability using a sigmoid function. With `--prop 0.5`, compounds with predicted probability ≥ 0.5 are retained.

### Reproduction example

A small inference example is included in:

```text
reproduction_demo/
```

The first 100 molecules of the ETBR test set were independently processed with PermMol.

The regenerated feature matrix had shape:

```text
(100, 1536)
```

and was identical to the corresponding stored PermMol representations:

```text
maximum absolute difference = 0.0
allclose = True
```

Using the regenerated features with `model_fold_0.pth` and a threshold of 0.5 gives:

```text
100 molecules screened
33 molecules predicted as active
```

This example verifies the complete inference path from PermMol representation generation to ETBR activity prediction.

## Model training

Training scripts for the molecular representations and machine-learning models evaluated in the study are provided in:

```text
04_Code/training/
```

The repository contains RF and DNN implementations for the molecular representations evaluated in the benchmark and ETBR experiments.

The pretrained checkpoints can be used directly for reproducing the reported ETBR predictions; retraining is not required for inference.

## Pharmacophore and docking

Files associated with the structure-based stage of the screening campaign are provided in:

```text
03_Pharmacophore/
05_Docking_and_Candidates/
```

The energy-based pharmacophore model was generated from the ETBR–Bosentan complex (PDB ID **5XPR**). Pharmacophore validation was performed using 40 known active compounds and 1,893 decoys.

Compounds retained after pharmacophore screening were subjected to hierarchical Glide docking:

```text
HTVS → SP → XP
```

followed by expert inspection of the predicted ETBR binding modes.

These stages were performed with Schrödinger software and require an appropriate Schrödinger installation and license for independent reproduction.

## Data availability

This repository provides the processed benchmark datasets, ETBR dataset, molecular representations, trained models, training and screening scripts, pharmacophore files, docking results, and candidate-compound files associated with the study.

The complete commercial screening libraries are not redistributed because of their size and source/licensing restrictions.

## Citation

If this repository is useful for your research, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

Citation information will be updated after publication.
