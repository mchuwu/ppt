import pandas as pd
import numpy as np
import re
import xlsxwriter
import csv
from ast import literal_eval
from functools import partial, reduce
import time

from merge_gudid import make_sheets, merge_sheets
from extract_pma_info import extract_info


def is_breast_implant(brand_name):
    '''Checks if a device in the data really is a breast implant.
    This is needed because there are errors in which data inputted were incorrect.
    
    :param brand_name: Breast implant brandName
    :type brand_name: str
    :return: A Boolean describing whether a device is a breast implant or not
    :rtype: Boolean
    '''

    if 'Diaphragm Valve' in brand_name or 'Injection Domes' in brand_name:
        return False
    else:
        return True

def fill_catnum(company_name, vmn):
    return {
        'MENTOR TEXAS L.P.': (f'{vmn[:3]}-{vmn[3:]}') if not str(vmn)[1].isalpha() else str(vmn),
        'IDEAL IMPLANT INCORPORATED': str(vmn)[:3]
    }.get(company_name, vmn) # default value is catalog number

def extract_manufacturer(company_name):
    '''Return a designated manufacturer name given GUDID companyName
    
    :param company_name: GUDID companyName
    :type company_name: str
    :raises ValueError: If company_name is not in one of the four designated,
    raises an error. 
    :return: A designated manufacturer name, i.e. 'Mentor', 'Allergan', 'Ideal Implant','Sientra'
    :rtype: str
    '''

    company_name = company_name.lower()

    if 'mentor' in company_name:
        return 'Mentor'
    elif 'allergan' in company_name:
        return 'Allergan'
    elif 'ideal' in company_name:
        return 'Ideal Implant'
    elif 'sientra' in company_name:
        return 'Sientra'
    else:
        raise ValueError(f'Unknown Manufacturer {company_name}')   

def extract_pfss(company_name, style, dev_desc, brand):
    """Return dictionary with profile, shape, filling and surface information
    
    :param style: Breast implant assigned style
    :type style: str
    :param dev_desc: Breast implant deviceDescription
    :type dev_desc: str
    :param brand: Breast implant brandName
    :type brand: str
    :param company_name: Breast implant companyName
    :type company_name: str
    :return: Returns dictionary with profile, shape, filling and surface information
    :rtype: dict
    """

    if company_name == 'Allergan, Inc.':
        return extract_pfss_allergan(style)
    elif company_name == 'IDEAL IMPLANT INCORPORATED':
        return extract_pfss_ideal()
    elif company_name == 'MENTOR TEXAS L.P.':
        return extract_pfss_mentor(dev_desc, brand)
    elif company_name == 'Sientra, Inc.':
        return extract_pfss_sientra(style)
    else:
        raise ValueError(f'unknown company name {company_name}')

def extract_style(company_name, vmn):
    '''Return breast implant style given versionModelNumber and companyName
    
    :param vmn: versionModelNumber
    :type vmn: str
    :param company_name: companyName
    :type company_name: str
    :return: breast implant style
    :rtype: str or float
    '''

    lazy = {}
    lazy['Allergan, Inc.'            ] = allergan_style
    lazy['IDEAL IMPLANT INCORPORATED'] = ideal_style
    lazy['MENTOR TEXAS L.P.'         ] = mentor_style
    lazy['Sientra, Inc.'             ] = sientra_style
    return lazy[company_name](vmn)

