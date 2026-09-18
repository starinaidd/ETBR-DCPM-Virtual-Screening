import random
import pandas as pd

random.seed(12)
data1 = pd.read_csv('D:\code\graduate\ETB_data/train_model_data\EDNRB_all_active.csv')
smiles1 = data1['SMILES']
#print(len(smiles1))
random_smiles1 = random.sample(smiles1.tolist(), 20)

random.seed(17)
data2 = pd.read_csv('D:\code\graduate\ETB_data/train_model_data\EDNRB_all_active.csv')
smiles2 = data2['SMILES']
#print(len(smiles2))
random_smiles2 = random.sample(smiles2.tolist(), 20)

#random.seed(12)
#data3 = pd.read_csv('D:\code\Lp(a)-apo(a)\dataset\mid_df.csv')
#smiles3 = data3['smiles']
#print(len(smiles3))
#random_smiles3 = random.sample(smiles3.tolist(), 150)

#random.seed(17)
#data4 = pd.read_csv('D:\code\Lp(a)-apo(a)\dataset\mid_df.csv')
#smiles4 = data4['smiles']
#print(len(smiles4))
#random_smiles4 = random.sample(smiles4.tolist(), 150)

#random.seed(26)
#data5 = pd.read_csv('D:\code\Lp(a)-apo(a)\dataset\mid_df.csv')
#smiles5 = data5['smiles']
#print(len(smiles5))
#random_smiles5 = random.sample(smiles5.tolist(), 150)

random_smiles = random_smiles1 + random_smiles2

nonactivity_smiles = pd.DataFrame(random_smiles, columns=['smiles'])
nonactivity_smiles.to_csv('D:\code\graduate\ETB_data\suyuan\ETB_random_choice_active.csv')