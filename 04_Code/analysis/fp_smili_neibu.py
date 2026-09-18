import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

# ====================== 只需改这里 ======================
INPUT_CSV = "D:\code\graduate\ETB_data\suyuan\ETB_9compounds.csv"       # 只有一列：SMILES，无表头
SMILES_COL = "SMILES"             # 列名（如果没有表头就用 0）
OUTPUT_MATRIX = "D:\code\graduate\ETB_data\suyuan\similarity_matrix.csv"
OUTPUT_PAIRS = "D:\code\graduate\ETB_data\suyuan\similar_pairs.csv"
# ======================================================

# 读取分子
print("读取分子中...")
df = pd.read_csv(INPUT_CSV, header=None, names=[SMILES_COL])  # 无表头自动识别
df = df.dropna(subset=[SMILES_COL]).reset_index(drop=True)

# 生成有效分子
mols = []
for smi in df[SMILES_COL]:
    mol = Chem.MolFromSmiles(smi)
    if mol:
        mols.append(mol)

print(f"有效分子数量：{len(mols)}")

# 生成Morgan指纹（ECFP4，最常用）
fps = [AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024) for m in mols]

# 批量计算两两相似性
n = len(fps)
sim_matrix = np.zeros((n, n))

for i in range(n):
    fp_i = fps[i]
    for j in range(i, n):
        sim = DataStructs.TanimotoSimilarity(fp_i, fps[j])
        sim_matrix[i][j] = sim
        sim_matrix[j][i] = sim

# 输出矩阵
mol_names = [f"Mol_{i+1}" for i in range(n)]
sim_df = pd.DataFrame(sim_matrix, index=mol_names, columns=mol_names)
sim_df.to_csv(OUTPUT_MATRIX, encoding="utf-8-sig")

# 输出相似对
pairs = []
for i in range(n):
    for j in range(i+1, n):
        pairs.append([f"Mol_{i+1}", f"Mol_{j+1}", sim_matrix[i][j]])

pair_df = pd.DataFrame(pairs, columns=["Mol1", "Mol2", "Tanimoto"])
pair_df = pair_df.sort_values("Tanimoto", ascending=False)
pair_df.to_csv(OUTPUT_PAIRS, index=False)

print("✅ 计算完成！")
print(f"📊 相似矩阵：{OUTPUT_MATRIX}")
print(f"📋 相似分子对：{OUTPUT_PAIRS}")