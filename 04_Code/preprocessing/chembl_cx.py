import pandas as pd

data = pd.read_csv("D:\code\EDNRB\dataset\EDNRB_CHEMBL_IC50.csv", sep = ";")
data = data[['Molecule ChEMBL ID', 'Standard Type', 'Standard Relation', 'Assay Type',
             'Assay ChEMBL ID', 'Assay Description', 'Standard Units', 'Standard Value', 'Smiles']]


# 用于处理分类任务
def process(chembl, type = 'None', aim = 'cla', gap = 100, split = 10000, limit = None):
    if limit == None:
        limit = split
    chembl = chembl[['Molecule ChEMBL ID', 'Smiles', 'Standard Type', 'Standard Units', 'Standard Relation', 'Standard Value']]
    chembl = chembl[(chembl['Standard Type'] == type)]
    print("Now we need only save ", type, "data is ", len(chembl))

    chembl = chembl.astype({"Standard Value": "float64"})
    chembl = chembl[chembl["Standard Units"] == "nM"]
    print("Now we need only save unit 'nM' data is ", len(chembl))

    chembl.dropna(subset=['Standard Value', 'Smiles'], axis=0, how="any", inplace=True)
    print("Now we need only save have smiles and data value data is ", len(chembl))

    data = chembl[(chembl['Standard Relation'] == '\'=\'')]
    print('Now we need only save "=" data is ', len(data))

    # chembl = chembl[(chembl['Standard Value'] <= limit) | (chembl['Standard Value'] >= split)]
    # print('Now we need only save have  data  which is <', limit, 'and >', split, 'about', len(chembl))
    max = data.groupby(['Molecule ChEMBL ID', 'Smiles', 'Standard Relation'])['Standard Value'].max()
    min = data.groupby(['Molecule ChEMBL ID', 'Smiles', 'Standard Relation'])['Standard Value'].min()
    valgap = pd.DataFrame([max, min])
    valgap = pd.DataFrame(valgap.values.T, index=valgap.columns, columns=valgap.index)  # 转置
    valgap.columns = ["max", "min"]
    valerr = valgap[(valgap['min'] <= limit) & (valgap['max'] >= split)]
    print('we need to remove the compound not only have <' + str(limit) + ' but also >' + str(split), 'about error',
          len(valerr))

    valgap = valgap.drop(index=list(valerr.index))    # 移除问题数据
    # 新增‘gap’列，数值为最大值除以最小值，然后再与输入的参数‘gap’比较，满足小于等于参数值，则保留
    valgap['gap'] = (valgap['max'] / valgap['min'])
    reason = valgap[valgap['gap'] <= gap].reset_index()
    # 在原’=‘数据中保留满足上面条件的数据
    keep = data[data['Molecule ChEMBL ID'].isin(reason['Molecule ChEMBL ID'].tolist())]
    keep = keep.groupby(['Molecule ChEMBL ID', 'Smiles', 'Standard Relation'])['Standard Value'].mean()
    keep = keep.reset_index()
    print(len(keep))
    # 对于数值小于split阈值的为活性，标为1；大于split阈值的为非活性，标为0

    keep = keep[(keep['Standard Value'] <= limit) | (keep['Standard Value'] >= split)]
    # keep = keep.drop(index=keep[(keep['Standard Value'] > limit) & (keep['Standard Value'] < split)].index.tolist())
    print('Now we need only save have  data  which is <=', limit, 'and >=', split, 'about', len(keep))
    keep['Activity'] = keep['Standard Value'].apply(lambda x: 1 if x < split else 0)
    print('Now we need only save the data which gap low ' + str(gap) + ' and keep one data one line is ', len(keep))

    # 把数据符号为等于‘=’的所有数据移除，剩下的即为'>''<'等符号数据
    plus = chembl[~chembl['Molecule ChEMBL ID'].isin(data['Molecule ChEMBL ID'].tolist())]
    print('Now we need to process the other relation ,such as < > total', len(plus))
    print(len(chembl), len(data), len(plus))
    # 符号为'<='以及'<'的数据保存到small；符号为'>='以及'>'的数据保存到big
    small = plus[plus['Standard Relation'].isin(['\'<=\'', '\'<\''])]
    big = plus[plus['Standard Relation'].isin(['\'>\'', '\'>=\''])]
    print('Now we have < ', len(small), 'and >', len(big))
    # 判断：small中的数据数值小于等于limit阈值的保留并且保留第一次出现的数值，否则移除数据；然后数据标为活性'1'

    small = small[small['Standard Value'] <= limit].drop_duplicates(subset='Molecule ChEMBL ID', keep='first')
    # max1 = small.groupby(['Molecule ChEMBL ID'])['Standard Value'].max()
    # max1 = pd.DataFrame([max1])
    # max1 = pd.DataFrame(max1.values.T, index=max1.columns, columns=max1.index)
    # max1.columns = ['max1']
    # max1 = max1[max1['max1'] <= limit]
    # small = small[small['Molecule ChEMBL ID'].isin(max1.index.tolist())]
    # small = small.drop_duplicates(subset='Molecule ChEMBL ID', keep='first')
    small['Activity'] = 1
    # 判断：big中的数据数值大于等于split阈值的保留并且保留第一次出现的数值，否则移除数据；然后数据标为非活性'0'
    big = big[big['Standard Value'] >= split].drop_duplicates(subset='Molecule ChEMBL ID', keep='first')
    # min1 = big.groupby(['Molecule ChEMBL ID'])['Standard Value'].min()
    # min1 = pd.DataFrame([min1])
    # min1 = pd.DataFrame(min1.values.T, index=min1.columns, columns=min1.index)
    # min1.columns = ['min1']
    # min1 = min1[min1['min1'] >= split]
    # big = big[big['Molecule ChEMBL ID'].isin(min1.index.tolist())]
    # big = big.drop_duplicates(subset='Molecule ChEMBL ID', keep='last')
    big['Activity'] = 0

    print('Now we could fenbie remove the dup in <.> ', 'and get <', len(small), 'get >', len(big))
    # 把small和big合并然后去重
    plus = small._append(big, ignore_index=True).drop_duplicates(subset='Molecule ChEMBL ID', keep=False)
    print('Now we could  remove the dup in <.> and merge <.> data', len(plus))
    # 最后和'='的数据合并
    data = keep._append(plus, ignore_index=True)
    print(len(data))
    data = data[['Molecule ChEMBL ID', 'Smiles', 'Standard Relation', 'Standard Value', 'Activity']]
    data.columns = ['ID', 'Smiles', 'Standard Relation', 'Standard Value', 'activity']
    print('Now we could  merge the = and <> total', len(data))
    data = data.drop_duplicates(subset='ID', keep=False)
    print(len(data))
    # 输出活性数据量和非活性数据量，再求他们的比值
    print('Now we have active  compounds ', len(data[data['activity'] == 1]), 'and inactive compounds ',
          len(data[data['activity'] == 0])
          , 'and the ratio of inactive/active is ',
          round(len(data[data['activity'] == 0]) / len(data[data['activity'] == 1]), 2))
    return data
print('we have total data is ',len(data))           #总的数据量

data = process(data, type = 'IC50', aim = 'cla', gap = 10, split = 1000, limit=100)
data=data.sample(frac=1.0)
data=data.reset_index(drop=True)
# print(data)
# data_name = '_'.join(['A1', '0410','chembl','Ki','cla','gap10','split1000','limit100.csv'])
# # data_name = '_'.join(['A1', 'chembl','Ki','cla','gap10', 'split1000.csv'])
# # data.to_csv(data_name, index=False)
data.to_csv('D:\code\EDNRB\dataset\EDNRB_CHEMBL_IC50_100_10000.csv', index=False)
