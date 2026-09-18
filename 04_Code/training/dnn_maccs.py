import gc
import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.nn import BCEWithLogitsLoss
from hyperopt import fmin, tpe, hp, Trials
from data_utils import collate_molgraphs, smiles_to_ecfp4, smiles_to_maccs
from sklearn.model_selection import KFold
from data_utils import Log, EarlyStopping
from dnn_torch_utils import Meter, MyDataset, MyDNN, collate_fn, set_random_seed
from dataset import FPDataset
from modeling import SimpleDNN
import numpy as np
import pickle


def train_epoch(model, data_loader, loss_func, optimizer, device):
    model.train()
    train_metric = Meter()
    for batch_id, batch_data in enumerate(data_loader):
        fp, labels, masks = batch_data
        fp = fp.to(device)
        labels = labels.reshape(-1, 1)
        labels = labels.to(device) # (bsz, 1)
        masks = masks.reshape(-1, 1)
        masks = masks.to(device)
        outputs = model(fp)# (bsz, 1)

        loss = (loss_func(outputs, labels) * (masks != 0).float()).mean()

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        y_score = outputs.detach().cpu().numpy()
        y_true = labels.detach().cpu().numpy()
        # torch.cuda.empty_cache()

        train_metric.update(y_score, y_true, masks)

    roc_score = train_metric.compute_metric('roc_auc')

    return roc_score

def eval_epoch(model, data_loader, device):
    model.eval()
    eval_metric = Meter()
    with torch.no_grad():
        for batch_id, batch_data in enumerate(data_loader):
            fp, labels, masks = batch_data
            fp = fp.to(device)
            labels = labels.reshape(-1, 1)
            labels = labels.to(device)  # (bsz, 1)
            masks = masks.reshape(-1, 1)
            masks = masks.to(device)
            outputs = model(fp)
            #outputs = F.sigmoid(outputs)

            y_score = outputs.detach().cpu().numpy()
            y_true = labels.detach().cpu().numpy()

            eval_metric.update(y_score, y_true, masks)
    acc_score = eval_metric.compute_metric('acc')
    mcc_score = eval_metric.compute_metric('mcc')
    #tn_score = eval_metric.compute_metric('tn')
    #fp_score = eval_metric.compute_metric('fp')
    #tp_score = eval_metric.compute_metric('tp')
    #fn_score = eval_metric.compute_metric('fn')
    precision_score = eval_metric.compute_metric('precision')
    se_score = eval_metric.compute_metric('se')
    sp_score = eval_metric.compute_metric('sp')
    roc_score = eval_metric.compute_metric('roc_auc')
    #eval_res = eval_metric.compute_metric('classification', ['se', 'sp', 'pre', 'acc', 'mcc', 'f1', 'auc_roc', 'auc_prc'])
    eval_res = []
    eval_res.append({'se': se_score, 'sp': sp_score, 'precision': precision_score, 'acc': acc_score, 'mcc': mcc_score, 'auc_roc': roc_score})


    return {'se': se_score, 'sp': sp_score, 'precision': precision_score, 'acc': acc_score, 'mcc': mcc_score, 'auc_roc': roc_score}

