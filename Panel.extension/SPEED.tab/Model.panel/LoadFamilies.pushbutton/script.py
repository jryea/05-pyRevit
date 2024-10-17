import clr
clr.AddReferenceToFileAndPath("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\netstandard\\v4.0_2.0.0.0__cc7b13ffcd2ddd51\\netstandard.dll")
clr.AddReferenceToFileAndPath(r"C:\Users\Jon.R.Ryea\AppData\Roaming\McNeel\Rhinoceros\8.0\Plug-ins\SpeckleRhino2 (8dd5f30b-a13d-4a24-abdc-3e05c8c87143)\SpeckleCore2.dll")
from Autodesk.Revit.DB import *
from pyrevit import revit, forms
from utilities import datum, geometry, families, files
from utilities import floors as floor_utils
from Speckle.Core.Credentials import *
from Speckle.Core.Api import *
from Speckle.Core.Transports import *
from Speckle.Core.Models import *
from utilities.collection import Collection

# ## VARIABLES ##
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

speckle_stream_url = forms.ask_for_string(
                     prompt= 'Speckle Stream URL',
                     title='Get Speckle Stream'
                     )

data = Helpers.Receive(speckle_stream_url).Result

# Use method GetDynamicMemberNames() on Base object to get children
outer_wrapper = data['Data']
base = outer_wrapper[r'@{0}'][0]
family_data_list = base['@familyData']

init_dir = R'SPEED.tab\C:\Users\Jon.R.Ryea\OneDrive - IMEG Corp\Desktop\08 Parametric Engineering Project'
base_path = R'\\files\Corporate\Standards\CAD-BIM Standards\Content\2023 Revit\zOOTB\2023\English-Imperial'

all_floors = Collection().add_floors(doc).to_list()
all_floor_types = Collection.get_floor_types(doc)

# ## FUNCTIONS ##
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

with revit.Transaction('Add Shafts'):
  loaded_families = []
  # Load Families if not loaded
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
    else:
      family_name = get_family_name_from_data(family_data)
      family_symbol_name = get_family_symbol_from_data(family_data)
      family_category = get_family_category_from_data(family_data)
      family_path = get_family_path_from_data(base_path, family_data)
      if family_name not in loaded_families:
        loaded_families.append(family_name)
        if families.is_family_loaded(doc, family_name) == False:
            families.load_family(doc, family_name, family_path)
        else:
          family = Collection.get_family_by_name(doc, family_name)
          doc.Delete(family.Id)
          families.load_family(doc, family_name, family_path)
    doc.Regenerate()

  # Load symbols if not loaded
  for family_data in family_data_list:
    family_category = get_family_category_from_data(family_data)
    if family_category.lower() != 'floors':
      family_name = get_family_name_from_data(family_data)
      family = Collection.get_family_by_name(doc, family_name)
      family_symbol_name = get_family_symbol_from_data(family_data)
      family_path = get_family_path_from_data(base_path, family_data)
      if families.does_family_symbol_exist(doc, family, family_symbol_name) == False:
        families.load_family_symbol(doc, family_path, family_symbol_name)




