from Autodesk.Revit.DB import *
from pyrevit import revit, forms
from utilities.collection import Collection
from utilities import floors, datum, geometry, families, files

# ## VARIABLES ##
init_dir = R'SPEED.tab\C:\Users\Jon.R.Ryea\OneDrive - IMEG Corp\Desktop\08 Parametric Engineering Project'

file_path = forms.pick_file(title = 'Select a file', file_ext = 'xlsx', multi_file=False, restore_dir=False, init_dir=init_dir)

family_data_list = files.get_excel_data_by_column(file_path, 1)

base_path = R'\\files\Corporate\Standards\CAD-BIM Standards\Content\2023 Revit\zOOTB\2023\English-Imperial'

def get_family_name_from_data(family_data):
  family_data_split = family_data.split(';')
  family_name = family_data_split[2].strip()
  return family_name

def get_family_symbol_from_data(family_data):
  family_data_split = family_data.split(';')
  family_symbol_name = family_data_split[3].strip()
  return family_symbol_name

def get_family_category_from_data(family_data):
  family_data_split = family_data.split(';')
  family_category_name = family_data_split[0].strip()
  return family_category_name

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

for family_data in family_data_list:
  family_name = get_family_name_from_data(family_data)
  family_symbol = get_family_symbol_from_data(family_data)

def get_family_path_from_data(base_path, family_data):
  path_list = []
  family_data_split = family_data.split(';')
  category = family_data_split[0].strip()
  material = family_data_split[1].strip()
  family_name = family_data_split[2].strip()
  symbol_name = family_data_split[3].strip()

  path_list.append(category)
  path_list.append(material)
  path_list.append(family_name)

  full_path = files.path_join(base_path, path_list, '.rfa')
  return full_path

with revit.Transaction('Add Shafts'):

  # Load Families if not loaded
  for family_data in family_data_list:
    family_name = get_family_name_from_data(family_data)
    family_symbol_name = get_family_symbol_from_data(family_data)
    family_category = get_family_category_from_data(family_data)
    family_path = get_family_path_from_data(base_path, family_data)
    if family_category.lower() != 'floors':
      if families.is_family_loaded(doc, family_name) == False:
        families.load_family(doc, family_name, family_path)
      else:
        family = Collection.get_family_by_name(doc, family_name)
        doc.Delete(family.Id)
        families.load_family(doc, family_name, family_path)
      # if families.is_family_loaded(doc, family_name) == False:

    doc.Regenerate()

  # Load symbols if not loaded
  for family_data in family_data_list:
    if family_category.lower() != 'floors':
      family_name = get_family_name_from_data(family_data)
      family = Collection.get_family_by_name(doc, family_name)
      family_symbol_name = get_family_symbol_from_data(family_data)
      family_path = get_family_path_from_data(base_path, family_data)
      if families.does_family_symbol_exist(doc, family, family_symbol_name) == False:
        families.load_family_symbol(doc, family_path, family_symbol_name )




