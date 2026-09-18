import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem import Lipinski, Descriptors, Crippen
import multiprocessing as mp
from rdkit.Chem.FilterCatalog import FilterCatalog, FilterCatalogParams
import argparse
import joblib
import time
import os
s = time.time()
params = FilterCatalogParams()
params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS)
catalog = FilterCatalog(params)
def ro5(x):
    try:
        mol = Chem.MolFromSmiles(x)
        h_acc = Lipinski.NumHAcceptors(mol)
        h_don = Lipinski.NumHDonors(mol)
        # rotal = Lipinski.NumRotatableBonds(mol)
        weight = Descriptors.ExactMolWt(mol)
        logp = Crippen.MolLogP(mol)
        count = sum([weight <= 500, h_acc <= 10, h_don <= 5, logp <= 5])
        return 1 if count >= 3 else 0
    except:
        return 0
def pains(x):
    mol = Chem.MolFromSmiles(x)
    entry = catalog.GetFirstMatch(mol)  # Get the first matching PAINS
    return 1 if entry is not None else 0
def ecfp4(X, file=''):
    smiles = np.array(X)
    count = 0
    ms = [Chem.MolFromSmiles(smiles[i]) for i in range(len(smiles))]
    ecfpMat = np.zeros((len(ms), 1024), dtype=int)
    for i in range(len(ms)):
        try:
            fp = AllChem.GetMorganFingerprintAsBitVect(ms[i], 2, 1024)
            ecfpMat[i] = np.array(list(fp.ToBitString()))
        except:
            count += 1
            ecfpMat[i] = np.zeros((1, 1024), dtype=int)
    X = ecfpMat

    return X


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', default='D:\code\compound_lirbary\chemdiv\IC_134978.csv')
    parser.add_argument('--models', default='D:\code\EP4\dataset_new\data/rf\RF/five_zhe\ckpt\model_fold_3.pkl')
    parser.add_argument('--prop', default=0.5, type=float)
    parser.add_argument('--sep', default=',', type=str)
    parser.add_argument('--smiles_col', default='smiles', type=str)
    parser.add_argument('--cpus', default=8,type=int)
    parser.add_argument('--out_dir', default='D:\code\EP4\dataset_new\data/rf\RF/five_zhe\screen')
    args = parser.parse_args()
    return args

args = parse_args()
file = args.file
models = args.models
sep = args.sep
prop = args.prop
smiles_col = args.smiles_col
cpus = args.cpus
out_dir = args.out_dir


def screen_file(file='',sep=',',prop = 0.5, models='', smiles_col=smiles_col, out_dir='./'):
    count = 0
    com = 0
    out_file = os.path.join(out_dir, file.split('\\')[-1].replace('.csv', '_rf_screen_{}.csv'.format(prop)))
    f = open(out_file, 'w')

    df = pd.read_csv(file, sep=sep, header=None, engine='python')
    df.columns = open(file,'r').readline().strip().split(sep)[:15]
    print(df.columns)
    total = len(df)
    print(total, time.time() - s)

    model = models
    model_name = 'RF'
    type = 'cla'
    print('model name:', model_name, 'des:', type)
    model = joblib.load(model)
    print('model classes:', model.classes_)

    for smile in df[smiles_col]:
        com += 1
        fprint = ecfp4([smile], file=file)
        pred = model.predict_proba(fprint)
        if pred[0][1] >= prop:
            count +=1
            f.write('{}\n'.format(smile))
        # pred = model.predict(fprint)
        # if pred[0] == 1:
        #     count += 1
        #     f.write('{}\n'.format(smile))
        if com / 100 == 0:
            print(com)
    f.close()
    print('time spent:',time.time() - s, 'screen', count, 'screen precent ', round((count / com) * 100, 2), '%')


if os.path.isdir(file):
    p = mp.Pool(processes=cpus)
    for file_content in os.listdir(file):
        if '.csv' in file_content and 'pubchem' not in file_content:
            file_path = os.path.join(file,file_content)
            param = {'file':file_path, 'sep':sep, 'models':models, 'prop':prop, 'out_dir':out_dir}
            get = p.apply_async(screen_file,kwds = param)
    p.close()
    p.join()
elif os.path.isfile(file):
    screen_file(file=file, sep=sep, models=models, prop=prop, out_dir=out_dir)
else:
    print('What\'s this ?')
