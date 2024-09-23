from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import revit, forms, script
from utilities import sheets
from utilities.collection import Collection
from data.data import plan_sheet_data
from System.Collections.Generic import List

def get_plan_sheet_by_type(doc, sheet_plan_type):
  sheets = Collection.get_sheets(doc)
  plan_sheets = []
  plan_sheets_of_type = []
  for sheet in sheets:
    view_ids_on_sheet = sheet.GetAllPlacedViews()
    for view_id in view_ids_on_sheet:
      view = doc.GetElement(view_id)
      if view.ViewType == ViewType.EngineeringPlan:
        plan_sheets.append(sheet)
  for sheet in plan_sheets:
    sheet_name = Element.Name.GetValue(sheet)
    if sheet_plan_type == 'shallow_foundation':
      if 'foundation' in sheet_name.lower():
        plan_sheets_of_type.append(sheet)
    if sheet_plan_type == 'steel_framing':
      if 'framing' in sheet_name.lower():
        plan_sheets_of_type.append(sheet)
  return plan_sheets_of_type

def is_room_for_viewports(view, sheet_outline, plan_vp, viewports):
  whitespace_percent = 1 + .05
  sheet_top = sheet_outline.MaximumPoint.Y
  sheet_bottom = sheet_outline.MinimumPoint.Y
  sheet_left = sheet_outline.MinimumPoint.X
  sheet_right = sheet_outline.MaximumPoint.X
  plan_top = plan_vp.GetBoxOutline().MaximumPoint.Y
  plan_bottom = plan_vp.GetBoxOutline().MinimumPoint.Y
  plan_left = plan_vp.GetBoxOutline().MinimumPoint.X
  plan_right = plan_vp.GetBoxOutline().MaximumPoint.X
  above_dist = abs(sheet_top - plan_top)
  left_dist = abs(sheet_left - plan_left)
  right_dist = abs(sheet_right - plan_right)
  below_dist = abs(sheet_bottom - plan_bottom)
  max_height_vp = sheets.get_max_height_viewport(view, viewports)
  max_vp_height = sheets.get_viewport_dimensions(view, max_height_vp)['height']
  max_width_vp = sheets.get_max_width_viewport(view, viewports)
  max_vp_width = sheets.get_viewport_dimensions(view, max_width_vp)['width']
  is_room_above = False
  is_room_below = False
  is_room_left = False
  is_room_right = False
  if (max_vp_height * whitespace_percent) < above_dist:
    is_room_above = True
  if (max_vp_height * whitespace_percent) < below_dist:
    is_room_below = True
  if (max_vp_width * whitespace_percent) < left_dist:
    is_room_left = True
  if (max_vp_width * whitespace_percent) < right_dist:
    is_room_right= True
  return {"above": is_room_above, "below": is_room_below\
        ,"left": is_room_left, "right": is_room_right}

# VARIABLES
viewport_type_name = "IMEG_No View Title"

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

foundation_sheets = get_plan_sheet_by_type(doc, 'shallow_foundation')
steel_framing_sheets = get_plan_sheet_by_type(doc, 'steel_framing')

foundation_sheet_legend_data = plan_sheet_data['shallow_foundation']['legends']
foundation_sheet_schedule_data = plan_sheet_data['shallow_foundation']['schedules']
framing_sheet_legend_data = plan_sheet_data['steel_framing']['legends']

foundation_legends = Collection.get_legends_by_name(doc, foundation_sheet_legend_data)
framing_legends = Collection.get_legends_by_name(doc, framing_sheet_legend_data)
foundation_schedules = Collection.get_schedules_by_name(doc, foundation_sheet_schedule_data)

vp_type = Collection.get_viewport_type_by_name(doc,viewport_type_name)
print(vp_type)
tb_working_area = sheets.get_titleblock_working_area(doc)

tb_min_pt = tb_working_area['min_pt']
tb_max_pt = tb_working_area['max_pt']

