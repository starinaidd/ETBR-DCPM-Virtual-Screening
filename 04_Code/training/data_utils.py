import numpy as np
import logging
import torch
import dgl
from sklearn.metrics import roc_auc_score, confusion_matrix, precision_recall_curve, auc
from typing import List, Tuple, Dict
from numpy.typing import NDArray
from rdkit.Chem import AllChem



class Meter(object):
    '''
    steps:
    meter.update()
    meter.compute_metric('classification', ['auc_roc', 'acc'])

    attenton! y_score, y_true need to be shape like (nsamples, 1)
    '''
    def __init__(self) -> None:
        self.y_score = []
        self.y_true = []

    def update(self, y_score: NDArray, y_true: NDArray) -> None:
        self.y_score.append(y_score)
        self.y_true.append(y_true)
    
    def gather(self) -> None:
        self.y_score = np.concatenate(self.y_score, axis=0)
        self.y_true = np.concatenate(self.y_true, axis=0)
        
    def calculate_cmat(self) -> Tuple[float]:
        y_pred = np.where(self.y_score > 0.5, 1, 0)
        tn, fp, fn, tp = confusion_matrix(self.y_true, y_pred, labels=[0, 1]).ravel()
        return tn, fp, fn, tp

    @staticmethod
    def calculate_se(tn: float, fp: float, fn: float, tp: float) -> float:
        se = tp / (tp + fn)
        return se

    @staticmethod
    def calculate_sp(tn: float, fp: float, fn: float, tp: float) -> float:
        sp = tn / (tn + fp)
        return sp

    @staticmethod
    def calculate_pre(tn: float, fp: float, fn: float, tp: float) -> float:
        pre = tp / (tp + fp)
        return pre

    @staticmethod
    def calculate_acc(tn: float, fp: float, fn: float, tp: float) -> float:
        acc = (tp + tn) / (tn + fp + fn + tp)
        return acc

    @staticmethod
    def calculate_mcc(tn: float, fp: float, fn: float, tp: float) -> float:
        mcc = (tp * tn - fp * fn) / np.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        return mcc

    @staticmethod
    def calculate_f1(tn: float, fp: float, fn: float, tp: float) -> float:
        f1 = (2*tp) / (2*tp + fp + fn)
        return f1 
    
    def calculate_auc_roc(self) -> float:
        auc_roc = roc_auc_score(self.y_true, self.y_score)
        return auc_roc

    def calculate_auc_prc(self) -> float:
        precision, recall, _ = precision_recall_curve(self.y_true, self.y_score, pos_label=1)
        auc_prc = auc(recall, precision)
        return auc_prc

    def calculate_rmse(self) -> float:
        rmse = np.sqrt(np.mean((self.y_score - self.y_true) ** 2))
        return rmse

    def compute_metric(self, task_type: str, metric_name: List[str]) -> Dict[str, float]:
        '''
        task_type should be 'classification' or 'regression'
        metric_name should be a list, 
        ['se', 'sp', 'pre', 'acc', 'mcc', 'f1', 'auc_roc', 'auc_prc', 'rmse']
        '''
        self.gather()
        res = {}
        if task_type == 'regression':
            for task in metric_name:
                if task == 'rmse':
                    res['rmse'] = self.calculate_rmse()
        elif task_type == 'classification':
            tn, fp, fn, tp = self.calculate_cmat()
            res['cmat'] = [tn, fp, fn, tp]
            for task in metric_name:
                if task == 'se':
                    res['se'] = self.calculate_se(tn, fp, fn, tp)
                if task == 'sp':
                    res['sp'] = self.calculate_sp(tn, fp, fn, tp)
                if task == 'pre':
                    res['pre'] = self.calculate_pre(tn, fp, fn, tp)
                if task == 'acc':
                    res['acc'] = self.calculate_acc(tn, fp, fn, tp)
                if task == 'mcc':
                    res['mcc'] = self.calculate_mcc(tn, fp, fn, tp)
                if task == 'f1':
                    res['f1'] = self.calculate_f1(tn, fp, fn, tp)
                if task == 'auc_roc':
                    res['auc_roc'] = self.calculate_auc_roc()
                if task == 'auc_prc':
                    res['auc_prc'] = self.calculate_auc_prc()
        else:
            raise ValueError('wrong task type')

        return res
    

def smiles_to_ecfp4(smiles):
    try:
        ms = AllChem.MolFromSmiles(smiles)
    except:
        ms = ''
    fpgen = AllChem.GetMorganGenerator(radius=2, fpSize=1024)
    fp = fpgen.GetFingerprint(ms)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array


def smiles_to_maccs(smiles):
    try:
        ms = AllChem.MolFromSmiles(smiles)
    except:
        ms = ''
    fp = AllChem.GetMACCSKeysFingerprint(ms)
    fp_array = np.array([int(i) for i in list(fp.ToBitString())], dtype='float32')
    fp_array = np.expand_dims(fp_array, 0)
    return fp_array


