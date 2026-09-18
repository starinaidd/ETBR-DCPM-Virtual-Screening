import pandas as pd

data = pd.read_csv('D:\code\EP4\dataset_new\data/rf\EP4_random_choice_pro.csv')
#将0和1分开
groups = data.groupby(data.activity)
data_true = groups.get_group(1)
data_false = groups.get_group(0)
#打乱乱数据
data_true = data_true.sample(frac=1.0)
data_false = data_false.sample(frac=1.0)

#训练集
train_true = data_true.iloc[:576, :]
train_false = data_false.iloc[:1280, :]
train_data = pd.concat([train_true, train_false], axis = 0, ignore_index=True).sample(frac=1)

#valid_true = data_true.iloc[497:559, :]
#valid_false = data_false.iloc[1139:1281, :]
#valid_data = pd.concat([valid_true, valid_false], axis = 0, ignore_index=True).sample(frac=1)

test_true = data_true.iloc[576:, :]
test_false = data_false.iloc[1280:, :]
test_data = pd.concat([test_true, test_false], axis = 0, ignore_index=True).sample(frac=1)

test_data.to_csv('D:\code\EP4\dataset_new\data/rf\EP4_test.csv')
#valid_data.to_csv('E:\code\EP4\dataset_new\EP4_random_choice_val.csv')
train_data.to_csv('D:\code\EP4\dataset_new\data/rf\EP4_train.csv')

