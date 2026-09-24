# ETBR-DCPM Virtual Screening

Code, data, trained models, and structure-based screening resources associated with the study:

**Discovery of novel endothelin B receptor antagonists through DCPM-enabled multistage virtual screening of ultra-large commercial libraries**

## Overview

This repository provides the computational resources used to develop and evaluate a multistage virtual-screening workflow for the discovery of novel endothelin B receptor (ETBR) antagonists.

The workflow integrates:

- **DCPM**, an in-house small-molecule foundation model for molecular representation
- Random forest (RF) and deep neural network (DNN) classifiers
- Ultra-large commercial-library screening
- Energy-based pharmacophore screening
- Hierarchical molecular docking with Glide
- Expert inspection of receptor–ligand interactions
- Experimental validation using a FLIPR calcium mobilization assay

DCPM generates a fixed-length **1 × 1536 molecular embedding** from standardized SMILES. These representations are used as input features for downstream molecular-property prediction, ETBR activity classification, and virtual screening.

The representation capability of DCPM was evaluated on **7 MoleculeNet datasets** and **17 MUV virtual-screening tasks**. DCPM achieved the best performance on 3 of the 7 MoleculeNet tasks, while DCPM combined with DNN achieved the best performance on 5 of the 17 MUV tasks.

For ETBR activity prediction, the DCPM+DNN model achieved an AUC-ROC of **0.988** on the independent test set.

The final multistage workflow reduced more than 16 million commercially available compounds to nine compounds for experimental evaluation.

## Study workflow

```text
MoleculeNet / MUV benchmark evaluation
                  ↓
          DCPM representation
              (1536-d)
                  ↓
          RF / DNN classifiers
                  ↓
       ETBR activity prediction
                  ↓
     >16 million commercial compounds
                  ↓
             DCPM + DNN
                  ↓
          173,435 compounds
                  ↓
       e-Pharmacophore screening
                  ↓
           25,751 compounds
                  ↓
        Glide HTVS → SP → XP
                  ↓
             928 compounds
                  ↓
          Expert inspection
                  ↓
             20 candidates
                  ↓
      Commercial availability
                  ↓
       9 experimental compounds
                  ↓
        FLIPR functional assay
```

## Installation

### Machine-learning environment

The PyTorch/scikit-learn environment used for model training, evaluation, and downstream screening is provided in `environment.yml`.

```bash
conda env create -f environment.yml
conda activate etbr-dnn
```

### DCPM feature-extraction environment

DCPM feature extraction requires the provided model package and a compatible MindSpore environment.

The verified feature-extraction environment used during reproducibility testing included:

```text
Python       3.9.13
MindSpore    2.0.0a0
NumPy        1.21.6
pandas       1.3.4
RDKit        2023.03.1
wget         3.2
```

The DCPM implementation distributed with this repository retains the historical Python package name `permmol` for compatibility with the original computational environment.

Install the provided wheel without modifying the existing MindSpore dependency stack:

```bash
pip install --no-deps 04_Code/PermMol/permmol-0.1.0.dev0-py3-none-any.whl
pip install wget==3.2
```

The original verified feature-extraction environment used Huawei Ascend/CANN. Other MindSpore-compatible hardware configurations may require environment-specific setup.

## Data and models

| Resource | Description |
|---|---|
| ETBR dataset | 1,803 compounds: 721 active and 1,082 inactive |
| ETBR split | 1,623 training compounds and 180 independent test compounds |
| DCPM representations | 1,536-dimensional molecular embeddings |
| MoleculeNet | BACE, BBBP, HIV, ClinTox, SIDER, Tox21, and ToxCast |
| MUV | 17 highly imbalanced virtual-screening benchmark tasks |
| Molecular representations | DCPM, ECFP4, MACCS, PubChem, RDKFingerprint, and Atom Pairs |
| Prediction models | RF and DNN classifiers |
| ETBR models | Trained checkpoints for six molecular representations with RF/DNN |
| Pharmacophore | 5XPR–Bosentan e-pharmacophore model and validation data |
| Docking | Glide docking results and expert-selected candidates |
| Candidate compounds | Structures and binding-mode files for prioritized ETBR antagonists |