def train_dnn(fold, train_datas, valid_datas, test_datas):
    device = torch.device('cpu')
    print(type(train_datas))
    train_dataset_c = train_datas.copy()
    train_dataset_c['smiles'] = train_dataset_c['smiles'].apply(smiles_to_maccs).tolist()
    data_tr_x = np.concatenate(train_dataset_c['smiles'].tolist(), axis=0)
    data_tr_y = np.array(train_dataset_c["activity"].tolist())
    train_dataset = MyDataset(data_tr_x, data_tr_y)
    
    valid_dataset_c = valid_datas.copy()
    valid_dataset_c['smiles'] = valid_dataset_c['smiles'].apply(smiles_to_maccs).tolist()
    data_va_x = np.concatenate(valid_dataset_c['smiles'].tolist(), axis=0)
    data_va_y = np.array(valid_dataset_c["activity"].tolist())
    valid_dataset = MyDataset(data_va_x, data_va_y)
    
    test_dataset_c = test_datas.copy()
    test_dataset_c['smiles'] = test_dataset_c['smiles'].apply(smiles_to_maccs).tolist()
    data_te_x = np.concatenate(test_dataset_c['smiles'].tolist(), axis=0)
    data_te_y = np.array(test_dataset_c["activity"].tolist())
    test_dataset = MyDataset(data_te_x, data_te_y)
    
    train_loader = DataLoader(dataset=train_dataset, batch_size=64, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(dataset=valid_dataset, batch_size=64, shuffle=False, collate_fn=collate_fn)
    test_loader = DataLoader(dataset=test_dataset, batch_size=64, shuffle=False, collate_fn=collate_fn)

    #train_loader = train_dataset
    #val_loader = valid_dataset
    #test_loader = test_dataset
    para_dict = {
        'hidden_unit1_ls' : [64, 128, 256, 512],
        'hidden_unit2_ls' : [64, 128, 256, 512],
        'hidden_unit3_ls' : [64, 128, 256, 512],
    }

    hyper_paras_space = {
        'lr': hp.uniform('lr', 0.0001, 0.1),
        'dropout': hp.uniform('dropout', 0, 0.5),
        'hidden_unit1': hp.choice('hidden_unit1', para_dict['hidden_unit1_ls']),
        'hidden_unit2': hp.choice('hidden_unit2', para_dict['hidden_unit2_ls']),
        'hidden_unit3': hp.choice('hidden_unit3', para_dict['hidden_unit3_ls'])
        }
    
    def hyper_opt(hyper_paras):
        hidden_units = [hyper_paras['hidden_unit1'], hyper_paras['hidden_unit2'], hyper_paras['hidden_unit3']]
        model = SimpleDNN(
            inputs=167,
            hideen_units=hidden_units,
            outputs=1,
            dp_ratio=hyper_paras['dropout']
            )
        
        optimizer = torch.optim.Adam(model.parameters(), lr=hyper_paras['lr'])

        loss_func = BCEWithLogitsLoss(reduction='none')
        stopper = EarlyStopping(mode='higher', patience=10, filename=None)
        model.to(device)
        for i in range(50):
            # training
            train_epoch(model, train_loader, loss_func, optimizer, device)
            # early stopping
            val_scores = eval_epoch(model, val_loader, device)
            early_stop = stopper.step(val_scores['auc_roc'], model)
            if early_stop:
                break
        for i in val_scores['auc_roc']:
            auc_roc = i
        feedback = 1 - auc_roc
        model.cpu()
        torch.cuda.empty_cache()
        gc.collect()
        return feedback
    trials = Trials()
    opt_res = fmin(hyper_opt, hyper_paras_space, algo=tpe.suggest, max_evals=50, trials=trials)
    
    best_params = {
        'best_lr' : opt_res['lr'],
        'best_dropout': opt_res['dropout'],
        'best_hidden_unit1' : para_dict['hidden_unit1_ls'][opt_res['hidden_unit1']],
        'best_hidden_unit2' : para_dict['hidden_unit2_ls'][opt_res['hidden_unit2']],
        'best_hidden_unit3' : para_dict['hidden_unit3_ls'][opt_res['hidden_unit3']]
    }
    logger.info(f'the best hyper-parameters settings for DNN are: {best_params}')
    best_hidden_units = [best_params['best_hidden_unit1'], best_params['best_hidden_unit2'], best_params['best_hidden_unit3']]

    best_model = SimpleDNN(inputs=167,hideen_units=best_hidden_units,outputs=1,dp_ratio=best_params['best_dropout'])
    
    optimizer = torch.optim.Adam(best_model.parameters(), lr=best_params['best_lr'])
    loss_func = BCEWithLogitsLoss(reduction='none')
    ckpt_path = f'./ckpt/toxcast_dnn_maccs/model_fold_{fold}.pth'
    stopper = EarlyStopping(mode='higher', patience=10, filename=None)
    best_model.to(device)
    for i in range(50):
        # training
        train_epoch(best_model, train_loader, loss_func, optimizer, device)
        # early stopping
        val_scores = eval_epoch(best_model, val_loader, device)
        early_stop = stopper.step(val_scores['auc_roc'], best_model)
        if early_stop:
            break
    torch.save(best_model.state_dict(), ckpt_path)

    eval_res = eval_epoch(best_model, val_loader, device)
    logger.info(eval_res)

    test_res = eval_epoch(best_model, test_loader, device)
    logger.info(test_res)


if __name__ == '__main__':
    #df = pd.read_csv("./data/EP4_train_new.csv")
    #test_datas = pd.read_csv("./data/EP4_test_new.csv")
    #train_fp = pickle.load(open('./data/ETB_train.pkl', 'rb')).tolist()
    #train_fp = pickle.load(open('./data/EP4_train.pkl'), 'rb').tolist()
    #train_activity = pd.read_csv('./data/ETB_train.csv')['activity']
    #df = pd.DataFrame({'fp' : train_fp, 'activity' : train_activity})

    #test_fp = pickle.load(open('./data/ETB_test.pkl', 'rb')).tolist()
    #test_activity = pd.read_csv("./data/ETB_test.csv")['activity']
    #test_datas = pd.DataFrame({'fp' : test_fp, 'activity' : test_activity})
    df = pd.read_csv('./data/toxcast_train_pro.csv')
    test_datas = pd.read_csv('./data/toxcast_test_pro.csv')
    #X = pickle.load(open(file_path, 'rb'))
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    logger = Log('train', f'./logs/toxcast_dnn_maccs.log')
    
    for fold, (train_index, valid_index) in enumerate(kf.split(df)):
        train_datas = df.iloc[train_index]
        valid_datas = df.iloc[valid_index]
        #train_datas = train_datas.to_numpy().tolist()
        #valid_datas = valid_datas.to_numpy().tolist()
        
        logger.info(f'now is fold {fold}')

        train_dnn(fold, train_datas, valid_datas, test_datas)
