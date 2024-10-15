#! python3

from Autodesk.Revit.DB import *
import xlrd
import os

def get_excel_data_by_column(file_path, column_int):
  column_data_list = []
  wb = xlrd.open_workbook(R"C:\Users\Jon.R.Ryea\OneDrive - IMEG Corp\Desktop\08 Parametric Engineering Project\Phase 1 - Meramec FS+EC\Excel\Excel_speckle_family_type_data.xlsx")
  sheet = wb.sheet_by_index(0)
  for i in range(1, sheet.nrows):
    column_data_list.append(sheet.cell_value(i,1))
  return column_data_list

def path_join(base_path, path_join_list, file_extension):
  full_path = base_path
  for path in path_join_list:
    full_path = os.path.join(full_path, path)
  full_path = full_path + file_extension
  return full_path