def smiles_to_atompairs(smiles):
    ms = AllChem.MolFromSmiles(smiles)
    if ms is None:
        return np.zeros((1, 1024), dtype='float32')

    fp = AllChem.GetHashedAtomPairFingerprintAsBitVect(ms, nBits=1024)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array


# 6. Topological Torsions 指纹
def smiles_to_torsions(smiles):
    ms = AllChem.MolFromSmiles(smiles)
    if ms is None:
        return np.zeros((1, 1024), dtype='float32')

    fp = AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect(ms, nBits=1024)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array


# 7. RDKitFP
def smiles_to_rdkitfp(smiles):
    ms = AllChem.MolFromSmiles(smiles)
    if ms is None:
        return np.zeros((1, 2048), dtype='float32')

    fp = AllChem.RDKFingerprint(ms, fpSize=2048)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array


# 8. AVALON 指纹
def smiles_to_avalon(smiles):
    ms = AllChem.MolFromSmiles(smiles)
    if ms is None:
        return np.zeros((1, 1024), dtype='float32')

    from rdkit.Avalon.pyAvalonTools import GetAvalonFP
    fp = GetAvalonFP(ms, nBits=1024)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array


def smiles_to_pubchem(smiles):

    ms = AllChem.MolFromSmiles(smiles)
    if ms is None:
        return np.zeros((1, 881), dtype='float32')

    fp = AllChem.GetHashedTopologicalTorsionFingerprintAsBitVect(ms, nBits=881)
    fp_array = np.array(list(fp.ToBitString()), dtype='float32').reshape(1, -1)
    return fp_array



class Log(logging.Logger):
    def __init__(self, name: str, log_path: str) -> None:
        super().__init__(name)
        self.log_path = log_path

        self.setLevel(logging.DEBUG)
        self.file_handler = logging.FileHandler(log_path, mode="a+")
        self.console_handler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                                      datefmt="%Y-%m-%d %H:%M:%S")
        self.file_handler.setFormatter(formatter)
        self.console_handler.setFormatter(formatter)
        self.addHandler(self.file_handler)
        self.addHandler(self.console_handler)

    def console_off(self) -> None:
        self.removeHandler(self.console_handler)

    def console_on(self) -> None:
        self.addHandler(self.console_handler)


class EarlyStopping(object):
    """Early stop performing

    Parameters
    ----------
    mode : str
        * 'higher': Higher metric suggests a better model
        * 'lower': Lower metric suggests a better model
    patience : int
        Number of epochs to wait before early stop if the metric stops getting improved
    filename : str or None
        Filename for storing the model checkpoint
        """
    def __init__(self, mode='higher', patience=10, filename=None):
        assert mode in ['higher', 'lower']
        self.mode = mode
        if self.mode == 'higher':
            self._check = self._check_higher
        else:
            self._check = self._check_lower

        self.patience = patience
        self.counter = 0
        self.filename = filename
        self.best_score = None
        self.early_stop = False

    def _check_higher(self, score, prev_best_score):
        return (score > prev_best_score)

    def _check_lower(self, score, prev_best_score):
        return (score < prev_best_score)

    def step(self, score, model):
        if self.best_score is None:
            self.best_score = score
            if self.filename:
                self.save_checkpoint(model)
        elif self._check(score, self.best_score):
            self.best_score = score
            if self.filename:
                self.save_checkpoint(model)
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        return self.early_stop

    def save_checkpoint(self, model):
        """Save model when the metric on the validation set gets improved."""
        torch.save({'model_state_dict': model.state_dict()}, self.filename)

    def load_checkpoint(self, model):
        """Load model saved with early stopping"""
        model.load_state_dict(torch.load(self.filename)['model_state_dict'])


def collate_molgraphs(data):
    """Batching a list of datapoints for dataloader.

    Parameters
    ----------
    data : list of 4-tuples.
        Each tuple is for a single datapoint, consisting of
        a SMILES, a DGLGraph, all-task labels and a binary
        mask indicating the existence of labels.

    Returns
    -------
    smiles : list
        List of smiles
    bg : DGLGraph
        The batched DGLGraph.
    labels : Tensor of dtype float32 and shape (B, T)
        Batched datapoint labels. B is len(data) and
        T is the number of total tasks.
    masks : Tensor of dtype float32 and shape (B, T)
        Batched datapoint binary mask, indicating the
        existence of labels.
    """
    assert len(data[0]) in [3, 4], \
        'Expect the tuple to be of length 3 or 4, got {:d}'.format(len(data[0]))
    if len(data[0]) == 3:
        smiles, graphs, labels = map(list, zip(*data))
    else:
        smiles, graphs, labels, masks = map(list, zip(*data))

    bg = dgl.batch(graphs)
    bg.set_n_initializer(dgl.init.zero_initializer)
    bg.set_e_initializer(dgl.init.zero_initializer)
    labels = torch.stack(labels, dim=0)

    if len(data[0]) == 3:
        # mask is None
        masks = torch.ones(labels.shape)
    else:
        masks = torch.stack(masks, dim=0)

    return smiles, bg, labels, masks



