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
Python       3.9.13
PermMol      0.1.0.dev0
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

## Data and models

The repository contains the datasets, molecular representations, trained models, and screening files used in the study.

| Data | Description |
|---|---|
| MoleculeNet | Seven molecular-property prediction benchmark datasets |
| MUV | Seventeen virtual-screening benchmark tasks |
| ETBR | 1,803 compounds: 721 active and 1,082 inactive |
| ETBR split | 1,623 training compounds and 180 independent test compounds |
| PermMol features | 1,536-dimensional molecular representations |
| Trained models | RF and DNN models for the molecular representations evaluated in the study |

Six molecular representations were evaluated:

- PermMol
- ECFP4
- MACCS
- PubChem
- RDKFingerprint
- Atom Pairs

Random forest (RF) and deep neural network (DNN) models were used for molecular-property prediction and virtual-screening experiments. Pretrained ETBR models and the corresponding evaluation results are included in the repository.

## Usage

The computational workflow consists of molecular-representation benchmarking, ETBR activity modeling, PermMol-based virtual screening, and structure-based screening.

### Molecular-representation benchmarking

PermMol was benchmarked against five conventional molecular representations — ECFP4, MACCS, PubChem, RDKFingerprint, and Atom Pairs — on seven MoleculeNet molecular-property prediction datasets and 17 MUV virtual-screening tasks.

Random forest (RF) and deep neural network (DNN) models were used to evaluate the different molecular representations. The training code includes five-fold cross-validation, model evaluation, checkpoint saving, and the task-specific settings used in the study.

The corresponding benchmark datasets, molecular representations, trained models, and evaluation logs are provided in the repository.

### ETBR activity modeling

The same RF/DNN framework was applied to the curated ETBR dataset to compare the six molecular representations.

The final ETBR dataset contains 1,803 compounds, with 1,623 compounds used for training and 180 compounds retained as an independent test set.

PermMol+DNN showed the best overall performance among the evaluated representation/model combinations. For PermMol, each molecule is represented by a 1,536-dimensional embedding. Five-fold trained ETBR models are provided and can be used directly for downstream prediction and virtual screening.

The reproduced fold-0 performance on the independent ETBR test set is:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

### PermMol feature extraction

PermMol molecular representations can be generated with the provided feature-extraction script:

```bash
python 04_Code/PermMol/extract_feat.py
```

The settings used in this study were:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

A reproducibility test on the first 100 compounds of the ETBR test set generated a `(100, 1536)` feature matrix that was identical to the corresponding stored PermMol representations:

```text
maximum absolute difference = 0.0
allclose = True
```

### ETBR virtual screening

The pretrained PermMol-DNN model can be applied directly to compound libraries using the screening script:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file reproduction_demo/demo_100.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir reproduction_demo
```

The fold-0 network has the architecture:

```text
1536 → 64 → 128 → 64 → 1
```

A sigmoid transformation is applied to the model output, and compounds with a predicted probability greater than or equal to the selected threshold are retained.

For the supplied 100-molecule reproduction example:

```text
100 molecules screened
33 molecules predicted as active
threshold = 0.5
```

The same screening implementation supports batch processing of large compound collections and was used for the AI-based prioritization stage of the ultra-large virtual-screening campaign.

### Structure-based virtual screening

Compounds prioritized by the PermMol-DNN model were subsequently subjected to energy-based pharmacophore screening and hierarchical molecular docking.

The pharmacophore model was derived from the human ETBR–Bosentan complex (PDB ID: **5XPR**) and contains seven features:

```text
A D N R R R R
```

The model was validated using 40 known active compounds and 1,893 decoys, and compounds matching at least five pharmacophore features were retained.

The remaining compounds were processed using Schrödinger LigPrep and screened with Glide using a hierarchical protocol:

```text
HTVS → SP → XP
```

with retention rates of 50%, 40%, and 20%, respectively.

Docking poses were subsequently inspected according to docking score, binding geometry, and key ETBR interactions. The associated pharmacophore, docking, and candidate-selection files are included in the repository.

Reproduction of the structure-based screening stages requires Schrödinger Phase, Glide, and an appropriate Schrödinger license.
## Data availability

The repository provides the processed benchmark datasets, ETBR dataset, molecular representations, trained models, training and screening code, pharmacophore files, docking results, and candidate-compound files associated with the study.

The complete commercial compound libraries used for the ultra-large screening campaign are not redistributed because of their size and source/licensing restrictions.

## Citation

If you use the datasets, molecular representations, trained models, or code from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

Citation details will be updated after publication.
