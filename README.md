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

The computational workflow includes molecular-representation benchmarking, ETBR activity modeling, PermMol-based virtual screening, pharmacophore screening, and molecular docking.

### Molecular-representation benchmarking

PermMol was evaluated together with ECFP4, MACCS, PubChem, RDKFingerprint, and Atom Pairs using random forest (RF) and deep neural network (DNN) models.

Seven MoleculeNet datasets were used for molecular-property prediction, and 17 MUV tasks were used for virtual-screening evaluation. The corresponding datasets, molecular representations, training scripts, trained models, and evaluation results are included in the repository.

### ETBR activity modeling

The six molecular representations were further evaluated on the curated ETBR dataset containing 721 active and 1,082 inactive compounds.

The dataset was divided into 1,623 training compounds and 180 independent test compounds. Five-fold RF and DNN models were trained for each molecular representation.

PermMol+DNN showed the best overall performance on the ETBR test set, achieving:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988 |
| Sensitivity | 0.889 |
| Specificity | 0.963 |
| Accuracy | 0.933 |
| MCC | 0.861 |

The trained ETBR models are provided for downstream prediction and virtual screening.

### PermMol feature extraction

PermMol converts molecular SMILES into 1,536-dimensional molecular representations.

Feature extraction can be performed using:

```bash
python 04_Code/PermMol/extract_feat.py
```

The settings used in this study are:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

### ETBR virtual screening

The pretrained PermMol-DNN checkpoints can be applied to compound libraries using the screening script. Specify the checkpoint to be used with `--models`.

Example using the fold-0 checkpoint:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file path/to/input.csv \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --out_dir path/to/output
```
PermMol representations are used as model input, and compounds with predicted probabilities above the specified threshold are retained for subsequent screening.

The same implementation can be used for batch screening of large compound collections.

### Pharmacophore screening

Compounds prioritized by the PermMol-DNN model were further screened using an energy-based pharmacophore model derived from the human ETBR–Bosentan complex (PDB ID: **5XPR**).

The final pharmacophore model contains seven features:

```text
A D N R R R R
```

The model was validated using 40 known active compounds and 1,893 decoys. Molecules matching at least five pharmacophore features were retained for molecular docking.

The pharmacophore model and associated screening files are included in the repository.


## Data availability

The repository provides the processed benchmark datasets, ETBR dataset, molecular representations, trained models, training and screening code, pharmacophore files, docking results, and candidate-compound files associated with the study.


## Citation

If you use the datasets, molecular representations, trained models, or code from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

Citation details will be updated after publication.
