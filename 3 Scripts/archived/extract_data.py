import pandas as pd
import numpy as np
from ast import literal_eval
import xlsxwriter


def extract_manufacturer(company_name):
    company_name = company_name.lower()

    if "mentor" in company_name:
        return "Mentor"
    elif "allergan" in company_name:
        return "Allergan"
    elif "ideal" in company_name:
        return "Ideal Implant"
    elif "sientra" in company_name:
        return "Sientra"
    else:
        raise ValueError(f"Unknown Manufacturer {company_name}")


def extract_profile_filling_shape_surface_mentor(dev_desc, product_code, brand):
    info = {
        "profile": "",
        "filling": "",
        "shape"  : "",
        "surface": ""
    }
    profiles = ["moderate plus profile xtra",
                "moderate classic",
                "moderate plus",
                "moderate",
                "high profile xtra",
                "ultra high",
                "high"]
    # shapes = ["round", "teardrop"]
    # surfaces = ["smooth", "siltex"]
    dev_desc = dev_desc.lower()
    brand = brand.lower()

    error_str = "Unknown"
    if product_code == "FTR":
        for p in profiles:
            if p in dev_desc:
                info["profile"] =  "MENTOR " + p + (" profile" if not "profile" in p else "")
                break
        if info["profile"] == "":
            error_str += f" profile: {dev_desc},"
        if "memorygel" in brand or "memorygel xtra" in brand:
            info["shape"] = "round shape"
            info["filling"] = "MENTOR MemoryGel silicone gel filling"
            if "smooth" in dev_desc:
                info["surface"] = "smooth shell surface"
            elif "siltex" in dev_desc:
                info["surface"] = "MENTOR SILTEX textured shell surface"
            else:
                error_str += f" surface: {dev_desc}"
        elif "memoryshape" in brand:
            info["shape"] = "MENTOR teardrop shape"
            info["filling"] = "MENTOR MemoryShape silicone gel filling"
            info["surface"] = "MENTOR SILTEX textured shell surface"
        else:
            error_str += f" shape: {brand}, surface: {dev_desc},"
    elif product_code == "FWM":
        for p in profiles:
            if p in brand:
                info["profile"] =  "MENTOR " + p + (" profile" if not "profile" in p else "")
                break

        # source: http://www.mentorwwllc.com/Documents/saline_spectrum_ppi.pdf
        if "spectrum" in brand:
            if "round" in brand:
                info["profile"] = "MENTOR moderate profile"
            elif "contour profile" in brand:
                info["profile"] = "MENTOR high profile"
                
        if info["profile"] == "":
            error_str += f" profile: {dev_desc},"

        info["filling"] = "saline filling"

        if "round" in brand:
            info["shape"] = "round shape"
        elif "contour profile" in brand:
            info["shape"] = "MENTOR CONTOUR PROFILE shape"
        else:
            error_str += f" shape: {brand}"

        if "smooth" in brand:
                info["surface"] = "smooth shell surface"
        elif "siltex" in brand:
            info["surface"] = "MENTOR SILTEX textured shell surface"
        else:
            error_str += f" surface: {brand}"
    else:
        error_str += f" product code: {product_code}"

    if error_str != "Unknown":
        raise ValueError(error_str)
    
    return info


def extract_profile_filling_shape_surface_allergan(style):
    styles_dict = literal_eval(open("natrelle_style_dict.txt").read())
    info = {
        "profile": "",
        "filling": "",
        "shape"  : "",
        "surface": ""
    }

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


def extract_profile_filling_shape_surface_sientra(style):
    styles_dict = literal_eval(open("sientra_style_dict.txt").read())
    info = {
        "profile": "",
        "filling": "",
        "shape"  : "",
        "surface": ""
    }

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
def extract_profile_filling_shape_surface_ideal():
    info = {
        "profile": "IDEAL IMPLANT high profile",
        "filling": "saline filling",
        "shape"  : "round shape",
        "surface": "smooth shell surface"
    }

    return info

def di_to_gudidurl(id):
    id = str(id).zfill(14)
    return f"https://accessgudid.nlm.nih.gov/devices/{id}"


