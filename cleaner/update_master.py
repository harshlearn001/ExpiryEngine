import os
import pandas as pd
import glob
from config.settings import RAW_DIR, MASTER_DIR

def update_master():
    raw_files = glob.glob(f"{RAW_DIR}/*.csv")

    for rf in raw_files:
        sym = os.path.basename(rf).split("_")[0]
        master_path = f"{MASTER_DIR}/{sym}.csv"

        df_new = pd.read_csv(rf)

        if os.path.exists(master_path):
            df_master = pd.read_csv(master_path)
            df_final = pd.concat([df_master, df_new]).drop_duplicates()
        else:
            df_final = df_new

        df_final.to_csv(master_path, index=False)
        print(f"✔ updated master: {sym}")

if __name__ == "__main__":
    update_master()
