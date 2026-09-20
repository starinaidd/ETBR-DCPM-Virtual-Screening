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
import pickle
import torch
from dnn_torch_utils import MyDNN
#from modeling import SimpleDNN





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
    parser.add_argument('--file', default='D:\code\compound_lirbary\specs_new_02.csv')
    parser.add_argument('--models', default='D:\code\MAT2A\dataset/five zhe\ckpt\dnn\model_fold_0.pth')
    parser.add_argument('--prop', default=0.5, type=float)
    parser.add_argument('--sep', default=',', type=str)
    parser.add_argument('--smiles_col', default='smiles', type=str)
    parser.add_argument('--cpus', default=32,type=int)
    parser.add_argument('--out_dir', default='D:\code\MAT2A\dataset/five zhe\ckpt\dnn')
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


def screen_file(file=file, sep=',', prop = 0.5, models=models, smiles_col=smiles_col, out_dir='./'):
    count = 0
    com = 0
    out_file = os.path.join(out_dir, file.split('/')[-1].replace('.csv', '_screen_new_{}.csv'.format(prop)))
    f = open(out_file, 'w')

    df = pd.read_csv(file, sep=sep, engine='python')
    #df.columns = open(file,'r').readline().strip().split(sep)[:15]
    print(df.columns)
    total = len(df)
    print('共有', total, '个分子需要筛选')
    print(time.time() - s)

    #model = models[0]
    #model_name = model.split('_')[1]
    #type = model.split('_')[-4]
    #print('model name:', model_name, 'des:', type)
    inputs = 1536

    model = MyDNN(inputs=1536,hideen_units=[64, 128, 64],outputs=1,dp_ratio=0.20112391936365895,reg=False)
    model.load_state_dict(torch.load(models))
    #print('model classes:', model.classes_)

    model.eval()
    features = pickle.load(open(file.replace('.csv', '.pkl'), 'rb'))
    #print(model)
    for i, smiles in enumerate(df[smiles_col]):
        com +=1
        fprint = np.asarray(features[i], dtype=np.float32).reshape(1, -1)
        pred = model(torch.FloatTensor(fprint))
        pred = torch.sigmoid(pred)
        if pred >= 0.5:
            count +=1
            f.write('{}\n'.format(smiles))
    #for smile in df[smiles_col]:
        #com += 1
        #feature = pickle.load(open(features, 'rb'))

        #pred = model.predict_proba(feature)
        #if pred[0][1] >= prop:
            #count +=1
            #f.write('{}\n'.format(smile))
        # pred = model.predict(fprint)
        # if pred[0] == 1:
        #     count += 1
        #     f.write('{}\n'.format(smile))
        if com % 100 == 0:
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