# Ideal Saline-Filled Breast Implant (Premarket Application Number: P120011)
# Allergan (formerly called McGhan and Inamed) Medical RTV Saline-Filled Breast Implant (Premarket application number: P990074)
# Mentor Saline-Filled and Spectrum Breast Implants (Premarket application number: P990075)
# Allergan Natrelle (Premarket application number: P020056) (Approved November 2006)
# Allergan Natrelle 410 Highly Cohesive Anatomically Shaped Silicone-Filled Breast Implants (Premarket application number: P040046) (Approved February 2013)
# Mentor MemoryGel (Premarket application number: P030053) (Approved November 2006)
# Mentor MemoryShape (Premarket application number: P060028) (Approved June 2013)
# Sientra’s Silicone Gel Breast Implants (Premarket application number: P070004) (Approved March 2012)
def assign_fda_pma_name(brand_name):
    fdaname_dict = {
        "natrelle saline-filled": "Natrelle Saline-Filled Breast Implant",
        "natrelle inspira cohesive": "Natrelle Inspira Cohesive Breast Implant",
        "natrelle inspira softtouch": "Natrelle Inspira SoftTouch Breast Implant",
        "natrelle inspira": "Natrelle Inspira Breast Implant",
        "natrelle silicone-filled": "Natrelle Silicone-Filled Breast Implant",
        "natrelle 410": "Natrelle 410 Highly Cohesive Anatomically Shaped Silicone-Filled Breast Implant",
        "mentor memorygel": "MemoryGel Silicone Gel-Filled Breast Implant",
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

def assign_company_name(brand_name, shell_surface):
    companyname_dict = {
        "natrelle saline-filled": "NATRELLE Saline-Filled Breast Implant",
        "natrelle inspira cohesive": "NATRELLE Inspira Cohesive Breast Implant",
        "natrelle inspira softtouch": "NATRELLE Inspira SoftTouch Breast Implant",
        "natrelle inspira": "NATRELLE Inspira Responsive Breast Implant",
        "natrelle silicone-filled": "NATRELLE Silicone-Filled Breast Implant",
        "natrelle 410": "NATRELLE 410 Breast Implant",
        "mentor siltex": "MENTOR SILTEX Saline-Filled Breast Implant",
        "mentor smooth round": "MENTOR Smooth Round Saline-Filled Breast Implant",
        "mentor memorygel xtra": {"smooth round": "MENTOR MemoryGel Xtra Smooth Round Breast Implant", "siltex round": "MENTOR MemoryGel Xtra SILTEX Round Breast Implant"},
        "mentor memorygel": {"smooth round": "MENTOR MemoryGel Smooth Round Breast Implant", "siltex round": "MENTOR MemoryGel SILTEX Round Breast Implant"},
        "mentor memoryshape": "MENTOR MemoryShape Breast Implant",
        "sientra silicone": "SIENTRA OPUS Silicone Gel Breast Implant",
        "ideal implant": "IDEAL IMPLANT Structured Breast Implant"
    }
    brand_name = brand_name.lower()
    for key, value in companyname_dict.items():
        if key in brand_name and key == "mentor memorygel xtra":
            if "siltex" in shell_surface:
                return value["siltex round"]
            else:
                return value["smooth round"]
        elif key in brand_name and key == "mentor memorygel":
            if "siltex" in shell_surface:
                return value["siltex round"]
            else:
                return value["smooth round"]
        elif key in brand_name:
            return value
    
    return brand_name

def assign_fda_pma(fda_dn):
    pma_dict = {
        "natrelle saline-filled": "P990074",
        "natrelle inspira cohesive": "P020056",   # S031
        "natrelle inspira softtouch": "P020056",  # S034
        "natrelle inspira": "P020056",            # S036
        "natrelle silicone-filled": "P020056",
        "natrelle 410": "P040046",
        "memorygel silicone": "P030053",
        "mentor memoryshape": "P060028",
        "mentor saline-filled and spectrum": "P990075",
        "sientra opus": "P070004",
        "ideal implant": "P120011"
    }
    fda_dn = fda_dn.lower()
    pma, pma_link = "", ""
    for key, value in pma_dict.items():
        if key in fda_dn:
            pma = value
            if key == "natrelle inspira cohesive":
                pma_link = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma}S031"
            elif key == "natrelle inspira softtouch":
                pma_link = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma}S034"
            elif key == "natrelle inspira":
                pma_link = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma}S036"
            else:
                pma_link = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma}"

    if pma == "":
        raise ValueError(f"unable to assign fda_pma: {fda_dn}")

    return {"pma": pma, "pma_link": pma_link}

