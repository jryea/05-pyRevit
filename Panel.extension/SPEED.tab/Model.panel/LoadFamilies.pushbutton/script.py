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

# speckle_stream_url = forms.ask_for_string(
#                      prompt= 'Speckle Stream URL',
#                      title='Get Speckle Stream'
#                      )
speckle_stream_url = 'https://app.speckle.systems/projects/f0fe348ca0/models/9d654c53b3'
data = Helpers.Receive(speckle_stream_url).Result

# Use method GetDynamicMemberNames() on Base object to get children
outer_wrapper = data['Data']
base = outer_wrapper[r'@{0}'][0]
family_data_list = base['@familyData']

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

def get_base_floor_type_from_family_data(floor_types, floor_data):
  floor_type = None
  existing_floor = None
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

def create_family_data_dict(family_data_list):
  family_data_dict = {'floors':{}, 'Structural Framing': {}, 'Structural Columns': {}}
  for family_data in family_data_list:
    family_data_split = family_data.split(';')
    category = family_data_split[0].strip()
    material = family_data_split[1].strip()
    if category == 'floors':
      floor_type = family_data_split[2].strip()
      thickness = family_name = family_data_split[3].strip()
      floor_type_dict = {floor_type:{'material': material, 'thickness': thickness}}
      family_data_dict.update({'floors': floor_type_dict})
    else:
      family_name = family_data_split[2].strip()
      symbol_name = family_data_split[3].strip()
      family_path = get_family_path_from_data(base_path, family_data)
      # type_dict = {'material': material, "" , }
      if family_name not in family_data_dict[category]:
        type_dict = {'material': material, 'family_path': family_path, 'family_symbols': [symbol_name]}
        family_data_dict[category].update({family_name: type_dict})
      else:
        if symbol_name not in family_data_dict[category][family_name]['family_symbols']:
          family_data_dict[category][family_name]['family_symbols'].append(symbol_name)
  return family_data_dict

family_data_dict = create_family_data_dict(family_data_list)

with revit.Transaction('Load families'):
  loaded_families = []
  for category in family_data_dict.keys():
    for family_name in family_data_dict[category].keys():
      if category == 'floors':
        family_name_dict = family_data_dict[category][family_name]
        base_floor_type = get_base_floor_type_from_family_data(all_floor_types, family_name_dict)
        thickness = family_name_dict['thickness']
        material = family_name_dict['material']
        if floor_utils.does_floor_type_exist(all_floor_types, family_name):
          continue
        else:
          new_floor = floor_utils.create_floor_type(base_floor_type, family_name, thickness)
          print(family_name + ' floor created')
      else:
        family_name_dict = family_data_dict[category][family_name]
        family_path = family_name_dict['family_path']
        family_symbols = family_name_dict['family_symbols']
        if family_name not in loaded_families:
          loaded_families.append(family_name)
          if families.is_family_loaded(doc, family_name):
            family = Collection.get_family_by_name(doc, family_name)
            doc.Delete(family.Id)
          families.load_family(doc, family_name, family_path)
        doc.Regenerate()
        family = Collection.get_family_by_name(doc, family_name)
        families.delete_unused_symbols(doc, family, family_symbols)



