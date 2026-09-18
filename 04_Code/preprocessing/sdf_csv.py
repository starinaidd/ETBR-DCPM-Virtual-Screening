from rdkit import Chem
import pandas as pd
#sdf转csv
suppl = Chem.SDMolSupplier('D:\code\graduate\ETB_data\suyuan\select_active_40.sdf')
cpd_list = []
for i in range(len(suppl)):
    try:
        smi=Chem.MolToSmiles(suppl[i])
        temp_dict=suppl[i].GetPropsAsDict()
        temp_dict['smi']=smi
        cpd_list.append(temp_dict)
    except Exception as e:
        print(e)
        continue

df = pd.DataFrame(cpd_list)
print(len(df))
#df = df[['smiles']]
df.to_csv('D:\code\graduate\ETB_data\suyuan\select_active_40.csv', index=False)