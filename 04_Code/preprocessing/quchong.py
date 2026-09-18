import pandas as pd
data = pd.read_csv('D:\code\permmol\dataset\muv_dataset\muv_548.csv')
print(data)
#data = data[['ID', 'Smiles', 'Standard Relation', 'Standard Value', 'acticity']]
data = data.drop_duplicates(subset='smiles', keep='first', ignore_index=True)
print(data)
data.to_csv('D:\code\permmol\dataset\muv_dataset\muv_548_qc.csv', index=False)