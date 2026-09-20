# ETBR-PermMol Virtual Screening

This repository accompanies the study:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

We developed a PermMol-enabled multistage virtual-screening strategy for the discovery of endothelin B receptor (ETBR) antagonists. PermMol was first evaluated on molecular-property prediction and virtual-screening benchmarks, and was subsequently combined with a deep neural network for ETBR activity prediction. The resulting model was applied to an ultra-large commercial compound collection, followed by energy-based pharmacophore screening, hierarchical molecular docking, expert inspection, and experimental validation.

PermMol+DNN achieved an AUC-ROC of 0.988 and an MCC of 0.861 on the independent ETBR test set. The complete screening campaign was applied to more than 16 million commercially available compounds and yielded nine compounds for experimental evaluation, five of which showed more than 50% inhibition of ETBR activity at 10 μM.

## Installation

### DNN environment

The environment used for model training and inference is provided in:

```text
jkl_environment.yml
```

Create the environment with:

```bash
conda env create -f jkl_environment.yml
conda activate jkl
```

### PermMol environment

PermMol feature extraction requires a MindSpore environment. The verified setup used:

```text
Python 3.9.13
PermMol 0.1.0.dev0
MindSpore 2.0.0a0
NumPy 1.21.6
pandas 1.3.4
RDKit 2023.03.1
wget 3.2
```

## Data and models

The repository contains the datasets, molecular representations, trained models, and screening files used in the study.

| Data | Description |
|---|---|
| MoleculeNet | Seven molecular-property prediction benchmarks |
| MUV | Seventeen virtual-screening benchmark tasks |
| ETBR | 1,803 compounds: 721 active and 1,082 inactive |
| ETBR split | 1,623 training compounds and 180 independent test compounds |
| PermMol features | 1,536-dimensional molecular representations |
| Trained models | RF and DNN models for the molecular representations evaluated in the study |

For ETBR, six molecular representations were evaluated:

- PermMol
- ECFP4
- MACCS
- PubChem
- RDKFingerprint
- Atom Pairs

The pretrained PermMol-DNN models used for ETBR prediction are included in the repository.

## Reproducing the ETBR prediction model

The provided ETBR test set, PermMol representations, and pretrained fold-0 model reproduce the following results:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

The fold-0 DNN has the architecture:

```text
1536 → 64 → 128 → 64 → 1
```

with a dropout ratio of `0.20112391936365895`.

## Screening with the pretrained ETBR model

PermMol converts each molecule into a 1,536-dimensional representation. The screening script reads these representations and applies the pretrained ETBR DNN.

The input CSV and PermMol feature file should have the same basename, for example:

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

The model output is transformed with a sigmoid function, and compounds with predicted probability ≥ 0.5 are retained.

A 100-molecule reproduction example is included. Independently regenerated PermMol features were identical to the corresponding stored features:

```text
shape = (100, 1536)
maximum absolute difference = 0.0
allclose = True
```

Using these regenerated representations with the pretrained fold-0 model, 33 of the 100 molecules were classified as active at a threshold of 0.5.

## PermMol feature extraction

PermMol features can be generated using the provided feature-extraction script.

The settings used in this study were:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

The generated feature matrix can then be used directly as input to the ETBR DNN screening script.

## Benchmarking and model training

Training scripts for the MoleculeNet, MUV, and ETBR experiments are included in the repository.

The benchmark experiments compare conventional molecular fingerprints with PermMol representations using random forest and deep neural network classifiers.

The pretrained models can be used directly for reproducing the reported prediction results; retraining is not required for inference.

## Structure-based virtual screening

Following AI-based prioritization, compounds were further evaluated using an energy-based pharmacophore model derived from the ETBR–Bosentan complex (PDB ID: 5XPR), followed by hierarchical Glide docking and expert inspection.

The pharmacophore and docking files used in these stages are included in the repository. Reproduction of these stages requires Schrödinger software and an appropriate license.

The complete commercial screening libraries are not redistributed because of their size and source/licensing restrictions.

## Citation

If you use the code, datasets, molecular representations, or trained models from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

Citation details will be updated after publication.
