import pandas as pd
data = pd.read_csv("D:\code\EDNRB\dataset\EDNRB_CHEMBL_BINDINGDB_IC50_100_1000.csv", sep = ",")
print(len(data))

# data = data[['Ligand SMILES', 'BindingDB MonomerID', 'BindingDB Ligand Name', 'IC50 (nM)', 'Curation/DataSource']]
#data = data.drop(index=data[data['Curation/DataSource'] == 'ChEMBL'].index.tolist())
print(len(data))

type = 'IC50'
data = data[['IC50 (nM)','BindingDB MonomerID','Ligand SMILES']]
#data = data[['Standard Value','ID','Smiles']]
data.columns = ['values','bdbm','Smiles']
data = data.dropna(subset=['values'])
print(len(data))
data = data.drop(data[data['bdbm']=='1'].index)
print(len(data))
data['relation'] = data['values'].apply(lambda x: str(x)[0])

data[type] = data['values'].apply(lambda x: '' if 'a' in str(x) else float(str(x)[1:]))
data = data[data['relation'].isin(['>',' ',"<"])]
change = {' ': "'='", '>': "'>'", '<': "'<'"}
data['relation'] = data['relation'].map(change)
data = data[['bdbm','Smiles','relation', type]]
print(len(data))
# data.to_csv('look.csv', index = False)
def process(bdbm,type='None',gap=100,split=10000,limit=None):
    if type == 'None':
        print('that need a selected type to process,such as \'IC50\'')
    if limit == None:
        limit = split
    print('limit: ', limit, ';', 'split:', split)
    bdbm = bdbm[['bdbm', 'Smiles', 'relation', type]]
    print('Now we will process to clssification')
    bdbm = bdbm.astype({type: "float64"})
    bdbm.dropna(subset=[type, 'Smiles'], axis=0, how="any", inplace=True)
    print('Now we need only save have smiles and data value data is ', len(bdbm))
    # bdbm = bdbm[(bdbm[type] <= limit) | (bdbm[type] >= split)]
    # print('Now we need only save have  data  which is <', limit, 'and >', split, 'about', len(bdbm))

    data = bdbm[(bdbm['relation'] == '\'=\'')]
    print('Now we need only save "=" data is ', len(data))
    max = data.groupby(['bdbm', 'Smiles', 'relation'])[type].max()
    min = data.groupby(['bdbm', 'Smiles', 'relation'])[type].min()
    valgap = pd.DataFrame([max, min]).T
    valgap.columns = ["max", "min"]
    valerr = valgap[(valgap['min'] < limit) & (valgap['max'] > split)]
    print('we need to remove the compound not only have <' + str(limit) + ' but also >' + str(split), 'about error',
          len(valerr))
    valgap = valgap.drop(index=list(valerr.index))
    valgap['gap'] = (valgap['max'] / valgap['min'])
    reason = valgap[valgap['gap'] <= gap].reset_index()
    keep = data[data['bdbm'].isin(reason['bdbm'].tolist())]
    keep = keep.groupby(['bdbm', 'Smiles', 'relation'])[type].mean()
    keep = keep.reset_index()
    keep = keep[(keep[type] <= limit) | (keep[type] >= split)]
    # keep = keep.drop(index=keep[(keep[type] > limit) & (keep[type] < split)].index.tolist())
    print('Now we need only save have  data  which is <=', limit, 'and >=', split, 'about', len(keep))
    keep['activity'] = keep[type].apply(lambda x: 1 if x < split else 0)
    print('Now we need only save the data which gap low ' + str(gap) + ' and keep one data one line is ', len(keep))

    plus = bdbm[~bdbm['bdbm'].isin(data['bdbm'].tolist())]
    print('Now we need to process the other relation ,such as < > total', len(plus))
    print(len(bdbm), len(data), len(plus))
    small = plus[plus['relation'].isin(['\'<\''])]
    big = plus[plus['relation'].isin(['\'>\''])]
    print('Now we have < ', len(small), 'and >', len(big))
    small = small[small[type] <= limit].drop_duplicates(subset='bdbm', keep='first')
    # max1 = small.groupby(['bdbm'])[type].max()
    # max1 = pd.DataFrame([max1])
    # max1 = pd.DataFrame(max1.values.T, index=max1.columns, columns=max1.index)
    # max1.columns = ['max1']
    # max1 = max1[max1['max1'] <= limit]
    # small = small[small['bdbm'].isin(max1.index.tolist())]
    small['activity'] = 1
    big = big[big[type] >= split].drop_duplicates(subset='bdbm', keep='first')
    # min1 = big.groupby(['bdbm'])[type].min()
    # min1 = pd.DataFrame([min1])
    # min1 = pd.DataFrame(min1.values.T, index=min1.columns, columns=min1.index)
    # min1.columns = ['min1']
    # min1 = min1[min1['min1'] >= split]
    # big = big[big['bdbm'].isin(min1.index.tolist())]
    # big = big.drop_duplicates(subset='bdbm', keep='first')
    big['activity'] = 0
    print('Now we could fenbie remove the dup in <.> and get <', len(small), 'get >', len(big))

    plus = small._append(big, ignore_index=True)
    print(len(plus))
    plus = plus.drop_duplicates(subset='bdbm', keep=False)
    print(len(plus))
    print('Now we could  remove the dup in <.> and merge <.> data', len(plus))
    data = keep._append(plus, ignore_index=True)

    data = data[['bdbm', 'Smiles', 'relation', type, 'activity']]
    data.columns = ['ID', 'Smiles', 'Standard Relation', 'Standard Value', 'activity']

    print('Now we could  merge the = and <> total', len(data))
    print('Now we have active  compounds ', len(data[data['activity'] == 1]), 'and inactive compounds ',
          len(data[data['activity'] == 0])
          , 'and the ratio of inactive/active is ',
          round(len(data[data['activity'] == 0]) / len(data[data['activity'] == 1]), 2))

    return data
print('we have total data is ',len(data))
data = process(data, type = 'IC50', gap=10, split=1000, limit=100)
# data = data.drop_duplicates(subset=['ID'], keep='first', inplace=False)
# print(len(data))
# data_name = '_'.join(['A1', '0410', 'bindingdb',type,'cla','gap10','split1000','limit100.csv'])
data.to_csv('D:\code\EDNRB\dataset\EDNRB_CHEMBL_BINDINGDB_IC50_100_1000_new.csv', index=False)
# data_name = '_'.join(['MNK', 'bindingdb',type,'cla','gap10','split10','1000.csv'])
# data.to_csv(data_name, index = False)