with revit.Transaction('Add Schedules and Notes'):

  sheet_outline = Outline(tb_min_pt, tb_max_pt)
  current_sheet = active_view

  # Get the extents of the plan viewport on sheet
  plan_viewport = None
  existing_viewport_ids = current_sheet.GetAllViewports()
  vp_list = list(existing_viewport_ids)
  existing_viewports = [doc.GetElement(vp) for vp in vp_list]
  plan_viewport = sheets.get_largest_viewport(existing_viewports)

  ## Placing views on sheet at 0,0,0
  legend_vps = sheets.add_views_to_sheet(doc, foundation_legends, current_sheet)
  schedule_instances = sheets.add_views_to_sheet(doc, foundation_schedules, current_sheet)
  all_vps = []
  all_vps.extend(legend_vps)
  all_vps.extend(schedule_instances)


  # determing where there is space and transforming viewports
  is_room_for_viewports = is_room_for_viewports(current_sheet, sheet_outline, plan_viewport, all_vps)

  print(is_room_for_viewports)

  margin = 0.02
  if is_room_for_viewports["above"]:
    anchor_pt = sheet_outline.MaximumPoint
    for vp in legend_vps:
      vp_height = sheets.get_viewport_dimensions(current_sheet, vp)["height"]
      vp_length = sheets.get_viewport_dimensions(current_sheet, vp)["width"]
      move_pt = XYZ(anchor_pt.X - vp_length/2, anchor_pt.Y - vp_height/2, 0)
      vp.SetBoxCenter(move_pt)
      vp_anchor_pt = vp.GetBoxOutline().MaximumPoint
      anchor_pt = XYZ(vp_anchor_pt.X - (vp_length + margin), vp_anchor_pt.Y, 0)
      vp.ChangeTypeId(vp_type.Id)
    for schedule in schedule_instances:
      y_offset = .02
      schedule_length = sheets.get_viewport_dimensions(current_sheet, schedule)["width"]
      schedule_height = sheets.get_viewport_dimensions(current_sheet, schedule)["height"]
      schedule_point = XYZ(anchor_pt.X - schedule_length\
                        , anchor_pt.Y - y_offset, 0)
      schedule.Point = schedule_point
      anchor_pt = XYZ(schedule_point.X - margin, schedule_point.Y + y_offset, 0)

  elif is_room_for_viewports["below"]:
    max_pt = sheet_outline.MaximumPoint
    min_pt = sheet_outline.MinimumPoint
    anchor_pt = XYZ(max_pt.X, min_pt.Y, 0)
    for vp in legend_vps:
      vp_height = sheets.get_viewport_dimensions(current_sheet, vp)["height"]
      vp_length = sheets.get_viewport_dimensions(current_sheet, vp)["width"]
      move_pt = XYZ(anchor_pt.X - vp_length/2, anchor_pt.Y + vp_height/2, 0)
      vp.SetBoxCenter(move_pt)
      vp_max_pt = vp.GetBoxOutline().MaximumPoint
      vp_min_pt = vp.GetBoxOutline().MinimumPoint
      vp_anchor_pt = XYZ(vp_max_pt.X, vp_min_pt.Y, 0)
      anchor_pt = XYZ(vp_anchor_pt.X - (vp_length + margin), vp_anchor_pt.Y, 0)
      vp.ChangeTypeId(vp_type.Id)
    for schedule in schedule_instances:
      y_offset = .02
      schedule_length = sheets.get_viewport_dimensions(current_sheet, schedule)["width"]
      schedule_height = sheets.get_viewport_dimensions(current_sheet, schedule)["height"]
      schedule_point = XYZ(anchor_pt.X - schedule_length\
                           ,anchor_pt.Y + y_offset + schedule_height, 0)
      schedule.Point = schedule_point
      anchor_pt = XYZ(schedule_point.X - margin, schedule_point.Y - + y_offset - schedule_height, 0)







