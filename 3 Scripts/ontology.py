from owlready2 import *
import pandas as pd
import numpy as np
import textwrap
import os
from functools import partial, reduce
import time

onto_path.append("1 Ontology/")
onto = get_ontology("http://purl.obolibrary.org/BIO/breast_implant_ontology_base.owl").load()
onto.base_iri = "http://purl.obolibrary.org/BIO/"
bio = onto.get_namespace(onto.base_iri)

# replace various inconsistencies
def repl_stuff(s):
    repl_dict = {
        "Gel_Filled"     : "Gel-Filled",
        "gel_filled"     : "gel-filled",
        "Saline_Filled"  : "Saline-Filled",
        "saline_filled"  : "saline-filled",
        "Height_"        : "Height/",
        "Moderate_plus"  : "Moderate-plus",
        "moderate_plus"  : "moderate-plus",
        "HSC_plus"       : "HSC-plus",
        "Extra_full"     : "Extra-full",
        "extra_full"     : "extra full",
        "Ultra_high"     : "Ultra-high",
        "ultra_high"     : "ultra-high",
        "Low_plus"       : "Low-plus"  ,
        "low_plus"       : "low-plus"  ,
        "non_round"      : "non-round" ,
        "__"             : "-"         , # fix this in process_data
        "_"              : " "         ,
    }
    for key, value in repl_dict.items():
        if key in s:
            s = s.replace(key, value)
    return s

