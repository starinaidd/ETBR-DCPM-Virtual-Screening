import numpy as np
from torch.utils.data import Dataset
from data_utils import smiles_to_ecfp4


class FPDataset(Dataset):
    def __init__(self, df, fptype='ECFP4', mode='train'):
        self.mode = mode
        self.fptype = fptype
        dataset = self._getfpdataset(df)
        self.fps = dataset['feature'].tolist()
        self.labels = dataset['label'].tolist()

    def _getfpdataset(self, dataset):
        if self.fptype == 'ECFP4':
            dataset['feature'] = dataset['smiles'].apply(smiles_to_ecfp4)
            return dataset
        else: 
            raise KeyError("no such def yet")

    def __len__(self):
        return len(self.fps)

    def __getitem__(self, idx):
        if self.mode == 'train':
            fp = self.fps[idx]
            label = self.labels[idx]
            return fp.ravel(), np.array([label], dtype=np.float32)
        elif self.mode == 'screen':
            return self.dataset['smiles'][idx], self.dataset['feature'][idx]
