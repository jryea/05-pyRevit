from Autodesk.Revit.DB import *

############# SHAFTS #############D
def does_shaft_intersect_floors(doc, shaft, floors):
  shaft_bb = shaft.get_BoundingBox(None)
  shaft_top = shaft_bb.Max.Z
  shaft_base = shaft_bb.Min.Z
  does_intersect = False
  for floor in floors:
    # floor_level = doc.GetElement(floor.LevelId)
    floor_elev = floor.get_Parameter(BuiltInParameter.STRUCTURAL_ELEVATION_AT_TOP).AsDouble()
    if floor_elev < shaft_top\
    and floor_elev > shaft_base:
      does_intersect = True
  return does_intersect

def create_floor_type(existing_floor,type_name, thickness1, thickness2=None):
  new_floor_type = existing_floor.Duplicate(type_name)
  compound_structure = new_floor_type.GetCompoundStructure()
  if thickness2:
    pass
  else:
    if compound_structure.GetLayerFunction(0) != MaterialFunctionAssignment.StructuralDeck:
      compound_structure.SetLayerWidth(0, thickness1)
  new_floor_type.SetCompoundStructure(compound_structure)
  return new_floor_type

def does_floor_type_exist(all_floor_types, type_name):
  for floor_type in all_floor_types:
    floor_type_name = Element.Name.GetValue(floor_type)
    if type_name.lower() == floor_type_name.lower():
      return True
  return False

