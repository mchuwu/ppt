import pandas as pd
import numpy as np


def sientra_catalog(df):
    nom_d_col = []

    df.rename(columns = {
        "projection": 'nominal projection'
    }, inplace=True)
    
    for idx, (width, height) in enumerate(zip(df["width"], df["height"])):
        if str(width) != "nan" and str(height) == "nan":
            nom_d_col.append(width)
            df.ix[idx, "width"] = np.nan
        else:
            nom_d_col.append(np.nan)
    
    df.insert(loc=1, column="nominal diameter", value=nom_d_col)
    return df

def mentor_allergan_catalog(df):
    width_col = []

    df.rename(columns = {
        "min fill volume": "nominal fill volume",
        "min diameter": "nominal diameter",
        "min projection": "nominal projection"
    }, inplace=True)

    for idx, (nom_vol, max_vol, nom_d, nom_p, max_d, max_p, height) in enumerate(zip(df["nominal fill volume"], df["max fill volume"], df["nominal diameter"], df["nominal projection"], df["max diameter"], df["max projection"], df["height"])):
        if str(nom_vol) == "nan" and str(max_vol) != "nan":
            df.ix[idx, "nominal fill volume"] = max_vol
            df.ix[idx, "max fill volume"] = np.nan
        if str(nom_d) == "nan" and str(max_d) != "nan":
            df.ix[idx, "nominal diameter"] = max_d
            df.ix[idx, "max diameter"] = np.nan
        if str(nom_p) == "nan" and str(max_p) != "nan":
            df.ix[idx, "nominal projection"] = max_p
            df.ix[idx, "max projection"] = np.nan
        if str(max_d) != "nan" and str(height) != "nan":
            width_col.append(max_d)
            df.ix[idx, "nominal diameter"] = np.nan
        else:
            width_col.append(np.nan)
    
    df.insert(loc=7, column="width", value=width_col)
    return df

# mentor_df = pd.read_csv("../4 Product Catalogs/MENTOR catalog.csv", sep=",", header=0)
# mentor_df = mentor_catalog(mentor_df)
# mentor_df.to_csv("../4 Product Catalogs/MENTOR catalog.csv", sep=",", index=False)

# allergan_df = pd.read_csv("../4 Product Catalogs/ALLERGAN NATRELLE catalog.csv", sep=",", header=0)
# allergan_df = mentor_allergan_catalog(allergan_df)
# allergan_df.to_csv("../4 Product Catalogs/ALLERGAN NATRELLE catalog.csv", sep=",", index=False)

sientra_df = pd.read_csv("../4 Product Catalogs/SIENTRA catalog.csv", sep=",", header=0)
sientra_df = sientra_catalog(sientra_df)
sientra_df.to_csv("../4 Product Catalogs/SIENTRA catalog.csv", sep=",", index=False)