def extract_pfss_mentor(dev_desc, brand):
    info = {
        'profile': '',
        'filling': '',
        'shape'  : '',
        'surface': ''
    }
    profiles = ['moderate plus profile xtra',
                'moderate classic',
                'moderate plus',
                'moderate',
                'high profile xtra',
                'ultra high',
                'high']
    brand, dev_desc = brand.lower().strip(), dev_desc.lower().strip()

    for p in profiles:
        if p in dev_desc or p in brand:
            info["profile"] =  "MENTOR " + p + (" profile" if not "profile" in p else "")
            break

    if 'memorygel' in brand or 'memorygel xtra' in brand:
        info["shape"] = "round shape"
        info["filling"] = "MENTOR MemoryGel silicone gel filling"
    elif 'memoryshape' in brand:
        info["shape"] = "MENTOR teardrop shape"
        info["filling"] = "MENTOR MemoryShape silicone gel filling"
        info["surface"] = "MENTOR SILTEX textured shell surface"
    elif 'spectrum' in brand:
        info["filling"] = 'saline filling'

        if "round" in brand:
            info["profile"] = "MENTOR moderate profile"
            info["shape"] = "round shape"
        elif "contour profile" in brand:
            info["profile"] = "MENTOR high profile"
            info["shape"] = "MENTOR CONTOUR PROFILE shape"
    else:
        info['filling'] = 'saline filling'

        if "round" in brand:
            info["shape"] = "round shape"
        elif "contour profile" in brand:
            info["shape"] = "MENTOR CONTOUR PROFILE shape"

    if "smooth" in brand or "smooth" in dev_desc:
        info["surface"] = "smooth shell surface"
    elif "siltex" in brand or "siltex" in dev_desc:
        info["surface"] = "MENTOR SILTEX textured shell surface"

    if info['profile'] == "": raise ValueError(f"{brand}")
    for _key, value in info.items():
        if value == "": raise ValueError(f"MENTOR info assignment error: {brand}, {dev_desc}, {info.items()}")

    return info

def extract_pfss_allergan(style):
    styles_dict = literal_eval(open("2 Data/natrelle_style_dict.txt").read())
    info = {
        "profile": "",
        "filling": "",
        "shape"  : "",
        "surface": "",}

    style = str(style)
    if style in styles_dict:
        info["profile"] = "NATRELLE " + styles_dict[style]["profile"]
        info["filling"] = "NATRELLE " + styles_dict[style]["filling"
                           ] if "silicone" in styles_dict[style]["filling"
                           ] else styles_dict[style]["filling"] 
        info["shape"] = "NATRELLE " + styles_dict[style]['shape'
                           ] if 'Anatomical' in styles_dict[style]['shape'
                           ] else styles_dict[style]['shape']
        info['surface'] = ('NATRELLE ' + styles_dict[style]['surface'
                           ] if 'BIOCELL' in styles_dict[style]['surface'
                           ] or 'textured' in styles_dict[style]['surface'
                           ] else styles_dict[style]['surface'])
    else:
        raise ValueError(f"Unknown NATRELLE style: {style}")

    return info

def extract_pfss_sientra(style):
    styles_dict = literal_eval(open("2 Data/sientra_style_dict.txt").read())
    info = {
        "profile": "",
        "filling": "",
        "shape"  : "",
        "surface": "",}

    if style in styles_dict:
        info["profile"] = "SIENTRA " + styles_dict[style]["profile"]
        info["filling"] = "SIENTRA " + styles_dict[style]["filling"
                           ] if "silicone" in styles_dict[style]["filling"
                           ] else "saline filling"
        info["shape"] = "SIENTRA " + styles_dict[style]['shape'
                           ] if 'Shaped' in styles_dict[style]['shape'
                           ] else styles_dict[style]['shape']
        info['surface'] = 'SIENTRA ' + styles_dict[style]['surface'
                           ] if 'textured' in styles_dict[style]['surface'
                           ] else styles_dict[style]['surface']
    else:
        raise ValueError(f"Unknown SIENTRA style: {style}")
    
    return info

# Ideal Implant only has one "profile": high profile
# source: https://www.yorkyates.com/plastic-surgery-procedures-utah/breast-surgery-utah/breast-augmentation/ideal-implant-breast-implant/
# Ideal Implant is also only round and smooth and has only saline filling
def extract_pfss_ideal():
    info = {
        "profile": "IDEAL IMPLANT high profile",
        "filling": "saline filling",
        "shape"  : "round shape",
        "surface": "smooth shell surface"
    }

    return info

def allergan_style(vmn):
    '''Return Allergan implant style given versionModelNumber
    
    :param vmn: versionModelNumber
    :type vmn: str
    :return: A company designated breast implant style
    :rtype: str
    '''

    return vmn[:vmn.index('-')]

def ideal_style(vmn):
    '''Ideal Implant does not assign style, so this function
    returns None

    :param vmn: versionModelNumber
    :type vmn: str
    :return: None
    :rtype: float
    '''

    return None

def mentor_style(vmn):
    '''Return Mentor implant style given versionModelNumber
    
    :param vmn: versionModelNumber
    :type vmn: str
    :return: A non-company designated breast implant style
    :rtype: str
    '''

    # vmn = str(vmn)
    # return (vmn[:3] + vmn[7:]
    #          if not re.search('[A-Z]{4}', vmn)
    #          else re.search('[A-Z]{4}', vmn).group())
    return None