### ETBR dataset

ETBR activity data were collected from ChEMBL and BindingDB using IC50 as the primary activity endpoint.

Activity labels were defined as:

```text
IC50 < 1,000 nM       Active
IC50 > 10,000 nM      Inactive
1,000–10,000 nM       Excluded
```

After data cleaning, standardization, deduplication, and supplementation of inactive compounds, the final dataset contained:

```text
Active:       721
Inactive:   1,082
Total:      1,803
```

The dataset was divided using stratified sampling:

```text
Training set: 1,623
Test set:       180
```

### ETBR model performance

Six molecular representations were evaluated with RF and DNN classifiers.

The DCPM+DNN model was selected for large-scale ETBR virtual screening.

Performance on the ETBR test set:

| Metric | Value |
|---|---:|
| AUC-ROC | 0.988 |
| Sensitivity | 0.889 |
| Specificity | 0.963 |
| Accuracy | 0.933 |
| MCC | 0.861 |

## Usage

### 1. DCPM molecular representation

DCPM converts standardized SMILES into 1,536-dimensional molecular embeddings.

The feature-extraction script is:

```text
04_Code/PermMol/extract_feat.py
```

The input CSV files must contain a column named:

```text
smiles
```

The script processes CSV files under `./csv/` and writes same-basename pickle feature files to `./sar/feats/`.

Example:

```bash
mkdir -p dcpm_feature_run/csv
mkdir -p dcpm_feature_run/sar/feats

cp input.csv dcpm_feature_run/csv/

cd dcpm_feature_run
python ../04_Code/PermMol/extract_feat.py
```

The resulting feature matrix has shape:

```text
N × 1536
```

where `N` is the number of molecules.

The pretrained DCPM parameters required for inference are initialized through the DCPM/legacy `permmol` API.

### 2. MoleculeNet benchmark

Seven MoleculeNet classification datasets are provided:

```text
BACE
BBBP
HIV
ClinTox
SIDER
Tox21
ToxCast
```

These datasets were used to compare DCPM with five conventional molecular representations:

```text
ECFP4
MACCS
PubChem
RDKFingerprint
Atom Pairs
```

RF and DNN classifiers were evaluated for molecular-property prediction.

DCPM achieved the best performance on **BBBP, ClinTox, and ToxCast**, corresponding to 3 of the 7 benchmark tasks.

Training scripts for the different representations and classifiers are provided under `04_Code/training/`.

### 3. MUV virtual-screening benchmark

The repository contains all **17 MUV tasks** used to evaluate molecular representations under highly imbalanced virtual-screening conditions.

DCPM representations were evaluated using both RF and DNN classifiers together with the five conventional molecular representations.

The DCPM+DNN combination achieved the best AUC-ROC performance on **5 of the 17 MUV tasks**.

The benchmark datasets, molecular representations, historical trained checkpoints, and evaluation logs are provided with the repository.

### 4. ETBR activity modeling

The ETBR dataset was evaluated using six molecular representations with RF and DNN classifiers.

RF hyperparameters were optimized using the Tree-structured Parzen Estimator implemented in Hyperopt.

The DNN consists of three fully connected hidden layers with ReLU activation and dropout regularization. Learning rate, dropout rate, and hidden-layer dimensions were optimized using Hyperopt.

Five-fold cross-validation was used during model development.

The DCPM+DNN combination was selected as the primary ETBR prediction model for subsequent large-library screening.

DCPM-related historical scripts and model directories may retain `permmol` in their filenames. These names are preserved to maintain compatibility with the original training and inference workflow.

### 5. ETBR virtual screening

The initial commercial screening library contained more than **16 million compounds** collected from ChemDiv, Specs, and TopScience.

All compounds were standardized and deduplicated before DCPM representation generation.

The DCPM+DNN classifier was applied using a probability threshold of:

```text
P(active) > 0.5
```

This stage retained:

```text
173,435 compounds
```

The screening scripts are provided under:

```text
04_Code/screening/
```

A DNN screening run can be invoked with:

```bash
python 04_Code/screening/ml_screener_dnn.py \
    --file <input_file> \
    --models <DCPM_DNN_checkpoint> \
    --prop 0.5 \
    --smiles_col smiles \
    --out_dir <output_directory>
```

The model architecture and input representation used by the screening script must match the selected checkpoint. For DCPM-based ETBR screening, the model input dimension is **1536**.

The repository contains five ETBR DNN checkpoints generated during model development. A specific checkpoint can be supplied through `--models`; for example, `model_fold_0.pth` can be used for a single-checkpoint screening run.

### 6. e-Pharmacophore screening

The energy-based pharmacophore model was constructed from the human ETBR–Bosentan complex:

```text
PDB ID:       5XPR
Ligand:       Bosentan
Resolution:   3.60 Å
```

The selected pharmacophore contains seven features:

```text
A D N R R R R
```

corresponding to one hydrogen-bond acceptor, one hydrogen-bond donor, one negative-charge feature, and four aromatic-ring features.

The validation dataset contains:

```text
40 active compounds
1,893 decoys
```

Compounds matching at least **5 of the 7 pharmacophore features** were retained.

The validated 5-of-7 model achieved:

```text
EF1%    = 10.17
BEDROC  = 0.23
AUAC    = 0.55
```

Application of the pharmacophore filter reduced the DCPM+DNN candidates from 173,435 to:

```text
25,751 compounds
```

### 7. Molecular docking

Structure-based screening was performed using Schrödinger Glide with a hierarchical protocol:

```text
HTVS
 ↓ retain 50%
SP
 ↓ retain 40%
XP
 ↓ retain 20%
```

Following docking and XP-score-based prioritization, **928 compounds** were retained for further inspection.

Expert inspection focused on interactions with key ETBR residues including:

```text
Asp154
Lys182
Phe240
Lys273
His340
Arg343
```

Hydrogen bonding, ionic interactions, π–π stacking, and overall binding-mode compatibility were considered during prioritization.

Twenty compounds were retained after expert inspection, and nine commercially available compounds were selected for experimental testing.

Schrödinger Maestro/Glide is proprietary software and is not distributed with this repository.

## Experimental validation

Nine selected compounds were evaluated using a FLIPR calcium mobilization assay in cells expressing human ETBR.

Five compounds showed more than 50% inhibition of ET-1-induced calcium signaling at 10 μM:

```text
C1
C2
C7
C8
C9
```

This corresponds to an experimental hit rate of:

```text
55.6%
```

Concentration–response measurements yielded:

| Compound | IC50 (μM) |
|---|---:|
| C1 | 3.67 |
| C2 | 16.06 |
| C7 | 36.28 |
| C8 | **0.66** |
| C9 | 2.78 |
| BQ-788 | 0.0625 |

C8 showed the strongest activity among the newly identified compounds, reaching submicromolar potency with an IC50 of **0.66 μM**.

## Naming convention

The molecular foundation model is referred to as **DCPM** in the publication and throughout the scientific description of this repository.

Some archived implementation files retain the earlier internal name **PermMol**, including:

```text
permmol-0.1.0.dev0-py3-none-any.whl
Python import: permmol
*_permmol.py
*_permmol.pkl
historical model/checkpoint directories
```

These legacy names are intentionally preserved to maintain compatibility with the original computational workflow and trained model artifacts. They refer to the same model implementation used under the publication name DCPM.

## Data availability

This repository provides the curated ETBR datasets, benchmark datasets, molecular representations, trained model checkpoints, evaluation logs, DCPM feature-extraction resources, pharmacophore files, docking results, candidate-compound files, and analysis scripts used in the study.

The complete >16-million-compound commercial screening libraries from ChemDiv, Specs, and TopScience are **not redistributed** because of their size and source/licensing restrictions.

Large intermediate files that can be regenerated from the supplied data and code may also be omitted.

The DCPM distribution included here consists of the feature-extraction interface and the legacy installation wheel required for representation generation; it should not be interpreted as a complete source-code release of the underlying foundation model.

## Citation

If you use the data, models, or workflow provided in this repository, please cite:

```text
Citation information will be added upon publication.
```

## License

License information will be added according to the final release policy for the publication repository.