def extracted_data(df):
    sheet = df
    # classifications
    # PrimaryDI | manufacturer | GUDID brand | company brand | FDA device name | style | filling | profile | shape | shell | shell surface | product code | sizeText

    # annotations
    # PrimaryDI | versionModelNumber | catalogNumber | deviceID (GUDID) | gmdnPTName | gmdnPTDefinition

    # classification columns
    p_di_col, manufacturer_col, gd_brand_col, company_brand_col, fda_name_col, style_col, filling_col, profile_col, shape_col, shell_col, shell_surface_col, product_code_col, size_col = ([] for i in range(13))
    nomfill_col, maxfill_col, nomd_col, nomp_col, maxd_col, maxp_col, w_col, h_col = ([] for i in range(8))
    # pma annotation columns - uses fda_name_col so it is included here
    fda_pma_col = []
    fda_pma_link_col = []
    # assign classification column values
    for p_di, c_name, brand, p_code, dev_desc, style, size, nomfill, maxfill, nomd, nomp, maxd, maxp, w, h in zip(sheet['PrimaryDI'],
    
                                                                  sheet['companyName'],
                                                                  sheet['brandName'],
                                                                  sheet['productCode'],
                                                                  sheet['deviceDescription'],
                                                                  sheet['style'],
                                                                  sheet['sizeText'],
                                                                  sheet["nominal fill volume"] ,
                                                                  sheet["max fill volume"]    ,  
                                                                  sheet["nominal diameter"]   ,  
                                                                  sheet["nominal projection"] ,  
                                                                  sheet["max diameter"]       ,  
                                                                  sheet["max projection"]     ,  
                                                                  sheet["width"]              ,  
                                                                  sheet["height"]
                                                                  ):
                                                                                

        p_di_col.append(p_di)
        manufacturer_col.append(extract_manufacturer(c_name))
        gd_brand_col.append(brand)

        fda_name_col.append(assign_fda_pma_name(brand))
        fda_pma_col.append(assign_fda_pma(fda_name_col[-1])["pma"])
        fda_pma_link_col.append(assign_fda_pma(fda_name_col[-1])["pma_link"])

        style_col.append(style)
        shell_col.append("silicone shell")

        brand = brand.lower()
        info = {}
        if "natrelle" in brand:
            info = extract_profile_filling_shape_surface_allergan(style)
        elif "mentor" in brand:
            info = extract_profile_filling_shape_surface_mentor(dev_desc, p_code, brand)
        elif "sientra" in brand:
            info = extract_profile_filling_shape_surface_sientra(style)
        else:
            info = extract_profile_filling_shape_surface_ideal()

        profile_col.append(info["profile"])
        filling_col.append(info["filling"])
        shape_col.append(info["shape"])
        shell_surface_col.append(info["surface"])


        product_code_col.append(p_code)
        size_col.append(size)

        nomfill_col.append(nomfill) if nomfill != 'nan' else nomfill_col.append(None)
        maxfill_col.append(maxfill) if maxfill != 'nan' else maxfill_col.append(None)
        nomp_col   .append(nomp   ) if nomp    != 'nan' else nomp_col.append(None)
        nomd_col   .append(nomd   ) if nomd    != 'nan' else nomd_col.append(None)
        maxd_col   .append(maxd   ) if maxd    != 'nan' else maxd_col.append(None)
        maxp_col   .append(maxp   ) if maxp    != 'nan' else maxp_col.append(None)
        w_col      .append(w      ) if w       != 'nan' else w_col.append(None)
        h_col      .append(h      ) if h       != 'nan' else h_col.append(None)

    # annotation columns
    vmn_col, dpd_col, ctg_num_col, dev_desc_col, dev_di_col, gudid_link_col, gmdn_pt_name_col, gmdn_pt_def_col = ([] for i in range(8))
    # assign annotation column values
    for vmn, dpd, ctg_num, dev_desc, dev_id, gmdn_pt_name, gmdn_pt_def in zip(sheet["versionModelNumber"], sheet["devicePublishDate"], sheet["catalogNumber"], sheet["deviceDescription"], sheet["deviceId"], sheet["gmdnPTName"], sheet["gmdnPTDefinition"]):
        vmn_col.append(vmn)
        dpd_col.append(dpd)
        ctg_num_col.append(ctg_num)
        dev_desc_col.append(dev_desc)
        dev_di_col.append(dev_id)
        gudid_link_col.append(di_to_gudidurl(dev_id))
        gmdn_pt_name_col.append(gmdn_pt_name)
        gmdn_pt_def_col.append(gmdn_pt_def)

    classifications_sheet = pd.DataFrame(np.column_stack([p_di_col, manufacturer_col, gd_brand_col, company_brand_col, fda_name_col, style_col, filling_col, profile_col, size_col, shape_col, shell_col, shell_surface_col, product_code_col,nomfill_col, maxfill_col, nomd_col, nomp_col, maxd_col, maxp_col, w_col, h_col]), \
                                        columns=['PrimaryDI', 'manufacturer', 'GUDID brand', 'company brand', 'FDA device name', 'style', 'filling', 'profile', 'size', 'shape', 'shell', 'shell surface', 'product code','nominal fill volume', 'max fill volume', 'nominal diameter', 'nominal projection', 'max diameter', 'max projection', 'width', 'height'])
    
    annotations_sheet = pd.DataFrame(np.column_stack([p_di_col, vmn_col, ctg_num_col, dev_desc_col, dev_di_col, gudid_link_col, fda_pma_col, fda_pma_link_col, dpd_col, gmdn_pt_name_col, gmdn_pt_def_col]), \
                                    columns=['PrimaryDI', 'versionModelNumber', 'catalogNumber', 'deviceDescription', 'deviceDI', 'GUDIDLink', 'FDA PMA', 'FDA PMA Link', 'devicePublishDate', 'gmdnPTName', 'gmdnPTDefinition'])
    
    def append_none(np_arr, maxlen):
        while len(np_arr) != maxlen:
            np_arr = np.append(np_arr, None)
        
        return np_arr
    
    # Unique Data
    u_mcol  = pd.unique(classifications_sheet["manufacturer"])
    u_bcol  = pd.unique(classifications_sheet["GUDID brand"])
    u_cbcol  = pd.unique(classifications_sheet["company brand"])
    u_fdncol  = pd.unique(classifications_sheet["FDA device name"])
    u_scol  = pd.unique(classifications_sheet["style"])
    u_fcol  = pd.unique(classifications_sheet["filling"])
    u_pcol  = pd.unique(classifications_sheet["profile"])
    u_szcol = pd.unique(classifications_sheet["size"])
    u_spcol = pd.unique(classifications_sheet["shape"])
    u_slcol = pd.unique(classifications_sheet["shell"])
    u_sscol = pd.unique(classifications_sheet["shell surface"])
    u_pccol = pd.unique(classifications_sheet["product code"])

    maxlen = max(len(u_mcol), len(u_bcol), len(u_cbcol), len(u_fdncol),
                  len(u_scol), len(u_fcol),
                  len(u_pcol), len(u_szcol),
                  len(u_spcol), len(u_slcol),
                  len(u_sscol), len(u_pccol))

    u_mcol  = append_none(u_mcol , maxlen)
    u_bcol  = append_none(u_bcol , maxlen)
    u_cbcol = append_none(u_cbcol, maxlen)
    u_fdncol= append_none(u_fdncol, maxlen)
    u_scol  = append_none(u_scol , maxlen)
    u_fcol  = append_none(u_fcol , maxlen)
    u_pcol  = append_none(u_pcol , maxlen)
    u_szcol = append_none(u_szcol, maxlen)
    u_spcol = append_none(u_spcol, maxlen)
    u_slcol = append_none(u_slcol, maxlen)
    u_sscol = append_none(u_sscol, maxlen)
    u_pccol = append_none(u_pccol, maxlen)

    unique_sheet = pd.DataFrame(np.column_stack([u_mcol,u_bcol,u_cbcol,u_fdncol,u_scol,u_fcol,u_pcol,u_szcol,u_spcol,u_slcol,u_sscol,u_pccol]), \
                                columns=['manufacturer', 'GUDID brand', 'company brand', 'FDA device name', 'style', 'filling', 'profile', 'size', 'shape', 'shell', 'shell surface', 'product code'])

    sheets_final = {
        "classifications sheet": classifications_sheet,
        "annotations sheet": annotations_sheet,
        "unique sheet": unique_sheet
    }
    return sheets_final

if __name__ == "__main__":
    sheet = pd.read_excel("../2 Data/_test_formatted_data.xlsx", sheet_name="formatted_cols")
    sheets_final = extracted_data(sheet)

    writer = pd.ExcelWriter("../2 Data/_test_extracted_data.xlsx", engine="xlsxwriter")
    writer2 = pd.ExcelWriter("../2 Data/_test_extracted_unique.xlsx", engine="xlsxwriter")
    sheets_final["classifications sheet"].to_excel(writer, index=False, sheet_name="classifications sheet")
    sheets_final["annotations sheet"].to_excel(writer, index=False, sheet_name="annotations sheet")
    sheets_final["unique sheet"].to_excel(writer2, index=False, sheet_name="annotations sheet")
    writer.save()
    writer2.save()
