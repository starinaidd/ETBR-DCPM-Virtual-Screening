from rdkit import Chem
import pandas as pd

#csv转sdf
df=pd.read_csv("D:\code\graduate\ETB_data\suyuan\select_active_40.csv")
print (df.shape)
df.head(1)

def out_sdf(lig_list, filename):
    writer=Chem.SDWriter(filename)
    for i in lig_list:
        writer.write(i)
    writer.close()
    return

cpd_list = []
for idx, row in df.iterrows():
    if idx % 5000 == 0:
        print(idx, ' have been processed')
    try:
        smi = row['smiles']
        mol = Chem.MolFromSmiles(smi)
        for prop in df.columns:
            prop_value = str(row[prop])
            mol.SetProp(prop, prop_value)
    except Exception as e:
        print(idx, e)
    cpd_list.append(mol)
len(cpd_list)
#
out_sdf(cpd_list, "D:\code\graduate\ETB_data\suyuan\select_active_40.sdf")


