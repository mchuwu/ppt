from owlready2 import *
import pandas as pd
import numpy as np
import textwrap
import os
from functools import partial, reduce


onto_path.append("1 Ontology/")
onto = get_ontology("http://purl.obolibrary.org/BIO/breast_implant_ontology_base.owl").load()
onto.base_iri = "http://purl.obolibrary.org/BIO/"
bio = onto.get_namespace(onto.base_iri)
workbook = pd.read_excel("2 Data/onto_data.xlsx", sheet_name=None)


u_sheet = workbook['unique']
c_sheet = workbook['classifications']
a_sheet = workbook['annotations']
all_sheet = workbook['all']

statement_funcs = {
    'manufacturer'   : lambda m:       f'{m} = type("{m}", (bio.breast_implant_manufacturer,), {{"namespace": bio}})',
    'fda device name': lambda dn:      f'{dn} = type("{dn}", (bio.breast_implant_device,), {{"namespace": bio}})',
    'productCode'    : lambda pc:      f'{pc} = bio.breast_implant_product_code("{pc}")',
    'filling'        : lambda f:       f'{f} = type("{f}", (bio.silicone_gel_filling,), {{"namespace": bio}})',
    'shell'          : lambda shl:     f'{shl} = type("{shl}", (bio.breast_implant_shell,), {{"namespace": bio}})',
    'shell surface'  : lambda shl_sfc: f'{shl_sfc} = type("{shl_sfc}", (bio.textured_shell_surface,), {{"namespace": bio}})',
    'shape'          : lambda shp:     f'{shp} = type("{shp}", (bio.non_round_shape,), {{"namespace": bio}})',
    'profile'        : lambda pfl:     f'{pfl} = type("{pfl}", (bio.breast_implant_profile,), {{"namespace": bio}})',
    'style'          : lambda styl:    f'style_{styl} = type("style_{styl}", (bio.breast_implant_style,), {{"namespace": bio}})',
    'fda pma number' : lambda fpn:     f'{fpn} = type("{fpn}", (bio.fda_pma_submission,), {{"namespace": bio}})',
    'fda pma number with supplement': lambda fpss: f'{fpss} = type("{fpss}", (bio.fda_pma_submission_supplement,), {{"namespace": bio}})',
}

def exec_strings_list(sheet_col, statements_dict=statement_funcs, value_test=None):
    rplc_chars      = [' ', '-']                                  # replace these chars with '_' because Protege doesn't
                                                                  # support them
    rx              = '[' + re.escape(''.join(rplc_chars)) +  ']' # regex string pattern i.e. r'[ -]'
                                                                  # re.escape to allow ^, ], etc

    not_nothing= partial(filter, lambda x: x is not np.nan and x is not None and x != "")
    val_test = partial(filter, lambda x: x != value_test)
    map_sub    = partial(map, lambda s: re.sub(pattern=rx, repl='_', string=s))
    mapto_execstr  = partial(map, statements_dict[sheet_col])

    return mapto_execstr(map_sub(val_test(not_nothing(u_sheet[sheet_col].values))))

# def main():
strs = []
for key, _value in statement_funcs.items():
    value_test = {
        'shell surface': 'smooth shell surface',
        'shape'        : 'round shape'         ,
        'filling'      : 'saline filling'
    }.get(key, None)

    strs.extend(list(exec_strings_list(f'{key}', value_test=value_test)))

for s in strs:
    exec(s)

# manually add pma numbers 
bio.Ideal_Implant_Structured_Breast_Implant.is_subject_device_of = [bio.P120011]
bio.Mentor_MemoryGel_Silicone_Gel_Filled_Breast_Implant.is_subject_device_of = [bio.P030053]
bio.Mentor_MemoryShape_Breast_Implant.is_subject_device_of = [bio.P060028]
bio.Mentor_Saline_Filled_And_SPECTRUM_Breast_Implant.is_subject_device_of = [bio.P990075]
bio.Natrelle_410_Highly_Cohesive_Anatomically_Shaped_Silicone_Filled_Breast_Implant.is_subject_device_of = [bio.P040046]
bio.Natrelle_Saline_Filled_Breast_Implant.is_subject_device_of = [bio.P990074]
bio.Natrelle_Silicone_Filled_Breast_Implant.is_subject_device_of = [bio.P020056]
bio.Sientra_OPUS_Silicone_Gel_Breast_Implant.is_subject_device_of = [bio.P070004]



