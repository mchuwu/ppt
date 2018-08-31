import pandas as pd
import xlsxwriter
import os
import tempfile
import shutil
from functools import reduce


def make_sheets(gudid_folder):
    tempfile.TMPDIR = os.getcwd()
    tf = tempfile.NamedTemporaryFile(dir=tempfile.TMPDIR)

    files = ['device.txt',
             'deviceSizes.txt',
             'productCodes.txt',
             'identifiers.txt',
             'gmdnTerms.txt']
    sheets = []
    sheet_names = []
    for f in files:
        with open(f"{gudid_folder}/{f}") as file:
            try:
                sheet = pd.read_csv(file, sep="|", header=0)
                sheets.append(sheet)
                sheet_names.append(os.path.basename(file.name).replace('.txt',''))
            except pd.errors.EmptyDataError as e:
                print(f"make_sheets.py: {e}: {os.path.basename(file.name)}")
    
    writer = pd.ExcelWriter(tf, engine="xlsxwriter")
    for s, sn in zip(sheets, sheet_names):
        s.to_excel(writer, index=False, sheet_name=f"{sn}")
    writer.save()

    return tf

def merge_sheets(file):
    sheets_dict = pd.read_excel(file, sheet_name=None)

    df = reduce(lambda left, right: pd.merge(left, right, on="PrimaryDI", how="outer"), sheets_dict.values())
    return df

if __name__ == "__main__":
    tf = make_sheets("../2 Data/AccessGUDID_6-28-2018")
    df_final = merge_sheets(tf)
    
    writer = pd.ExcelWriter("../2 Data/_test_merged_sheets.xlsx", engine="xlsxwriter")
    df_final.to_excel(writer, index=False,sheet_name="relevant_cols")
    writer.save()
