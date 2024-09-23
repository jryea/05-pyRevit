from Autodesk.Revit.DB import *
from pyrevit import revit
from System.Collections.Generic import List
from data import data
from utilities import collectors as col
from utilities import selection as sel
from utilities import connections as conn
from utilities import view as utilview

def get_intersecting_elements_in_view(doc, view_id, element, element_list):
    outline = create_outline_from_element(element)
    bb_intersects_filter = BoundingBoxIntersectsFilter(outline)
    intersects_collector = FilteredElementCollector(doc, view_id)\
                           .WherePasses(bb_intersects_filter).ToElements()
    elements_intersecting = list(intersects_collector)
    return elements_intersecting

def get_detail_dict(detail_key, detail_data):
  all_detail_keys = detail_data.keys()
  if detail_key in all_detail_keys:
    return detail_data[detail_key]
  else:
    print('detail key:'+detail_key+' not found')

def get_drafting_ref_view(detail_key, drafting_views):
  for view in drafting_views:
    if view.LookupParameter('IMEG DETAIL NUMBER'):
      detail_num = view.LookupParameter('IMEG DETAIL NUMBER').AsString()
      if detail_num:
        if detail_num == detail_key:
          return view
  print('Detail reference view not found')
  return None

def get_member_keys(key):
  all_member_keys = key.split('_')
  structural_type_key = all_member_keys[0]
  material_key = None
  family_type_key = None
  if len(all_member_keys) > 1:
    material_key = all_member_keys[1]
  if len(all_member_keys) > 2:
    family_type_key = all_member_keys[2]
  member_key = {'structural_type_key':structural_type_key, 'material_key':material_key , 'family_type_key': family_type_key}
  return member_key

def get_members(doc, view, key):
  member_keys = get_member_keys(key)
  sk = member_keys['structural_type_key']
  mk = member_keys['material_key']
  fk = member_keys['family_type_key']
  if sk == 'co':
    columns = col.collect_columns(doc, view)
    columns = col.filter_columns_by_material(columns, mk)
    return columns
  elif sk == 'bm':
    beams = col.collect_beams(doc, view)
    beams = col.filter_beams_by_material(beams, mk)
    if fk:
      beams = col.filter_framing_by_type(beams, fk)
    return beams
  elif sk == 'fl':
    floors = col.collect_floors(doc, view)
    floors = col.filter_floors_by_material(floors, mk)
    return floors
  elif sk == 'sf':
    spread_footings = col.collect_spread_footings(doc, view)
    return spread_footings
  elif member_keys['structural_type_key'] == 'cf':
    cont_footings = col.collect_cont_footings(doc, view)
    return cont_footings
  else:
    print('member key is not valid')
    return None

def get_detail_members(doc, view, detail):
  detail_members = []
  member_keys = detail['members']['structural']
  for key in member_keys:
    members = get_members(doc, view, key)
    if members:
      detail_members.extend(get_members(doc, view, key))
  return detail_members

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

view_collector = FilteredElementCollector(doc)\
                 .OfCategory(BuiltInCategory.OST_Views)\
                 .WhereElementIsNotElementType()

view_list = list(view_collector)
plan_views = [view for view in view_list if view.ViewType == ViewType.EngineeringPlan]
drafting_views = [view for view in view_list if view.ViewType == ViewType.DraftingView]
plan_views_on_sheet = [view for view in plan_views if view.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced]
drafting_views_on_sheet = [view for view in drafting_views if view.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced]

detail_data = data.detail_data
detail_01 = get_detail_dict('2200-03', detail_data)
detail_02 = get_detail_dict('2200-04', detail_data)
detail_01_ref_view = get_drafting_ref_view('2200-03', drafting_views_on_sheet)
detail_02_ref_view = get_drafting_ref_view('2200-04', drafting_views_on_sheet)

with revit.Transaction('Create Section Cuts'):
  detail_01_location_pts_w_direction = []
  detail_02_location_pts_w_direction = []
  detail_01_members = get_detail_members(doc, active_view, detail_01)
  detail_02_members = get_detail_members(doc, active_view, detail_02)
  detail_01_columns = col.get_columns_from_elements(detail_01_members)
  detail_01_beams = col.get_beams_from_elements(detail_01_members)
  detail_02_columns = col.get_columns_from_elements(detail_02_members)
  detail_02_beams = col.get_beams_from_elements(detail_02_members)
  for column in detail_02_columns:
    connection = conn.beam2_to_column(doc, detail_02_beams, column, 'top')
    if connection:
      if connection[0]:
        direction = connection[1]
        col_pt = column.Location.Point
        detail_02_location_pts_w_direction.append((col_pt, direction))
  for pt_direction in detail_02_location_pts_w_direction:
    pt = pt_direction[0]
    direction = pt_direction[1]
    ref_section = utilview.create_ref_section(doc, active_view, detail_02_ref_view, pt, direction)
