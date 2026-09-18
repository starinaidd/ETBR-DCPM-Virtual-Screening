from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from sklearn.metrics import roc_auc_score
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import os
from data_utils import Meter, Log, smiles_to_pubchem


from sklearn.model_selection import KFold
import pickle
from rdkit import rdBase


def train_rf(train_dataset, valid_dataset, test_dataset, fold):

    para_dict = {
        "n_estimators_ls": [10, 50, 100, 200, 300, 400, 500],
        "max_depth_ls": range(3, 12),
        "min_samples_leaf_ls": [1, 3, 5, 10, 20, 50],
        "max_features_ls": ["sqrt", "log2", 0.7, 0.8, 0.9],
    }

    space_ = {
        "n_estimators": hp.choice("n_estimators", para_dict["n_estimators_ls"]),
        "max_depth": hp.choice("max_depth", para_dict["max_depth_ls"]),
        "min_samples_leaf": hp.choice(
            "min_samples_leaf", para_dict["min_samples_leaf_ls"]
        ),
        "min_impurity_decrease": hp.uniform("min_impurity_decrease", 0, 0.01),
        "max_features": hp.choice("max_features", para_dict["max_features_ls"]),
    }

    trials = Trials()

    train_dataset_c = train_dataset.copy()
    train_dataset_c['smiles'] = train_dataset_c['smiles'].apply(smiles_to_pubchem)
    data_tr_x = np.concatenate(train_dataset_c['smiles'].tolist(), axis=0)
    data_tr_y = np.array(train_dataset_c["activity"].tolist())

    valid_dataset_c = valid_dataset.copy()
    valid_dataset_c['smiles'] = valid_dataset_c['smiles'].apply(smiles_to_pubchem)
    data_va_x = np.concatenate(valid_dataset_c['smiles'].tolist(), axis=0)
    data_va_y = np.array(valid_dataset_c["activity"].tolist())

    test_dataset_c = test_dataset.copy()
    test_dataset_c['smiles'] = test_dataset_c['smiles'].apply(smiles_to_pubchem)
    data_te_x = np.concatenate(test_dataset_c['smiles'].tolist(), axis=0)
    data_te_y = np.array(test_dataset_c["activity"].tolist())

    def hyper_opt(kwargs):
        model = RandomForestClassifier(
            **kwargs, n_jobs=10, random_state=1, verbose=0, class_weight="balanced"
        )
        model.fit(data_tr_x, data_tr_y)
        val_preds = model.predict_proba(data_va_x)
        loss = 1 - roc_auc_score(data_va_y, val_preds[:, 1])
        return {"loss": loss, "status": STATUS_OK}

    best_results = fmin(
        hyper_opt,
        space_,
        algo=tpe.suggest,
        max_evals=50,
        trials=trials,
        show_progressbar=False,
    )
    logger.info(
        f"the best hyper-parameters for are {best_results}"
    )  # log the best params
    best_model = RandomForestClassifier(
        n_estimators=para_dict["n_estimators_ls"][best_results["n_estimators"]],
        max_depth=para_dict["max_depth_ls"][best_results["max_depth"]],
        min_samples_leaf=para_dict["min_samples_leaf_ls"][
            best_results["min_samples_leaf"]
        ],
        max_features=para_dict["max_features_ls"][best_results["max_features"]],
        min_impurity_decrease=best_results["min_impurity_decrease"],
        n_jobs=6,
        random_state=1,
        verbose=0,
        class_weight="balanced",
    )
    best_model.fit(data_tr_x, data_tr_y)

    with open(f"./etb_ckpt/etb_rf_pubchem/model_fold_{fold}.pth", "wb") as f:
        pickle.dump(best_model, f)

    va_pred = best_model.predict_proba(data_va_x)
    va_pred = np.expand_dims(va_pred[:, 1], -1)
    valid_meter = Meter()
    valid_meter.update(va_pred, data_va_y.reshape(-1, 1))
    va_results = valid_meter.compute_metric(
        "classification", ["se", "sp", "pre", "acc", "mcc", "f1", "auc_roc", "auc_prc"]
    )
    logger.info(va_results)

    te_pred = best_model.predict_proba(data_te_x)
    te_pred = np.expand_dims(te_pred[:, 1], -1)
    test_meter = Meter()
    test_meter.update(te_pred, data_te_y.reshape(-1, 1))
    te_results = test_meter.compute_metric(
        "classification", ["se", "sp", "pre", "acc", "mcc", "f1", "auc_roc", "auc_prc"]
    )
    logger.info(te_results)


if __name__ == "__main__":
    rdBase.DisableLog("rdApp.*")

    #train_fp = pickle.load(open('./data/ETB_train.pkl', 'rb')).tolist()
    # train_fp = pickle.load(open('./data/EP4_train.pkl'), 'rb').tolist()
    #train_activity = pd.read_csv('./data/ETB_train.csv')['activity']
    #df = pd.DataFrame({'fp': train_fp, 'activity': train_activity})

    #test_fp = pickle.load(open('./data/ETB_test.pkl', 'rb')).tolist()
    #test_activity = pd.read_csv("./data/ETB_test.csv")['activity']
    #test_datas = pd.DataFrame({'fp': test_fp, 'activity': test_activity})

    df = pd.read_csv('./data/ETB_train_new.csv')
    test_datas = pd.read_csv('./data/ETB_test_new.csv')
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    logger = Log("train", f"./logs/etb_rf_pubchem.log")

    for fold, (train_index, valid_index) in enumerate(kf.split(df)):
        train_datas = df.iloc[train_index]
        valid_datas = df.iloc[valid_index]

        logger.info(f"now is fold {fold}")

        train_rf(train_datas, valid_datas, test_datas, fold=fold)