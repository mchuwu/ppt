import pandas as pd
import numpy as np


def reference_dictionary(compname):
    if compname == "mentor":
        df = pd.read_csv("2 Data/Product Catalogs/MENTOR catalog.csv")
    elif compname == "allergan":
        df = pd.read_csv("2 Data/Product Catalogs/ALLERGAN NATRELLE catalog.csv")
    elif compname == "sientra":
        df = pd.read_csv("2 Data/Product Catalogs/SIENTRA catalog.csv")
    else: # compname == "IDEAL IMPLANT INCORPORATED":
        df = pd.read_csv("2 Data/Product Catalogs/IDEAL catalog.csv")    

    ref_dict = {}
    for ref, nfill, mfill, nd, np, md, mp, w, h in zip(df["reference"],
                                                       df["nominal fill volume"],
                                                       df["max fill volume"],
                                                       df["nominal diameter"],
                                                       df["nominal projection"],
                                                       df["max diameter"],
                                                       df["max projection"],
                                                       df["width"],
                                                       df["height"]):
        ref_dict[str(ref)] = {
            'nominal fill volume': nfill if str(nfill) != "nan" else "nan",
            'maximum fill volume': mfill if str(mfill) != "nan" else "nan",
            'nominal projection' : nd    if str(nd   ) != "nan" else "nan",
            'nominal diameter'   : np    if str(np   ) != "nan" else "nan",
            'max projection'     : md    if str(md   ) != "nan" else "nan",
            'max diameter'       : mp    if str(mp   ) != "nan" else "nan",
            'width'              : w     if str(w    ) != "nan" else "nan",
            'height'             : h     if str(h    ) != "nan" else "nan",            
        }
    return ref_dict

for company in ['sientra', 'allergan', 'mentor', 'ideal']:
    ref_dict = reference_dictionary(f"{company}")
    with open(f"2 Data/{company}_catalog_dict.txt", "w") as f:
        f.write(str(ref_dict))

