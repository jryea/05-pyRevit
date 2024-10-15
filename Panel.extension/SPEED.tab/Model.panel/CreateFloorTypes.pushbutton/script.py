from Autodesk.Revit.DB import *
from pyrevit import revit, forms
from utilities.collection import Collection
from utilities import datum, geometry, families, files
from utilities import floors as floor_utils
from System.Collections.Generic import List

# ## VARIABLES ##
init_dir = R'SPEED.tab\C:\Users\Jon.R.Ryea\OneDrive - IMEG Corp\Desktop\08 Parametric Engineering Project'

base_path = R'\\files\Corporate\Standards\CAD-BIM Standards\Content\2023 Revit\zOOTB\2023\English-Imperial'

file_path = forms.pick_file(title = 'Select a file', file_ext = 'xlsx', multi_file=False, restore_dir=False, init_dir=init_dir)

family_data_list = files.get_excel_data_by_column(file_path, 1)

def get_family_name_from_data(family_data):
  family_data_split = family_data.split(';')
  family_name = family_data_split[2].strip()
  return family_name

def get_family_symbol_from_data(family_data):
  family_data_split = family_data.split(';')
  family_symbol_name = family_data_split[3].strip()
  return family_symbol_name

def is_floor_data(family_data):
  family_data_split = family_data.split(';')
  category = family_data_split[0].strip()
  if category.lower() == 'floor'\
    or category.lower() == 'floors':
      return True
  else:
    return False

def get_floor_type_data(family_data):
  floor_data_split = family_data.split(';')
  category = floor_data_split[0].strip()
  material = floor_data_split[1].strip()
  type_name = floor_data_split[2].strip()
  thickness1 = float(floor_data_split[3].strip())
  thickness2 = None
  if len(floor_data_split) > 4:
    thickness2 = float(floor_data_split[4].strip())
  return {'category': category, 'material': material, 'type_name': type_name, 'thickness1': thickness1, 'thickness2': thickness2}

def get_base_floor_type_from_family_data(floor_types, family_data):
  floor_type = None
  existing_floor = None
  floor_data = get_floor_type_data(family_data)
  material = floor_data['material']
  if 'concrete' in material.lower()\
    and 'deck' in material.lower():
    floor_type = Collection.get_floor_type_if_name_contains(floor_types, 'concrete', include_name2='deck')
  elif 'concrete' in material.lower():
    floor_type = Collection.get_floor_type_if_name_contains(floor_types, 'concrete', exclude_name='deck')
  elif 'deck' in material.lower():
    floor_type = Collection.get_floor_type_if_name_contains(floor_types, 'deck', exclude_name='concrete')
  else:
    print('Floor Type not recognized')
  return floor_type

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

all_floors = Collection().add_floors(doc).to_list()
all_floor_types = Collection.get_floor_types(doc)

with revit.Transaction('Create Floor Types'):
  for family_data in family_data_list:
    if is_floor_data(family_data):
      base_floor_type = get_base_floor_type_from_family_data(all_floor_types, family_data)
      floor_type_data = get_floor_type_data(family_data)
      thickness1 = floor_type_data['thickness1']
      thickness2 = floor_type_data['thickness2']
      type_name = floor_type_data['type_name']
      if floor_utils.does_floor_type_exist(all_floor_types, type_name):
        continue
      else:
        new_floor = floor_utils.create_floor_type(base_floor_type, type_name, thickness1, thickness2)