def sientra_style(vmn):
    '''Return Sientra implant style given versionModelNumber
    
    :param vmn: versionModelNumber
    :type vmn: str
    :return: A non-company designated breast implant style
    :rtype: str
    '''

    return vmn[:vmn.index('-')] + vmn[re.search('[a-zA-Z]', vmn).start():]

def assign_fda_pma_name(brand_name):
    fdaname_dict = {
        "natrelle saline-filled": "Natrelle Saline-Filled Breast Implant",
        "natrelle inspira cohesive": "Natrelle Silicone-Filled Breast Implant",
        "natrelle inspira softtouch": "Natrelle Silicone-Filled Breast Implant",
        "natrelle inspira": "Natrelle Silicone-Filled Breast Implant",
        "natrelle silicone-filled": "Natrelle Silicone-Filled Breast Implant",
        "natrelle 410": "Natrelle 410 Highly Cohesive Anatomically Shaped Silicone-Filled Breast Implant",
        "mentor memorygel": "Mentor MemoryGel Silicone Gel-Filled Breast Implant",
        "mentor memoryshape": "Mentor MemoryShape Breast Implant",
        "mentor siltex": "Mentor Saline-Filled And SPECTRUM Breast Implant",
        "mentor smooth": "Mentor Saline-Filled And SPECTRUM Breast Implant",
        "sientra silicone": "Sientra OPUS Silicone Gel Breast Implant",
        "ideal implant": "Ideal Implant Structured Breast Implant"
    }
    brand_name = brand_name.lower()
    for key, value in fdaname_dict.items():
        if key in brand_name:
            return value
    
    raise ValueError(f"unable to assign fda name from brand name: {brand_name}")

def assign_fda_pma(brand_name):
    pma_dict = {
        "natrelle saline-filled": "P990074",
        "natrelle inspira cohesive": "P020056",  
        "natrelle inspira softtouch": "P020056", 
        "natrelle inspira": "P020056",           
        "natrelle silicone-filled": "P020056",
        "natrelle 410": "P040046",
        "mentor memorygel": "P030053",
        "mentor memoryshape": "P060028",
        "mentor siltex": "P990075",
        "mentor smooth": "P990075",
        "sientra silicone": "P070004",
        "ideal implant": "P120011"
    }
    brand_name = brand_name.lower()
    pma, pma_supp, pma_link = "", "", ""
    for key, value in pma_dict.items():
        if key in brand_name:
            pma = value

            pma_supp = {
                "natrelle saline-filled": "S041",
                "natrelle inspira cohesive": "S031", 
                "natrelle inspira softtouch": "S034",
                "natrelle inspira": "S036",          
                "natrelle silicone-filled": "S045",
                "natrelle 410": "S027",
                "mentor memorygel": "S047",
                "mentor memoryshape": "S029",
                "mentor siltex": "S044",
                "mentor smooth": "S044",
                "sientra silicone": "S014",
                "ideal implant": "S011"
            }[key]
            
            pma_link = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma}"

    if pma == "":
        raise ValueError(f"unable to assign fda_pma: {brand_name}")

    return pma, pma_supp, pma_link

def id_to_gudidurl(id):
    id = str(id).zfill(14)
    return f"https://accessgudid.nlm.nih.gov/devices/{id}"

def fmt_sizetext(company_name, size_text, dev_desc):
    size_text, dev_desc = str(size_text).lower().strip(), str(dev_desc).lower().strip()

    if company_name == 'MENTOR TEXAS L.P.':
        st = re.search(r"\d{3,}[c]{2}", dev_desc)
        return st.group()[:3] + " " + st.group()[3:]
    elif company_name == 'IDEAL IMPLANT INCORPORATED':
        return re.search(r"\d{3,}\s[c]{2}", size_text).group()
    elif company_name == 'Sientra, Inc.':
        return re.search(r"\d{3,}\s[c]{2}", size_text).group()
    else:
        return size_text

