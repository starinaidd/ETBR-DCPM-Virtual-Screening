import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, DataStructs

# ====================== 1. 你的7个分子（A组）======================

# ====================== 2. 配置文件路径 ======================
  # B组（721个分子），只需要SMILES一列
SMILES_COL_B = 0  # B组SMILES所在列（无表头填0）
TOP_N = 10  # 输出每个A分子的TOP-10最相似
OUTPUT_ALL = "all_similarity_results.csv"
OUTPUT_TOP = "top_similarity_per_A.csv"

# ====================== 3. 读取A组 ======================
from io import StringIO

df_A = pd.read_csv('D:\code\graduate\ETB_data\suyuan\ETB_7compounds.csv')
df_A = df_A.dropna().reset_index(drop=True)

mols_A = []
valid_A = []
for smi in df_A["SMILES"]:
    mol = Chem.MolFromSmiles(smi)
    if mol:
        mols_A.append(mol)
        valid_A.append(smi)

print(f"A组有效分子：{len(mols_A)}")

# ====================== 4. 读取B组（721个）======================
df_B = pd.read_csv("D:\code\graduate\ETB_data\suyuan\EDNRB_all_active.csv", header=None, names=["SMILES"])
df_B = df_B.dropna().reset_index(drop=True)

mols_B = []
valid_B = []
for smi in df_B["SMILES"]:
    mol = Chem.MolFromSmiles(smi)
    if mol:
        mols_B.append(mol)
        valid_B.append(smi)

print(f"B组有效分子：{len(mols_B)}")

# ====================== 5. 生成指纹 ======================
fps_A = [AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024) for m in mols_A]
fps_B = [AllChem.GetMorganFingerprintAsBitVect(m, 2, 1024) for m in mols_B]

# ====================== 6. 批量计算相似性 ======================
all_results = []
top_results = []

print("\n开始计算相似性...")
for a_idx, (smi_a, fp_a) in enumerate(zip(valid_A, fps_A)):
    a_name = f"A{a_idx + 1}"
    print(f"正在计算 {a_name} ...")

    sim_list = []
    for b_idx, (smi_b, fp_b) in enumerate(zip(valid_B, fps_B)):
        sim = DataStructs.TanimotoSimilarity(fp_a, fp_b)
        sim_list.append([a_name, smi_a, f"B{b_idx + 1}", smi_b, sim])

    # 保存全部结果
    all_results.extend(sim_list)

    # 取TOP-N
    sim_list_sorted = sorted(sim_list, key=lambda x: x[4], reverse=True)[:TOP_N]
    top_results.extend(sim_list_sorted)

# ====================== 7. 输出文件 ======================
df_all = pd.DataFrame(all_results, columns=[
    "A_name", "A_SMILES", "B_name", "B_SMILES", "Tanimoto"
])
df_all.to_csv(OUTPUT_ALL, index=False)

df_top = pd.DataFrame(top_results, columns=[
    "A_name", "A_SMILES", "B_name", "B_SMILES", "Tanimoto"
])
df_top.to_csv(OUTPUT_TOP, index=False)

print("\n✅ 计算完成！")
print(f"全部结果：{OUTPUT_ALL}")
print(f"TOP-{TOP_N} 结果：{OUTPUT_TOP}")