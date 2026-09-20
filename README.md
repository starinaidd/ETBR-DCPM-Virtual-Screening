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

The computational part of the study includes molecular-representation benchmarking, ETBR model development, PermMol-based compound screening, pharmacophore screening, and molecular docking.

### Molecular-representation benchmarking and model training

PermMol and five conventional molecular representations were evaluated on seven MoleculeNet datasets and 17 MUV virtual-screening tasks.

Training scripts for the RF and DNN models are provided in `04_Code/training/`. The scripts perform data loading, five-fold model training, evaluation, and checkpoint saving for the corresponding molecular representation.

For example, the PermMol DNN model can be trained with:

```bash
python 04_Code/training/dnn_permmol.py
```

and the corresponding random forest model with:

```bash
python 04_Code/training/rf_permmol.py
```

Equivalent training scripts are provided for the other molecular representations.

The same modeling framework was used for the ETBR activity-prediction experiments. For PermMol, each molecule is represented by a 1,536-dimensional embedding, and five-fold models were trained on the ETBR training set and evaluated on the independent test set.

Pretrained models are included in the repository, so retraining is not required for downstream virtual screening.

### PermMol feature extraction

PermMol embeddings are generated from molecular SMILES using `extract_feat.py`.

The extraction settings used in this study are:

```text
max_len = 301
batch_size = 256
feature dimension = 1536
```

Set the input CSV directory and output feature directory in `extract_feat.py`:

```python
csv_dir = "./csv"
save_dir = "./sar/feats"
```

and run:

```bash
python extract_feat.py
```

The script processes the CSV files in the input directory and saves the corresponding PermMol representations as `.pkl` files.

For an input containing `N` molecules, the generated feature matrix has shape:

```text
(N, 1536)
```

The molecular order in the feature matrix is preserved and must remain consistent with the corresponding input CSV file.

### Screening with the pretrained ETBR model

The pretrained PermMol-DNN model can be used to screen molecules with precomputed PermMol representations.

For each CSV file, the corresponding PermMol feature file must have the same basename and contain molecules in the same order:

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

The fold-0 PermMol-DNN model has the architecture:

```text
1536 → 64 → 128 → 64 → 1
```

The model output is converted to an activity probability using a sigmoid function. With `--prop 0.5`, compounds with predicted probability greater than or equal to 0.5 are retained.

The screening script also supports directory input for parallel processing of multiple compound-library files:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file path/to/library_directory \
    --models 02_Trained_Models/ETBR_models/ETB_model/etb_dnn_permmol/model_fold_0.pth \
    --prop 0.5 \
    --cpus 32 \
    --out_dir path/to/output
```

This model was used for the AI-based prioritization stage of the ultra-large commercial compound screening campaign.

### Energy-based pharmacophore screening

Compounds retained by the AI model were subsequently screened using an energy-based pharmacophore model derived from the human ETBR–Bosentan complex (PDB ID: **5XPR**).

The final pharmacophore model contains seven features:

```text
A D N R R R R
```

corresponding to one hydrogen-bond acceptor, one hydrogen-bond donor, one negative ionizable feature, and four aromatic features.

The pharmacophore model was validated using 40 known active compounds and 1,893 decoys. Molecules matching at least five pharmacophore features were retained for subsequent structure-based docking.

The pharmacophore model and validation files used in the study are included in the repository. Reproduction of this stage requires Schrödinger Phase.

### Molecular docking

Pharmacophore-selected compounds were prepared with Schrödinger LigPrep and docked to ETBR using Glide.

A hierarchical docking protocol was used:

```text
HTVS → retain 50%
SP   → retain 40%
XP   → retain 20%
```

The resulting XP poses were further evaluated according to docking score, binding geometry, and interactions with key residues in the ETBR binding pocket.

This stage reduced the pharmacophore-selected compounds to 928 docked candidates. Expert inspection of the predicted binding modes was then used to prioritize 20 compounds, from which nine commercially available compounds were selected for experimental testing.

The pharmacophore, docking, and candidate-selection files required to inspect these results are included in the repository. Reproduction of the docking stage requires an appropriate Schrödinger installation and license.

## Reproducibility

### ETBR prediction

Using the provided ETBR test set, PermMol representations, and pretrained fold-0 model, the following results were reproduced:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988683 |
| Sensitivity | 0.888889 |
| Specificity | 0.962963 |
| Accuracy | 0.933333 |
| MCC | 0.860753 |

The fold-0 model uses a dropout ratio of:

```text
0.20112391936365895
```

### PermMol feature generation

PermMol features were independently regenerated for the first 100 compounds of the ETBR test set.

The regenerated feature matrix had shape:

```text
(100, 1536)
```

Comparison with the corresponding stored PermMol representations gave:

```text
maximum absolute difference = 0.0
allclose = True
```

This confirms exact agreement between the independently generated and stored PermMol representations for the tested molecules.

### End-to-end screening

The regenerated 100-molecule PermMol feature set was subsequently passed through the pretrained fold-0 ETBR DNN model.

At a probability threshold of 0.5:

```text
100 molecules screened
33 molecules predicted as active
```

This verifies the complete computational path from PermMol feature generation to ETBR activity prediction.

## Experimental validation

The complete multistage virtual-screening campaign was applied to more than 16 million commercially available compounds.

The major screening stages reduced the chemical library to:

| Stage | Compounds |
|---|---:|
| Initial commercial libraries | >16 million |
| PermMol-DNN screening | 173,435 |
| Pharmacophore screening | 25,751 |
| Glide docking | 928 |
| Expert inspection | 20 |
| Experimental candidates | 9 |

Nine commercially available compounds were evaluated using an ETBR FLIPR calcium-mobilization assay.

Five compounds — C1, C2, C7, C8, and C9 — showed more than 50% inhibition at 10 μM and were subsequently evaluated in concentration-response experiments.

| Compound | IC50 |
|---|---:|
| C1 | 3.67 μM |
| C2 | 16.06 μM |
| C7 | 36.28 μM |
| C8 | 0.66 μM |
| C9 | 2.78 μM |

C8 showed the strongest activity among the newly identified compounds.

Experimental procedures and complete biological results are described in the accompanying manuscript.

## Data availability

The repository provides the processed benchmark datasets, ETBR dataset, molecular representations, trained models, training and screening code, pharmacophore files, docking results, and candidate-compound files associated with the study.

The complete commercial compound libraries used for the ultra-large screening campaign are not redistributed because of their size and source/licensing restrictions.

## Citation

If you use the datasets, molecular representations, trained models, or code from this repository, please cite:

**Discovery of novel endothelin B receptor antagonists through PermMol-enabled multistage virtual screening of ultra-large commercial libraries**

Citation details will be updated after publication.
