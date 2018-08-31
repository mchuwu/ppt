import pandas as pd
import numpy as np
import re
import xlsxwriter
import csv
from ast import literal_eval


# FORMAT VERSION MODEL NUMBER
def format_allergan(vmn):
    try:
        return vmn[:vmn.index('-')], vmn[vmn.index('-'):]
    except ValueError as e:
        raise ValueError("Allergan versionModelNumber format unknown: ", e)

def format_ideal(vmn):
    # return str(vmn)[:3], str(vmn)[3:]
    return np.nan, str(vmn)[:3]

def format_mentor(vmn):
    return (vmn[:3] + vmn[7:], vmn[3:7]) if not re.search("[A-Z]{4}", vmn) \
           else (re.search("[A-Z]{4}", vmn).group(), vmn.replace(re.search("[A-Z]{4}", vmn).group(), ""))

def format_sientra(vmn):
    try:
        return vmn[:vmn.index('-')] + vmn[re.search("[a-zA-Z]", vmn).start():], \
               vmn[vmn.index('-'):re.search("[a-zA-Z]", vmn).start()]
    except ValueError as e:
        raise ValueError("Sientra versionModelNumber format unknown: ", e)

# FORMAT SIZE TEXT
def format_mentor_st(dev_desc):
    st = re.search(r"\d{3,}[c]{2}", str(dev_desc)) # search pattern: "###cc" (at least three #s)
    if st:
        return st.group()[:3] + " " + st.group()[3:]
    else:
        raise ValueError(f"MENTOR device - no size text: {dev_desc}")

# def format_allergan_st(st):
#     return st

def format_ideal_st(size_text):
    st = re.search(r"\d{3,}\s[c]{2}", str(size_text)) # search pattern "### cc" (at least three #s)
    if st:
        return st.group()
    else:
        raise ValueError(f"IDEAL device - no size text: {size_text}")

def format_sientra_st(size_text):
    st = re.search(r"\d{3,}\s[c]{2}", str(size_text)) # search pattern "### cc" (at least three #s)
    if st:
        return st.group()
    else:
        raise ValueError(f"SIENTRA device - no size text: {size_text}")

def format_mentor_catnum(catnum, vmn):
    if not str(catnum)[1].isalpha():
        return catnum[:3] + "-" + catnum[3:]
    else:
        return catnum

def find_dimensions(cn, catnum, pdi):
    """[summary]
    
    :param cn: [description]
    :type cn: [type]
    :param catnum: [description]
    :type catnum: [type]
    :param pdi: [description]
    :type pdi: [type]
    :return: [description]
    :rtype: [type]
    """

    if cn == "MENTOR TEXAS L.P.":
        ddict = literal_eval(open("mentor_catalog_dict.txt").read())
    elif cn == "Allergan, Inc.":
        ddict = literal_eval(open("allergan_catalog_dict.txt").read())
    elif cn == "Sientra, Inc.":
        ddict = literal_eval(open("sientra_catalog_dict.txt").read())
    elif cn == "IDEAL IMPLANT INCORPORATED":
        ddict = literal_eval(open("ideal_catalog_dict.txt").read())

    for k1, v1 in ddict.items():
        for k2, v2 in v1.items():
            if v2 == "nan":
                ddict[k1][k2] = np.nan

    if catnum in ddict:
        return ddict[catnum]
    else:
        print(f"Unknown catalog number. Company: {cn}, Ctg#: {catnum}, PDI: {pdi}")
        return {'nfill': 'nan', 'mfill': 'nan', 'nd': 'nan', 'np': 'nan', 'md': 'nan', 'mp': 'nan', 'w': 'nan', 'h': 'nan'}


# MAIN FUNCTION
def formatted_data(df):
    sheet = df

    # remove diaphragm or injection dome rows
    anomalies = [i for i, bn in zip(sheet.index.values, sheet.brandName) if bn.find("Diaphragm Valve") != -1 or bn.find("Injection Domes") != -1]
    sheet = sheet.drop(anomalies)

    style_col = []
    rest_col = []
    new_catnum_col = []
    nomfill_col, maxfill_col, nomd_col, nomp_col, maxd_col, maxp_col, w_col, h_col = ([] for i in range(8))

    # take versionModelNumbers and extract main style (determined from looking at catalogs)
    for pdi, vmn, catnum, cn in zip(sheet["PrimaryDI"], sheet["versionModelNumber"], sheet["catalogNumber"], sheet["companyName"]):
        vmn = str(vmn) # convert all #'s to strings

        if cn == "MENTOR TEXAS L.P.":
            style, rest = format_mentor(vmn)
            style_col.append(style)
            rest_col.append(rest)
            new_catnum_col.append(format_mentor_catnum(catnum, vmn))
        elif cn == "Allergan, Inc.":
            style, rest = format_allergan(vmn)
            style_col.append(style)
            rest_col.append(rest)
            new_catnum_col.append(catnum)
        elif cn == "Sientra, Inc.":
            style, rest = format_sientra(vmn)
            style_col.append(style)
            rest_col.append(rest)
            new_catnum_col.append(catnum)
        elif cn == "IDEAL IMPLANT INCORPORATED":
            style, rest = format_ideal(vmn)
            style_col.append(style)
            rest_col.append(rest)
            new_catnum_col.append(catnum)
        else:
            raise ValueError(f"Unknown companyName found at PrimaryDI: {pdi}")

        ddict = find_dimensions(cn, new_catnum_col[-1], pdi)

        nomfill_col.append(ddict["nfill"])
        maxfill_col.append(ddict["mfill"])
        nomp_col   .append(ddict["np"   ])
        nomd_col   .append(ddict["nd"   ])
        maxd_col   .append(ddict["md"   ])
        maxp_col   .append(ddict["mp"   ])
        w_col      .append(ddict["w"    ])
        h_col      .append(ddict["h"    ])

    sheet["catalogNumber"] = new_catnum_col
    sheet["nominal fill volume"] = nomfill_col
    sheet["max fill volume"]     = maxfill_col
    sheet["nominal diameter"]    = nomp_col   
    sheet["nominal projection"]  = nomd_col   
    sheet["max diameter"]        = maxd_col   
    sheet["max projection"]      = maxp_col   
    sheet["width"]               = w_col      
    sheet["height"]              = h_col      
    # insert columns
    sheet.insert(loc=3, column="style", value=style_col)
    sheet.insert(loc=4, column="rest", value=rest_col)

    new_st_col = []
    for cn, size_text, dev_desc in zip(sheet["companyName"], sheet["sizeText"], sheet["deviceDescription"]):
        if cn == "MENTOR TEXAS L.P.":
            new_st_col.append(format_mentor_st(dev_desc))
        elif cn == "Allergan, Inc.":
            new_st_col.append(size_text) # already properly formatted
        elif cn == "Sientra, Inc.":
            new_st_col.append(format_sientra_st(size_text))
        elif cn == "IDEAL IMPLANT INCORPORATED":
            new_st_col.append(format_ideal_st(size_text))
        else:
            raise ValueError(f"""Improperly formatted text.\n 
                                cn: {cn}\n
                                size_text: {size_text}\n
                                dev_desc: {dev_desc}""")

    # replace column
    sheet["sizeText"] = new_st_col
    return sheet


if __name__ == "__main__":
    df = pd.read_excel("../2 Data/_test_merged_sheets.xlsx", sheet_name="relevant_cols")
    sheet = formatted_data(df)

    writer = pd.ExcelWriter("../2 Data/_test_formatted_data.xlsx", engine="xlsxwriter")
    sheet.to_excel(writer, index=False, sheet_name="formatted_cols")
    writer.save()
