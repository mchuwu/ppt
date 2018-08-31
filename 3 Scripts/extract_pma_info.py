import pandas as pd
import numpy as np

def extract_info(df):
    pma_df = df

    bi_pmas = [
        "P990075",
        "P990074",
        "P120011",
        "P030053",
        "P060028",
        "P070004",
        "P020056",
        "P040046",
    ]

    pma_df = pma_df.loc[lambda x: x['PMANUMBER'].map(lambda pma: pma in bi_pmas)]

    return pma_df

if __name__ == '__main__':
    df = pd.read_csv('2 Data/PMA_8-3-2018/pma.txt', sep='|', encoding = "ISO-8859-1")

    df = extract_info(df)
    df.to_csv('2 Data/_test_pma_extraction.csv', index=False)