def main(onto_data: str) -> None:
    start = time.time()

    workbook = pd.read_excel(onto_data, sheet_name=None)

    u_sheet = workbook['unique']
    c_sheet = workbook['classifications']
    a_sheet = workbook['annotations']
    all_sheet = workbook['all']
    pma_sheet = workbook['pma']

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
    }

    # returns map with strings to execute and create classes dynamically
    #
    # first check if not 'nan'
    # then replace restricted classname chars e.g. ' ', '-'
    # then filter for `not value_test` as it is already in ontology_base 
    # then use corresponding lambda (in statement_funcs) to make executable string
    def exec_strings_map(sheet_col, statements_dict=statement_funcs, value_test=None):
        rplc_chars      = [' ', '-']                                  # replace these chars with '_' because Protege doesn't
                                                                    # support them
        rx              = '[' + re.escape(''.join(rplc_chars)) +  ']' # regex string pattern i.e. r'[ -]'
                                                                    # re.escape to allow ^, ], etc

        not_nothing= partial(filter, lambda x: x is not np.nan and x is not None and x != "")
        val_test = partial(filter, lambda x: x != value_test)

        def rplc_chars(s):
            s = s.replace(' ', '_').replace('-','__').replace('/','_')
            return s

        map_sub    = partial(map, lambda s: rplc_chars(s))

        mapto_execstr  = partial(map, statements_dict[sheet_col])

        return mapto_execstr(map_sub(val_test(not_nothing(u_sheet[sheet_col].values))))

    # returns a list with 
    def ex_strs(items):
        strs = []
        for key, _value in items:
            value_test = {
                'shell surface': 'smooth shell surface',
                'shape'        : 'round shape'         ,
                'filling'      : 'saline filling'
            }.get(key, None)

            strs.extend(exec_strings_map(f'{key}', value_test=value_test))
        return strs

    for s in ex_strs(statement_funcs.items()):
        exec(s)

    # manually add pma numbers 
    bio.Ideal_Implant_Structured_Breast_Implant.is_subject_device_of = [bio.P120011]
    bio.Mentor_MemoryGel_Silicone_Gel__Filled_Breast_Implant.is_subject_device_of = [bio.P030053]
    bio.Mentor_MemoryShape_Breast_Implant.is_subject_device_of = [bio.P060028]
    bio.Mentor_Saline__Filled_And_SPECTRUM_Breast_Implant.is_subject_device_of = [bio.P990075]
    bio.Natrelle_410_Highly_Cohesive_Anatomically_Shaped_Silicone__Filled_Breast_Implant.is_subject_device_of = [bio.P040046]
    bio.Natrelle_Saline__Filled_Breast_Implant.is_subject_device_of = [bio.P990074]
    bio.Natrelle_Silicone__Filled_Breast_Implant.is_subject_device_of = [bio.P020056]
    bio.Sientra_OPUS_Silicone_Gel_Breast_Implant.is_subject_device_of = [bio.P070004]

    # add pma information
    # no spaces/unallowed classname chars so no need to replace
    for idx, row in pma_sheet.iterrows():
        exec_str = textwrap.dedent(f"""
            # if not an original pma
            if '{row['SUPPLEMENTNUMBER']}' != 'nan':
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']} = type("{row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}", (bio.fda_pma_submission_supplement,), {{"namespace": bio}})

                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaApprovalOrderStatement = '''{row['AOSTATEMENT']}'''
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaGenericName = "{row['GENERICNAME']}"
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaSupplementType = "{row['SUPPLEMENTTYPE']}"
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaSupplementReason = "{row['SUPPLEMENTREASON']}"
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaTradeName = "{row['TRADENAME']}"
                
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaApplicant = "{row['APPLICANT']}"
                {row['PMANUMBER']}{row['SUPPLEMENTNUMBER']}.pmaApplicantAddress = "{row['STREET_1']} {row['STREET_2'] if row['STREET_2'] else ""}, " \
                                                                                    "{str(row['CITY']).title().replace(',', ' ')}, {row['STATE']} {row['ZIP']}"
            else:
                {row['PMANUMBER']}.pmaApprovalOrderStatement = '''{row['AOSTATEMENT']}'''
                {row['PMANUMBER']}.pmaGenericName = "{row['GENERICNAME']}"
                {row['PMANUMBER']}.pmaTradeName = "{row['TRADENAME']}"
                {row['PMANUMBER']}.pmaDocketNumber = "{row['DOCKETNUMBER']}"
                {row['PMANUMBER']}.pmaFedRegNoticeDate = "{row['FEDREGNOTICEDATE']}"

                {row['PMANUMBER']}.pmaApplicant = "{row['APPLICANT']}"
                {row['PMANUMBER']}.pmaApplicantAddress = "{row['STREET_1']} {row['STREET_2'] if row['STREET_2'] != 'nan' else ""}, {str(row['CITY']).title().replace(',', ' ')}, {row['STATE']} {row['ZIP']}"
        """).strip()
        try:
            exec(exec_str)
        except TypeError as e:
            raise TypeError("pma assignment error", e)



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
                    .replace('-','__')
                    .replace('/','_') if not k in nonrplc_cols else str(v)) for k, v in row.items()}

        exec_str = textwrap.dedent(f"""
            {row['fda pma number']}{row['fda pma number with supplement']} = type("{row['fda pma number']}{row['fda pma number with supplement']}", (bio.fda_pma_submission_supplement,), {{"namespace": bio}})

            has_manufacturer = bio.has_manufacturer
            has_filling = bio.has_filling
            has_shell = bio.has_shell
            has_profile = bio.has_profile
            has_shell_surface = bio.has_shell_surface
            has_shape = bio.has_shape
            has_product_code = bio.has_product_code
            is_subject_device_of = bio.is_subject_device_of

            {row['fda device name']}.has_shell.append(bio.{row['shell']})
            class {row['company brand name']}(bio.{row['fda device name']}):
                namespace = bio

            {row['company brand name']}.has_manufacturer.append(bio.{row['manufacturer']})

            if "{row['company brand name lower']}" != "nan":
                class {row['company brand name lower']}(bio.{row['company brand name']}):
                    namespace = bio

                {row['company brand name lower']}.has_profile.append(bio.{row['profile']})            

                class {row['device specific name']}(bio.{row['company brand name lower']}):
                    namespace = bio
            else: # IDEAL IMPLANT
                class {row['device specific name']}(bio.{row['company brand name']}):
                    namespace = bio
                {row['company brand name']}.has_profile.append(bio.{row['profile']})

            if 'spectrum' not in "{row['company brand name']}".lower():
                {row['company brand name']}.has_shell_surface.append(bio.{row['shell surface']})
            else:
                {row['company brand name lower']}.has_shell_surface.append(bio.{row['shell surface']})  

            # properties
            {row['device specific name']}.has_filling.append(bio.{row['filling']})
            {row['device specific name']}.has_shell_surface.append(bio.{row['shell surface']})
            {row['device specific name']}.has_shape.append(bio.{row['shape']})

            {row['device specific name']}.is_mentioned_in.append(bio.{row['fda pma number']}{row['fda pma number with supplement']})

            try:
                assert {row['nominal fill volume']}
                {row['device specific name']}.has_nominal_fill_volume.append({row['nominal fill volume']})
            except Exception:
                pass
            try:
                assert {row['max fill volume']}
                {row['device specific name']}.has_max_fill_volume.append({row['max fill volume']})
            except Exception:
                pass
            try:
                assert {row['nominal projection']}
                {row['device specific name']}.has_nominal_projection.append({row['nominal projection']})
            except Exception:
                pass
            try:
                assert {row['max projection']}
                {row['device specific name']}.has_max_projection.append({row['max projection']})
            except Exception:
                pass
            try:
                assert {row['nominal diameter']}
                {row['device specific name']}.has_nominal_diameter.append({row['nominal diameter']})
            except Exception:
                pass
            try:
                assert {row['max diameter']}
                {row['device specific name']}.has_max_diameter.append({row['max diameter']})
            except Exception:
                pass
            try:
                assert {row['width']}
                {row['device specific name']}.has_width.append({row['width']})
            except Exception:
                pass
            try:
                assert {row['height']}
                {row['device specific name']}.has_height.append({row['height']})
            except Exception:
                pass


            # annotations
            {row['device specific name']}.catalogNumber = "{row['catalogNumber']}"
            {row['device specific name']}.versionModelNumber = "{row['versionModelNumber']}"
            {row['device specific name']}.devicePublishDate = "{row['devicePublishDate']}"
            {row['device specific name']}.deviceDescription = "{row['deviceDescription']}"
            {row['device specific name']}.deviceID = "{row['deviceId']}"
            {row['device specific name']}.gudidLink = "{row['GUDIDLink']}"
            {row['device specific name']}.pmaLink = "{row['PMALink']}"
            {row['device specific name']}.gmdnPTName = "{row['gmdnPTName']}"
            {row['device specific name']}.gmdnPTDefinition = "{row['gmdnPTDefinition']}"
        """).strip() # change maximum fill volume to max fill volume
        try:
            exec(exec_str)
        except TypeError as e:
            raise TypeError(f"{exec_str}", e)


    # recreate fda pma links for fda_pma_submissions
    for pma in onto.search(is_a=onto.fda_pma_submission):
        pma.pmaLink = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma.name}"

    # recreate fda pma links for all breast_implant_devices"
    for clss in onto.classes():
        if clss.is_subject_device_of:
            pma = clss.is_subject_device_of[0]
            clss.pmaLink = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma.name}"

    for supplm in onto.search(is_a=onto.fda_pma_submission_supplement):
        supplm.pmaLink = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={supplm.name}"
        supplm.name = supplm.name[:7] + '/' + supplm.name[7:]
        supplm.mentions = [eval(f"bio.{supplm.name[:7]}")]

    # GLOBAL COUNTER
    ctr = 0

    # refactor classes
    for c in onto.classes():
        name = repl_stuff(c.name)
        c.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", c.iri)
        c.label = name
        ctr += 1

    # refactor properties
    for p in onto.properties():
        label = p.name.replace('_',' ')
        p.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", p.iri)
        p.label = label
        ctr += 1

    # refactor individuals
    for i in onto.individuals():
        label = i.name.replace('_',' ')
        i.iri = re.sub(r'BIO/.*$', f"BIO/BIO_{str(ctr).zfill(7)}", i.iri)
        i.label = label
        ctr += 1

    onto.save("1 Ontology/test1.owl")

    end = time.time()
    print(f"Time: {end - start}")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('--onto_data_path', dest='onto_data_path', type=str, nargs=1, default=['2 Data/onto_data.xlsx'],
                        help='File path for ontology data Excel file.')
    args = parser.parse_args()

    onto_data_path = args.onto_data_path[0]
    main(onto_data_path)