def assign_company_device_name(brand_name, shell_surface, filling, shape):
    companyname_dict = {
        'natrelle saline-filled'        : {'smooth': 'NATRELLE Saline-Filled Smooth Round Breast Implant',
                                            'textured': 'NATRELLE Saline-Filled Textured Breast Implant'},
        'natrelle inspira cohesive'     : {'smooth': 'NATRELLE INSPIRA Cohesive Smooth Round Breast Implant',
                                            'textured': 'NATRELLE INSPIRA Cohesive Textured Breast Implant'},
        'natrelle inspira softtouch'    : {'smooth': 'NATRELLE INSPIRA SoftTouch Smooth Round Breast Implant',
                                           'textured': 'NATRELLE INSPIRA SoftTouch Textured Breast Implant'}, 
        'natrelle inspira'              : {'smooth': 'NATRELLE INSPIRA Responsive Smooth Round Breast Implant',
                                           'textured': 'NATRELLE INSPIRA Responsive Textured Breast Implant'},
        "natrelle silicone-filled"      : {'smooth': 'NATRELLE Silicone Gel-Filled Smooth Round Breast Implant',
                                           'textured': 'NATRELLE Silicone Gel-Filled BIOCELL Textured Round Breast Implant'},
        "natrelle 410": "NATRELLE 410 Anatomical Gel Breast Implant",
        "spectrum": "MENTOR SPECTRUM Saline-Filled Post-Operatively Adjustable Breast Implant",
        "mentor smooth round": "MENTOR Smooth Round Saline-Filled Breast Implant",
        "mentor siltex": "MENTOR SILTEX Saline-Filled Breast Implant",
        "mentor memorygel xtra": {"smooth round": "MENTOR MemoryGel Silicone Gel-Filled Xtra Smooth Round Breast Implant", "siltex round": "MENTOR MemoryGel Silicone Gel-Filled Xtra SILTEX Round Breast Implant"},
        "mentor memorygel": {"smooth round": "MENTOR MemoryGel Silicone Gel-Filled Smooth Round Breast Implant", "siltex round": "MENTOR MemoryGel Silicone Gel-Filled SILTEX Round Breast Implant"},
        "mentor memoryshape": "MENTOR MemoryShape Breast Implant",
        "sientra silicone": "", # PLACEHOLDER, WE USIN OTHER COLS
        "ideal implant": "IDEAL IMPLANT Structured Breast Implant"
    }
    brand_name, shell_surface = brand_name.lower(), shell_surface.lower()
    for key, value in companyname_dict.items():
        if key in brand_name and (key == "mentor memorygel xtra" or key == "mentor memorygel"):
            if "siltex" in shell_surface:
                return value["siltex round"]
            else:
                return value["smooth round"]
        elif key in brand_name and ('natrelle saline' in key or 'natrelle inspira' in key or 'natrelle silicone-filled' in key):
            if 'smooth' in shell_surface:
                return value['smooth']
            else:
                return value['textured']
        elif key in brand_name and 'sientra' in key:
            filling = filling.replace('SIENTRA', '').replace('silicone gel filling', '').strip()

            shell_surface = shell_surface.replace('SIENTRA', '').replace('shell surface','').strip().capitalize().replace('Sientra', '').strip().capitalize()

            shape = shape.replace('SIENTRA', '').replace('shape', '').strip().title()

            return f"SIENTRA {filling} {shell_surface} {shape} Breast Implant"
        elif key in brand_name:
            return value
    
    return brand_name

def assign_company_device_name_lower(brand_name, company_device_name, profile, style, dev_desc):
    company_device_name = company_device_name.replace('Breast Implant', '').strip()
    
    lower_name = ""

    companies = ['MENTOR', 'NATRELLE', 'IDEAL IMPLANT', 'SIENTRA']
    for c in companies:
        if c in profile:
            profile = profile.replace(c, '').strip().capitalize()
            break

    if 'NATRELLE' in company_device_name:
        if str(style) in ['10', '15', '20', '40', '45', '110', '115', '120']:
            lower_name =  f"{company_device_name} Style {style} {profile}"
        elif '410' in company_device_name:
            height = {
                'L': 'Low Height',
                'M': 'Moderate Height',
                'F': 'Full Height',
            }[style[0]]
            lower_name =  f"{company_device_name} {height}/{profile}"
        else:
            lower_name =  f"{company_device_name} {profile}"
    elif 'MENTOR' in company_device_name:
        if 'SPECTRUM' in company_device_name:
            lower_name =  f"{brand_name} {profile}" # return brand name instead of POST-OPERATIVELY...
        elif 'mentor smooth round' in company_device_name:
            # remove ending filling
            company_device_name = company_device_name.replace('Saline Filled', '').strip()
            lower_name =  f"{company_device_name} {profile}"
        elif 'memorygel' in company_device_name:
            lower_name =  f"{company_device_name} {profile}"
        else: # MemoryGel
            heights = ['Tall Height', 'Low Height', 'Medium Height']
            height = ""
            for h in heights:
                if h in dev_desc:
                    height = h
            lower_name =  f"{company_device_name} {height} {profile}"
    elif 'SIENTRA' in company_device_name:
        lower_name =  f"{company_device_name} {profile}"
    elif 'IDEAL' in company_device_name:
        lower_name =  None

    # If lower_name is not None, i.e. ideal device (has no lower_name)
    if lower_name:
        return lower_name.replace("profile", "Profile") + " Breast Implant"
    else:
        return lower_name

