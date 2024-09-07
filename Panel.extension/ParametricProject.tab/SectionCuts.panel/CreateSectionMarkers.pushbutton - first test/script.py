from Autodesk.Revit.DB import *
from pyrevit import revit
from System.Collections.Generic import List

## FUNCTIONS
def create_outline_from_element(element):
  bounding_box = element.get_BoundingBox(None)
  bb_min = bounding_box.Min
  bb_max = bounding_box.Max
  outline = Outline(bb_min, bb_max)
  return outline

def does_column_floor_overlap(column, floor):
  point = column.Location.Point
  bb = floor.get_BoundingBox(None)
  outline = create_outline_from_bb(bb)
  if outline.Contains(point, 0.01):
    return True
  else:
    return False

def does_column_spread_footing_overlap(column, footing):
  point = column.Location.Point
  bb = footing.get_BoundingBox(None)
  outline = create_outline_from_bb(bounding_box)
  if outline.Contains(point, 0.01):
    return True
  else:
    return False

def retrieve_section_dict_members(view, section_dict):
  member_names = section_dict['members']['structural']
  section_dict_members = []
  member_dict = {}
  for member_name in member_names:
    member_list = []
    if member_name == 'column_steel':
      for column in column_steel:
        member_list.append(column)
    if member_name == 'floor_concrete':
      for floor in floor_concrete:
        member_list.append(floor)
    if member_name == 'spread_footing':
      for footing in spread_footing:
        member_list.append(footing)
    if member_name == 'cont_footing':
      for footing in spread_footing:
        member_list.append(footing)
    member_dict[member_name] = member_list
  return member_dict

def get_intersecting_elements_in_view(doc, view_id, element, element_list):
    outline = create_outline_from_element(element)
    bb_intersects_filter = BoundingBoxIntersectsFilter(outline)
    intersects_collector = FilteredElementCollector(doc, view_id)\
                           .WherePasses(bb_intersects_filter).ToElements()
    elements_intersecting = list(intersects_collector)
    return elements_intersecting

def collect_view_elements(doc, view_id):
  floor_collector = FilteredElementCollector(doc, view_id)\
              .OfCategory(BuiltInCategory.OST_Floors)\
              .WhereElementIsNotElementType()
  wall_collector = FilteredElementCollector(doc, view_id)\
                  .OfCategory(BuiltInCategory.OST_Walls)\
                  .WhereElementIsNotElementType()
  column_collector = FilteredElementCollector(doc, view_id)\
                    .OfCategory(BuiltInCategory.OST_StructuralColumns)\
                    .WhereElementIsNotElementType()
  foundation_collector = FilteredElementCollector(doc, view_id)\
                    .OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                    .WhereElementIsNotElementType()

  floor_list = list(floor_collector)
  wall_list = list(wall_collector)
  column_list = list(column_collector)
  foundation_list = list(foundation_collector)

  column_steel = [column for column in column_list\
                  if column.StructuralMaterialType\
                  == Structure.StructuralMaterialType.Steel]

  floor_concrete = [floor for floor in floor_list\
                  if "concrete" in Element.Name\
                  .GetValue(floor.FloorType).lower()]

  wall_concrete = [wall for wall in wall_list\
                  if "concrete" in Element.Name\
                  .GetValue(wall.WallType).lower()]

  cont_footing = [f for f in foundation_list\
                  if type(f) == WallFoundation]

  spread_footing = [f for f in foundation_list\
                  if type(f) == FamilyInstance]

  view_elements = column_steel + floor_concrete + wall_concrete + cont_footing + spread_footing
  return view_elements

### SECTION DICTIONARIES
## Should I add all dictionaries to a section dictionary list?
column_footing_dict = {"detail_key": '2200-03',
                       'members': {'structural':
                                  ['column_steel', 'floor_concrete', 'spread_footing'],
                       'architectural': None
                                  },
                       'connections':[['column_steel', 'spread_footing']]}

foundation_coldform_dict = {"detail_key": '2200-04',
                            'members': {'structural':
                                         ['wall_concrete', 'floor_concrete', 'cont_footing', 'wall-coldform'],
                            'architectural':
                                         ['wall_coldform']},
                            'connections': [['wall_concrete', 'cont_footing']]}

foundation_glazing_dict = {"detail_key": '2200-05',
                            'members': {'structural':
                                         ['wall_concrete', 'floor_concrete', 'cont_footing'],
                            'architectural':
                                         ['wall_glazing']},
                            'connections': [['wall_concrete', 'cont_footing']]}

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

view_collector = FilteredElementCollector(doc)\
                 .OfCategory(BuiltInCategory.OST_Views)\
                 .WhereElementIsNotElementType()

view_list = list(view_collector)
plan_views = [view for view in view_list if view.ViewType == ViewType.EngineeringPlan]

with revit.Transaction('Create Section Cuts'):
  for view in plan_views:
    view_elements = collect_view_elements(doc, view.Id)
    family_instances = [element for element in view_elements if type(element) == FamilyInstance]
    columns = [element for element in family_instances if element.StructuralType == Structure.StructuralType.Column]

    for column in columns:
      intersecting_elements = get_intersecting_elements_in_view(doc, view.Id, column, view_elements)
      print(len(intersecting_elements))
                                                                                                                                                                 


  # column_footing_sect_members_dict = retrieve_section_dict_members(None, column_footing_dict)
  # foundation_coldform_members_dict = retrieve_section_dict_members(None, foundation_coldform_dict)
  # foundation_glazing_members_dict = retrieve_section_dict_members(None, foundation_glazing_dict)

  # all_dict_members = []
  # for key in column_footing_sect_members_dict.keys():
  #   for value in column_footing_sect_members_dict[key]:
  #     if value:
  #       all_dict_members.append(value)

  # element = column_footing_sect_members_dict["column_steel"][0]
  # intersecting_elements = get_intersecting_elements(doc, element, all_dict_members)
  # print(intersecting_elements)

  # for column in column_footing_sect_members_dict['column_steel']:
  #   section_member_keys = column_footing_section_members_dict.keys