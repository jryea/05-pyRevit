from Autodesk.Revit.DB import *
from pyrevit import revit
from System.Collections.Generic import List
from data import data
from utilities.collection import Collection
from utilities import selection as sel
from utilities import connections as conn
from utilities import views as utilview



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
    columns = Collection().add_columns(doc, view)
    columns.filter_columns_by_material(mk)
    return columns.to_list()
  elif sk == 'bm':
    beams = Collection().add_beams(doc, view)
    beams.filter_beams_by_material(mk)
    if fk:
      beams.filter_beams_by_type(fk)
    return beams.to_list()
  elif sk == 'fl':
    floors = Collection().add_floors(doc, view)
    floors.filter_floors_by_material(mk)
    return floors.to_list()
  elif sk == 'sf':
    spread_footings = Collection().add_spread_footings(doc, view)
    return spread_footings.to_list()
  elif sk == 'cf':
    cont_footings = Collection().collect_cont_footings(doc, view)
    return cont_footings.to_list()
  else:
    print('member key is not valid')
    return None

def get_detail_members(doc, view, detail):
  detail_members = []
  member_keys = detail['members']['structural']
  for key in member_keys:
    members = get_members(doc, view, key)
    if members:
      detail_members.extend(members)
  return detail_members

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

## TESTING
plan_views = Collection.get_plan_views(doc)

drafting_views = Collection.get_drafting_views(doc)

plan_views_on_sheet = [view for view in plan_views if view.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced]

drafting_views_on_sheet = [view for view in drafting_views if view.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced]

detail_data = data.detail_data
detail_01 = get_detail_dict('2200-03', detail_data)
detail_02 = get_detail_dict('5400-06', detail_data)
detail_01_ref_view = get_drafting_ref_view('2200-03', drafting_views_on_sheet)
detail_02_ref_view = get_drafting_ref_view('5400-06', drafting_views_on_sheet)

with revit.Transaction('Create Section Cuts'):
  for view in plan_views_on_sheet:
    detail_01_location_pts_w_direction = []
    detail_02_location_pts_w_direction = []
    detail_01_members = get_detail_members(doc, view, detail_01)
    detail_02_members = get_detail_members(doc, view, detail_02)
    detail_01_columns = Collection.get_columns_from_elements(detail_01_members)
    detail_01_spread_footings = Collection.get_spread_footings_from_elements(detail_01_members)
    detail_02_columns = Collection.get_columns_from_elements(detail_02_members)
    detail_02_beams = Collection.get_beams_from_elements(detail_02_members)

    for column in detail_01_columns:
      if detail_01_spread_footings:
        connection = conn.footing_to_column(doc, detail_01_spread_footings, column)
        if connection:
          direction = XYZ().BasisY
          pt = column.Location.Point
          ref_section = utilview.create_ref_section(doc, view, detail_01_ref_view, pt, direction)

    for column in detail_02_columns:
      if detail_02_beams:
        connection = conn.beam2_to_column(doc, detail_02_beams, column, 'top')
        if connection:
          if connection[0]:
            direction = connection[1]
            col_pt = column.Location.Point
            detail_02_location_pts_w_direction.append((col_pt, direction))
    for pt_direction in detail_02_location_pts_w_direction:
      if detail_02_beams:
        pt = pt_direction[0]
        direction = pt_direction[1]
        ref_section = utilview.create_ref_section(doc, view, detail_02_ref_view, pt, direction)

