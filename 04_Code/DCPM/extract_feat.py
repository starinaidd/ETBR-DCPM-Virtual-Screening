import os

from permmol.api import batch_extarct_feature, init_inference
from rdkit import RDLogger

if __name__ == "__main__":
    RDLogger.DisableLog("rdApp.*")
    # Directory of CSV files including SMILES column.
    csv_dir = "./csv"
    # Directory to save feature files (pickle binary files).
    save_dir = "./sar/feats"
    # Set new start CSV file when extracting loop crashed.
    # CSV files will be loaded one by one according file name when `breakpoint_csv` is `None`.
    breakpoint_csv = None
    csv_list = sorted(filter(lambda s: s.endswith(".csv"), os.listdir(csv_dir)))
    init_inference(device_id=0)
    if not breakpoint_csv is None:
        cal_flag = False
    else:
        cal_flag = True

    for csv in csv_list:
        if not cal_flag:
            if breakpoint_csv == csv:
                cal_flag = True
                continue

        else:
            csv_path = os.path.join(csv_dir, csv)
            csv_name = os.path.splitext(csv)[0]
            save_path = os.path.join(save_dir, f"{csv_name}.pkl")

            batch_extarct_feature(
                data_path=csv_path,
                save_path=save_path,
                max_len=301,
                batch_size=256,
                # Columns name of smiles column
                usecols=["smiles"]
            )
