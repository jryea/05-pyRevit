import json
from Autodesk.Revit.DB import *
from pyrevit import revit

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

level_col = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_Levels)\
            .WhereElementIsNotElementType()
floor_col = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_Floors)\
            .WhereElementIsNotElementType()
beam_type_col = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_StructuralFraming)\
            .WhereElementIsElementType()

beam_type_list = list(beam_type_col)
level_list = list(level_col)
floor_list = list(floor_col)

# Helps convert the sp joists into family types
def find_closest_joist_type(joist_type):
  if joist_type[-1].lower() == "k":
    # print(joist_type)
    for beam_type in beam_type_list:
      if Element.Name.GetValue(beam_type)[:-1] == joist_type:
        # print(Element.Name.GetValue(beam_type))
        # print(joist_type)
        return beam_type
  else:
    for beam_type in beam_type_list:
      if Element.Name.GetValue(beam_type) == joist_type:
        return beam_type

beam_system_floors = [floor for floor in floor_list if Element.Name.GetValue(floor.FloorType) == "BeamSystem"]

bs_file_path = r'G:\My Drive\08 Parametric Engineering Project\JSON\meramec_beam_system_test.json'

bs_data = {}

with open(bs_file_path) as file:
  bs_data = json.load(file)

num_of_keys = 0

for key in bs_data.keys():
  num_of_keys += 1

beam_system_list = []

for item in range(num_of_keys):
  key_target = item
  for key in bs_data.keys():
    if int(key) == key_target:
      beam_system_list.append(bs_data[key])

floor_thickness = 6.0

# for beam_system in beam_system_list:
#   print(beam_system['type'][-1])

# def find_closest_level(level_list, point_z):
#   closest_level = level_list[0]
#   for level in level_list:
#     elev = closest_level.ProjectElevation
#     cur_elev = level.ProjectElevation
#     elev_dif = abs(elev - point_z)
#     cur_elev_dif = abs(cur_elev - point_z)
#     if cur_elev_dif < elev_dif:
#       closest_level = level
#   return closest_level

with revit.Transaction('Create Beam Systems'):
  for i, floor in enumerate(beam_system_floors):
    spacing = beam_system_list[i]['spacing']
    b_type = beam_system_list[i]['type']
    family = beam_system_list[i]['family']
    if b_type[:3] == '2.5K':
      family = 'IMEG_2.5K Series'
    direction = beam_system_list[i]['direction']

    beam_type = beam_type_list[0]
    for cur_beam_type in beam_type_list:
      beam_type = find_closest_joist_type(b_type)
    print('beam string from JSON: ')
    print(b_type)
    print('Revit Beam Type Name: ')
    print(Element.Name.GetValue(beam_type))
    curve_list =[]
    curve_ar_array = doc.GetElement(floor.SketchId).Profile
    for curve_array in curve_ar_array:
      for curve in curve_array:
        curve_list.append(curve)
    level_id = floor.LevelId
    level = doc.GetElement(level_id)
    print(len(curve_list))
    print(level)
    beam_system = BeamSystem.Create(doc, curve_list, level, 1, True)
    print(beam_system)

    beam_system.BeamType = beam_type
    beam_system.get_Parameter(BuiltInParameter.JOIST_SYSTEM_FIXED_SPACING_PARAM).Set(spacing)
    beam_system.get_Parameter(BuiltInParameter.INSTANCE_ELEVATION_PARAM).Set(-(floor_thickness)/12.0)
    doc.Delete(floor.Id)
    