def assign_individual_name(company_lower, catnum):
    if company_lower != None:
        return f"{company_lower} {catnum}"
    else: # ideal implant devices
        return f"IDEAL IMPLANT Structured Breast Implant {catnum}"

def assign_dimensions(cn, catnum, pdi):
    """Assign individual device dimensions
    
    :param cn: companyName
    :type cn: string
    :param catnum: catalogNumber
    :type catnum: string
    :param pdi: PrimaryDI
    :type pdi: string
    :return: Dictionary with nominal fill, max fill, nom diameter, nom projection,
    max diameter, max projection
    :rtype: dict
    """


    if cn == "MENTOR TEXAS L.P.":
        ddict = literal_eval(open("2 Data/mentor_catalog_dict.txt").read())
    elif cn == "Allergan, Inc.":
        ddict = literal_eval(open("2 Data/natrelle_catalog_dict.txt").read())
    elif cn == "Sientra, Inc.":
        ddict = literal_eval(open("2 Data/sientra_catalog_dict.txt").read())
    elif cn == "IDEAL IMPLANT INCORPORATED":
        ddict = literal_eval(open("2 Data/ideal_catalog_dict.txt").read())

    for k1, v1 in ddict.items():
        for k2, v2 in v1.items():
            if v2 == "nan":
                ddict[k1][k2] = None

    if catnum in ddict:
        return ddict[catnum]
    else:
        with open("2 Data/unknown ctg nums.txt", "a+") as f:
            f.write(f"Unknown catalog number. Company: {cn}, Ctg#: {catnum}, PDI: {pdi}\n")
        return {'nfill': None, 'mfill': None, 'nd': None, 'np': None, 'md': None, 'mp': None, 'w': None, 'h': None}

def process_data(dataframe):
    '''Processes a pandas.DataFrame containing GUDID breast implant data.

    
    :param dataframe: GUDID breast implant merged dataframe
    :type dataframe: pandas.DataFrame
    '''

    df = dataframe

    df = df.loc[lambda x: x['brandName'].map(lambda bn: is_breast_implant(bn)), :]

    # Step 1
    step1_cols = {
        'catalogNumber'  : list(map(fill_catnum, df['companyName'].values, df['versionModelNumber'].values)),
        'manufacturer'   : list(map(extract_manufacturer, df['companyName'].values)),
        'style'          : list(map(extract_style, df['companyName'].values, df['versionModelNumber'].values)),
        'GUDIDLink'      : list(map(id_to_gudidurl, df['deviceId'].values)),
        'sizeText'       : list(map(fmt_sizetext, df['companyName'].values, df['sizeText'].values, df['deviceDescription'].values)),
    }
    df = df.assign(**{col: val for col, val in step1_cols.items()})
    
    # Step 2
    step2_cols = ['profile','filling','shape','surface']
    pfss_dicts = list(map(extract_pfss, df['companyName'].values, df['style'].values, df['deviceDescription'].values, df['brandName'].values))
    df = df.assign(**{col: [dct[col] for dct in pfss_dicts] for col in step2_cols})

    # Step 2.5
    df = df.assign(**{'shell': ['silicone shell' for x in range(df.shape[0])],
                      'companyBrandName' : list(map(assign_company_device_name, df['brandName'], df['surface'], df['filling'], df['shape']))})

    df = df.assign(**{'companyBrandNameLower': list(map(assign_company_device_name_lower, df['brandName'], df['companyBrandName'], df['profile'], df['style'], df['deviceDescription']))})

    df = df.assign(**{'deviceSpecificName': list(map(assign_individual_name, df['companyBrandNameLower'], df['catalogNumber']))})

    # Step 3
    step3_cols = {'fdaDeviceName': list(map(assign_fda_pma_name, df['brandName']))}
    df = df.assign(**{col: val for col, val in step3_cols.items()})

    # Step 4
    step4_cols = ['fdaPmaNumber','fdaPmaNumberWithSupp', 'PMALink']
    pma_tups = list(map(assign_fda_pma, df['brandName']))
    df = df.assign(**{col: [tup[idx] for tup in pma_tups] for idx, col in enumerate(step4_cols)})
    
    # Step 5
    step5_cols = ['nominal fill volume',
                  'maximum fill volume',
                  'nominal projection' ,
                  'nominal diameter'   ,
                  'max projection'     ,
                  'max diameter'       ,
                  'width'              ,
                  'height'             ,]
    dimension_dicts = list(map(assign_dimensions, df['companyName'], df['catalogNumber'], df['PrimaryDI']))
    df = df.assign(**{col: [dct.get(col) for dct in dimension_dicts] for col in step5_cols})

    df['brandName'].apply(lambda x: x.strip())

    return df

