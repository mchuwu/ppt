import sys
import os
from merge_gudid import make_sheets, merge_sheets
from format_data import formatted_data
from extract_data import extracted_data
import pandas as pd
import pandas.io.formats.excel
import numpy as np
import xlsxwriter
import time


def main(gudid_folder="../2 Data/AccessGUDID_6-28-2018"):
    start = time.time()
    print("CREATING GUDID SHEETS...", end="")
    gudid_file = make_sheets(gudid_folder)
    t1 = time.time()
    print(f" time: {t1 - start:.7f} \nMERGING RELEVANT COLUMNS...", end="")
    ms_df = merge_sheets(gudid_file)
    t2 = time.time()
    print(f" time: {t2 - t1:.7f} \nFORMATTING DATA...", end="")
    fd_df = formatted_data(ms_df)
    t3 = time.time()
    print(f" time: {t3 - t2:.7f}\nEXTRACTING DATA...", end="")
    ed_df = extracted_data(fd_df)
    t4 = time.time()
    print(f" time: {t4 - t3:.7f}\nWRITING TO \"../2 Data/...\"", end="")

    pandas.io.formats.excel.header_style = None

    writer1 = pd.ExcelWriter("../2 Data/ontology_data.xlsx", engine="xlsxwriter")
    writer2 = pd.ExcelWriter("../2 Data/ontology_data_unique.xlsx", engine="xlsxwriter")
    ed_df["classifications sheet"].to_excel(writer1, index=False, sheet_name="classifications sheet")
    ed_df["annotations sheet"].to_excel(writer1, index=False,sheet_name="annotations sheet")
    ed_df["unique sheet"].to_excel(writer2, index=False,sheet_name="unique sheet")

    workbook1 = writer1.book
    workbook2 = writer2.book

    c_sheet = writer1.sheets["classifications sheet"]
    a_sheet = writer1.sheets["annotations sheet"]
    u_sheet = writer2.sheets["unique sheet"]

    c_sheet.freeze_panes(1, 0)
    a_sheet.freeze_panes(1, 0)
    u_sheet.freeze_panes(1, 0)

    head_fmt1 = workbook1.add_format({
        "align": "center",
        "bg_color": "#e3ecff",
        "bold": True,
        "font_size": 15,
        "font_color": "#1F497D",
        "bottom" : 2,
        "bottom_color": "#1F497D",
    })
    head_fmt2 = workbook2.add_format({
        "align": "center",
        "bg_color": "#e3ecff",
        "bold": True,
        "font_size": 15,
        "font_color": "#1F497D",
        "bottom" : 2,
        "bottom_color": "#1F497D",
    })

    c_sheet.set_column('A:A', 37.5 )
    c_sheet.set_column('B:B', 17   )
    c_sheet.set_column('C:C', 45   )
    c_sheet.set_column('D:D', 45   )
    c_sheet.set_column('E:E', 45   )
    c_sheet.set_column('F:F', 8.0  )
    c_sheet.set_column('G:G', 45.5 )
    c_sheet.set_column('H:H', 33   )
    c_sheet.set_column('I:I', 8    )
    c_sheet.set_column('J:J', 32   )
    c_sheet.set_column('K:K', 12   )
    c_sheet.set_column('L:L', 37   )
    c_sheet.set_column('M:M', 16   )

    a_sheet.set_column('A:A', 37.5 )
    a_sheet.set_column('B:B', 27   )
    a_sheet.set_column('C:C', 19   )
    a_sheet.set_column('D:D', 75   )
    a_sheet.set_column('E:E', 14.5 )
    a_sheet.set_column('F:F', 14.5 )
    a_sheet.set_column('G:G', 14.5 )
    a_sheet.set_column('H:H', 18 )
    a_sheet.set_column('I:I', 20   )
    a_sheet.set_column('J:J', 30   )
    a_sheet.set_column('K:K', 254  )

    u_sheet.set_column('A:A', 17   )
    u_sheet.set_column('B:B', 45   )
    u_sheet.set_column('C:C', 51   )
    u_sheet.set_column('D:D', 60   )
    u_sheet.set_column('E:E', 8    )
    u_sheet.set_column('F:F', 44   )
    u_sheet.set_column('G:G', 32   )
    u_sheet.set_column('H:H', 12   )
    u_sheet.set_column('I:I', 37   )
    u_sheet.set_column('J:J', 16   )
    u_sheet.set_column('K:K', 37   )
    u_sheet.set_column('L:L', 16.5 )

    c_sheet.set_row(0, 20.25, head_fmt1)
    a_sheet.set_row(0, 20.25, head_fmt1)
    u_sheet.set_row(0, 20.25, head_fmt2)

    writer1.save()
    writer2.save()

    t5 = time.time()
    print(f" time: {t5 - t4:.7f}")
    print(f"Done. Total elapsed time: {t5 - start:.7f}")

if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(f"../2 Data/{sys.argv[1]}")
    else:
        main()
