import os
import pandas as pd
import numpy as np
from rdkit.Chem import AllChem
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, roc_auc_score, precision_recall_curve, auc


def saltremover(i):
    l = i.split('.')
    d = {len(a):a for a in l }
    smile = d[max(d.keys())]
    return smile
def stand_smiles(smiles):
    try:
        smiles = AllChem.MolToSmiles(AllChem.MolFromSmiles(smiles))
    except:
        smiles = ''
    return smiles

def cano_smiles(file, sep=','):
    data = pd.read_csv(file, sep=sep)
    start = len(data)
    data['smiles'] = data['smiles'].apply(saltremover)
    data['smiles'] = data['smiles'].apply(stand_smiles)
    output = file.split('.csv')[0] + '_pro.csv'
    if os.path.exists(output):
        pass
    else:
        data.to_csv(output, index=False)
        print('we meet some smiles which cannot revert to cano_smiles and the number is', start - len(data))


def create_ECFP4(X, Y):
    smiles = np.array(X)
    ms = [AllChem.MolFromSmiles(smiles[i]) for i in range(len(smiles))]
    ms = [AllChem.MolFromSmiles(smiles[i]) for i in range(len(smiles))]
    ecfpMat = np.zeros((len(ms), 1024), dtype=int)
    for i in range(len(ms)):
        try:
            fp = AllChem.GetMorganFingerprintAsBitVect(ms[i], 2, 1024)
            ecfpMat[i] = np.array(list(fp.ToBitString()))
        except:
            ecfpMat[i] = np.array([0] * 1024)
    X = ecfpMat
    return X, Y


def statistical(y_true, y_pred, y_pro):
    c_mat = confusion_matrix(y_true, y_pred)
    tn, fp, fn, tp = list(c_mat.flatten())
    se = tp / (tp + fn)
    sp = tn / (tn + fp)
    precision = tp / (tp + fp)
    acc = (tp + tn) / (tn + fp + fn + tp)
    mcc = (tp * tn - fp * fn) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn) + 1e-8)
    auc_prc = auc(precision_recall_curve(y_true, y_pro, pos_label=1)[1],
                  precision_recall_curve(y_true, y_pro, pos_label=1)[0])
    auc_roc = roc_auc_score(y_true, y_pro)
    return precision, se, sp, acc, mcc, auc_prc, auc_roc, tn, fp, fn, tp

#这里只讨论了一种数据分割方式
def split_dataset(X,Y,split_type='random',valid_need = False,train_size=0.80,random_state=42):
    if valid_need is True:
        if split_type == 'random':
            X_train, X_rest, Y_train, Y_rest = train_test_split(X, Y, train_size=train_size, random_state=random_state)
            X_valid, X_test, Y_valid, Y_test = train_test_split(X_rest, Y_rest, train_size=0.5, random_state=random_state)
            return X_train, X_valid, X_test, Y_train, Y_valid, Y_test
    else:
        if split_type == 'random':
            X_train, X_test, Y_train, Y_test = train_test_split(X, Y, train_size = train_size, random_state=random_state)
            return X_train, X_test, Y_train, Y_test

file = 'D:\code\EP4\dataset_new/new_screen\compounds\compound_screen\compounds_dnn_permmol_screen_5.3.csv'
cano_smiles(file, sep=',')