def main(gudid_fldr: str, pma_flpth: str) -> None:
    gudid_folder= gudid_fldr
    pma_file_path = pma_flpth

    start = time.time()
    print("CREATING GUDID SHEETS...", end="")
    gudid_file = make_sheets(gudid_folder)
    t1 = time.time()
 
    print(f" time: {t1 - start:.7f} \nMERGING RELEVANT COLUMNS...", end="")
    ms_df = merge_sheets(gudid_file)
    t2 = time.time()

    print(f" time: {t2 - t1:.7f} \nPROCESSING DATA...", end="")
    df = process_data(ms_df)
    df = df.rename(index=str,columns={'brandName': 'gudid brand name',
                                      'fdaDeviceName': 'fda device name',
                                      'fdaPmaNumber': 'fda pma number',
                                      'fdaPmaNumberWithSupp': 'fda pma number with supplement',
                                      'companyBrandName': 'company brand name',
                                      'companyBrandNameLower': 'company brand name lower',
                                      'deviceSpecificName': 'device specific name',
                                      'surface': 'shell surface',
                                      'maximum fill volume': 'max fill volume'})
    
    rel_cols = ['PrimaryDI'          ,
                'manufacturer'       ,
                'fda device name'    ,
                'company brand name' ,
                'company brand name lower',
                'device specific name',
                'gudid brand name'   ,
                'style'              ,
                'profile'            ,
                'filling'            ,
                'shape'              ,
                'shell'              ,
                'shell surface'      ,
                'productCode'        ,
                'fda pma number'         ,
                'fda pma number with supplement'     ,
                'nominal fill volume',
                'max fill volume',
                'nominal projection' ,
                'nominal diameter'   ,
                'max projection'     ,
                'max diameter'       ,
                'width'              ,
                'height'             ,
                'devicePublishDate' ,
                'versionModelNumber',
                'catalogNumber'     ,
                'deviceDescription' ,
                'sizeText'          ,
                'deviceId'          ,
                'GUDIDLink'         ,
                'PMALink'           ,
                'gmdnPTName'        ,
                'gmdnPTDefinition'  ,
                ]
    df = df[rel_cols].reindex(columns=rel_cols)

    class_cols = [
        'PrimaryDI'         ,
        'manufacturer'      ,
        'fda device name'   ,
        'company brand name',
        'company brand name lower',
        'device specific name',
        'gudid brand name'  ,
        'style'             ,
        'profile'           ,
        'filling'           ,
        'shape'             ,
        'shell'             ,
        'shell surface'     ,
        'productCode'       ,
        'fda pma number'         ,
        'fda pma number with supplement'     ,
        'nominal fill volume',
        'max fill volume',
        'nominal projection' ,
        'nominal diameter'   ,
        'max projection'     ,
        'max diameter'       ,
        'width'              ,
        'height'             ,
    ]
    class_df = df[class_cols]

    annot_cols = [
        'PrimaryDI'         ,
        'devicePublishDate' ,
        'versionModelNumber',
        'catalogNumber'     ,
        'deviceDescription' ,
        'sizeText'          ,
        'deviceId'          ,
        'GUDIDLink'         ,
        'PMALink'           ,
        'gmdnPTName'        ,
        'gmdnPTDefinition'  ,
    ]
    annot_df = df[annot_cols]

    unique_cols = {}
    unique_cols_exclude = ['PrimaryDI']
    for c_col in class_cols:
        if not c_col in unique_cols_exclude:
            unique_cols[c_col] = pd.unique(class_df[c_col])
    
    maxlen = max(map(len, unique_cols.values()))

    def append_none(arr, ml=maxlen):
        while len(arr) != ml:
                arr = np.append(arr, None)    
        return arr

    unique_cols = {key:append_none(value) for key, value in unique_cols.items()}
    unique_df = pd.DataFrame.from_dict(unique_cols)

    pma_df = pd.read_csv(pma_file_path, sep='|', encoding = "ISO-8859-1")
    pma_df = extract_info(pma_df)

    t3 = time.time()
    print(f" time: {t3 - t2:.7f}\nWRITING TO EXCEL", end="")

    import pandas.io.formats.excel
    pandas.io.formats.excel.header_style = None

    data_writer = pd.ExcelWriter('2 Data/onto_data.xlsx', engine='xlsxwriter')

    class_df.to_excel(data_writer, index=False, sheet_name='classifications')
    annot_df.to_excel(data_writer, index=False, sheet_name='annotations')
    df.to_excel(data_writer, index=False, sheet_name='all')

    unique_df.to_excel(data_writer, index=False, sheet_name='unique')

    pma_df.to_excel(data_writer, index=False, sheet_name='pma')

    data_wkbk = data_writer.book

    class_sheet = data_writer.sheets['classifications']
    annot_sheet = data_writer.sheets['annotations']
    all_sheet = data_writer.sheets['all']
    unique_sheet = data_writer.sheets['unique']
    pma_sheet = data_writer.sheets['pma']

    head_fmt ={
        "align": "center",
        "bg_color": "#e3ecff",
        "bold": True,
        "font_size": 15,
        "font_color": "#1F497D",
        "bottom" : 2,
        "bottom_color": "#1F497D",
    }
    data_head = data_wkbk.add_format(head_fmt)

    # set header format
    class_sheet. set_row(0, 20.25, data_head)
    annot_sheet. set_row(0, 20.25, data_head)
    all_sheet.   set_row(0, 20.25, data_head)
    unique_sheet.set_row(0, 20.25, data_head)
    pma_sheet   .set_row(0, 20.25, data_head)

    # freeze top pane
    class_sheet.freeze_panes(1,0)
    annot_sheet.freeze_panes(1,0)
    all_sheet.freeze_panes(1,0)
    unique_sheet.freeze_panes(1,0)
    pma_sheet.freeze_panes(1,0)

    # set column widths
    def get_col_widths(df):
        return [max(list(map(len, map(str, df[col].values))) + [len(str(col)) + 5]) for col in df.columns]

    for i, width in enumerate(get_col_widths(class_df)):
        class_sheet.set_column(i, i, width)
    for i, width in enumerate(get_col_widths(annot_df)):
        annot_sheet.set_column(i, i, width)
    for i, width in enumerate(get_col_widths(df)):
        all_sheet.set_column(i, i, width)
    for i, width in enumerate(get_col_widths(unique_df)):
        unique_sheet.set_column(i, i, width)
    for i, width in enumerate(get_col_widths(pma_df)):
        pma_sheet.set_column(i, i, width)

    data_writer.save()

    t4 = time.time()
    print(f" time: {t4 - t3:.7f}")


    print(f"Done. Total elapsed time: {t4 - start:.7f}")

import argparse
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create onto_data.xlsx file in `../2 Data/` with relevant' \
                                                 ' ontology info from updated FDA PMA info and GUDID info')
    parser.add_argument('--gudid_folder_path', dest='gudid_folder_path', type=str, nargs=1,
                        default=['2 Data/AccessGUDID_6-28-2018'], help='GUDID folder path (default: `2 Data/AccessGUDID_6-28-2018`)')
    parser.add_argument('--pma_file_path', dest='pma_file_path', type=str, nargs=1,
                        default=['2 Data/PMA_8-3-2018/pma.txt'], help='File path of FDA PMA information (default: `2 Data/PMA_8-3-2018/pma.txt`)')

    args = parser.parse_args()

    gudid_folder = args.gudid_folder_path[0]
    pma_file_path = args.pma_file_path[0]

    main(gudid_folder, pma_file_path)