# assign individual devices
# STRUCTURE
# device
# - FDA name
# -- company brand name
# --- company brand name lower + catalogNumber
#
#
for idx, row in all_sheet.iterrows():
    nonrplc_cols = list(a_sheet.columns.values)
    row = {k:(str(v).replace(' ', '_')
                   .replace('-','_')
                   .replace('/','_') if not k in nonrplc_cols else str(v)) for k, v in row.items()}

    exec_str = textwrap.dedent(f"""
        has_manufacturer = bio.has_manufacturer
        has_filling = bio.has_filling
        has_shell = bio.has_shell
        has_profile = bio.has_profile
        has_shell_surface = bio.has_shell_surface
        has_shape = bio.has_shape
        has_product_code = bio.has_product_code
        is_subject_device_of = bio.is_subject_device_of

        class {row['company brand name']}(bio.{row['fda device name']}):
            namespace = bio

        {row['company brand name']}.has_manufacturer.append(bio.{row['manufacturer']})
        {row['company brand name']}.has_shell.append(bio.{row['shell']})

        if "{row['company brand name lower']}" != "nan":
            class {row['company brand name lower']}(bio.{row['company brand name']}):
                namespace = bio

            {row['company brand name lower']}.has_profile.append(bio.{row['profile']})
            
            class {row['device specific name']}(bio.{row['company brand name lower']}):
                namespace = bio
        else:
            class {row['device specific name']}(bio.{row['company brand name']}):
                namespace = bio

        #classes
        {row['device specific name']}.has_filling.append(bio.{row['filling']})
        {row['device specific name']}.has_shell_surface.append(bio.{row['shell surface']})
        {row['device specific name']}.has_shape.append(bio.{row['shape']})

        # {row['device specific name']}.is_subject_device_of.append(bio.{row['fda pma number']})
        {row['device specific name']}.has_pma_supplement.append(bio.{row['fda pma number with supplement']})

        # annotations
        {row['device specific name']}.catalogNumber = "{row['catalogNumber']}"
        {row['device specific name']}.versionModelNumber = "{row['versionModelNumber']}"
        {row['device specific name']}.devicePublishDate = "{row['devicePublishDate']}"
        {row['device specific name']}.deviceID = "{row['deviceId']}"
        {row['device specific name']}.gudidLink = "{row['GUDIDLink']}"
        {row['device specific name']}.pmaLink = "{row['PMALink']}"
        {row['device specific name']}.gmdnPTName = "{row['gmdnPTName']}"
        {row['device specific name']}.gmdnPTDefinition = "{row['gmdnPTDefinition']}"
    """).strip()
    try:
        exec(exec_str)
    except TypeError as e:
        raise TypeError(f"{exec_str}", e)

# recreate fda pma links for outer class
# recreate fda pma subject devices
for pma in onto.search(is_a=onto.fda_pma_submission):
    pma.pmaLink = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma.name}"

for supplm in onto.search(is_a=onto.fda_pma_submission_supplement):
    supplm.pmaLink = ""

# GLOBAL COUNTER
ctr = 0

# replace various inconsistencies
def repl_stuff(s):
    repl_dict = {
        "Gel Filled"     : "Gel-Filled",
        "gel filled"     : "gel-filled",
        "Saline Filled"  : "Saline-Filled",
        "saline filled"  : "saline-filled",
        "Height "        : "Height/",
        "Moderate plus"  : "Moderate-plus",
        "moderate plus"  : "moderate-plus",
        "HSC plus"       : "HSC-plus",
        "Extra full"     : "Extra-full",
        "extra full"     : "extra full",
        "Ultra high"     : "Ultra-high",
        "ultra high"     : "ultra-high",
        "__"             : "_"          # fix this in process_data
    }
    for key, value in repl_dict.items():
        if key in s:
            s = s.replace(key, value)
    return s

# refactor classes
for c in onto.classes():
    c.label = repl_stuff(c.name.replace('_',' '))
    c.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", c.iri)
    ctr += 1

# refactor properties
for p in onto.properties():
    p.label = p.name.replace('_',' ')
    p.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", p.iri)
    ctr += 1

for i in onto.individuals():
    i.label = i.name.replace('_',' ')
    i.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", i.iri)
    ctr += 1

onto.save("1 Ontology/test1.owl")
