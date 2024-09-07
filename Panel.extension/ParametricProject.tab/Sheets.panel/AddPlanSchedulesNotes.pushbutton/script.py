from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import revit, forms, script
from System.Collections.Generic import List

def sort_min_max_pts(pt1, pt2):
  pt1_x = pt1.X
  pt1_y = pt1.Y
  pt2_x = pt2.X
  pt2_y = pt2.Y

  rpt_x_min = None
  rpt_y_min = None
  rpt_x_max = None
  rpt_y_max = None

  if pt1_x < pt2_x:
    rpt_x_min = pt1_x
    rpt_x_max = pt2_x
  else:
    rpt_x_min = pt2_x
    rpt_x_max = pt1_x

  if pt1_y < pt2_y:
    rpt_y_min = pt1_y
    rpt_y_max = pt2_y
  else:
    rpt_y_min = pt2_y
    rpt_y_max = pt1_y

  min_pt = XYZ(rpt_x_min, rpt_y_min, 0)
  max_pt = XYZ(rpt_x_max, rpt_y_max, 0)

  return {"min": min_pt, "max": max_pt}

def get_largest_viewport(view, viewports):
  largest_viewport = viewports[0]
  max_area = 0
  for vp in viewports:
    min_pt = XYZ(0,0,0)
    max_pt = XYZ(0,0,0)
    if type(vp) == ScheduleSheetInstance:
      min_pt = vp.get_BoundingBox(view).Min
      max_pt = vp.get_BoundingBox(view).Max
    else:
      outline = vp.GetBoxOutline()
      min_pt = outline.MinimumPoint
      max_pt = outline.MaximumPoint
    length = abs(max_pt.X - min_pt.X)
    height = abs(max_pt.Y - min_pt.Y)
    area = length * height
    if area >= max_area:
      max_area = area
      largest_viewport = vp
  return largest_viewport

def get_viewport_dimensions(view, viewport):
  vp_min = None
  vp_max = None
  if type(viewport) == ScheduleSheetInstance:
    vp_min = viewport.get_BoundingBox(view).Min
    vp_max = viewport.get_BoundingBox(view).Max
  else:
    vp_min = viewport.GetBoxOutline().MinimumPoint
    vp_max = viewport.GetBoxOutline().MaximumPoint
  length = vp_max.X - vp_min.X
  height = vp_max.Y - vp_min.Y
  return {"length": length, "height": height}

## There has to be much simpler way of doing this
## Just collect all sets of x points, y points, and compare
def get_max_viewport_dimensions(view, viewports):
  highest_vp = viewports[0]
  longest_vp = viewports[0]
  max_height = 0
  max_length = 0
  for vp in viewports:
    vp_min_pt = XYZ(0,0,0)
    vp_max_pt = XYZ(0,0,0)
    highest_vp_min_pt = XYZ(0,0,0)
    highest_vp_max_pt = XYZ(0,0,0)
    longest_vp_min_pt = XYZ(0,0,0)
    longest_vp_max_pt = XYZ(0,0,0)
    if type(vp) == ScheduleSheetInstance:
      vp_min_pt = vp.get_BoundingBox(view).Min
      vp_max_pt = vp.get_BoundingBox(view).Max
    else:
      vp_min_pt = vp.GetBoxOutline().MinimumPoint
      vp_max_pt = vp.GetBoxOutline().MaximumPoint
    if type(highest_vp) == ScheduleSheetInstance:
      highest_vp_min_pt = highest_vp.get_BoundingBox(view).Min
      highest_vp_max_pt = highest_vp.get_BoundingBox(view).Max
    else:
      highest_vp_min_pt = highest_vp.GetBoxOutline().MinimumPoint
      highest_vp_max_pt = highest_vp.GetBoxOutline().MaximumPoint
    if type(longest_vp) == ScheduleSheetInstance:
      longest_vp_min_pt = longest_vp.get_BoundingBox(view).Min
      longest_vp_max_pt = longest_vp.get_BoundingBox(view).Max
    else:
      longest_vp_min_pt = longest_vp.GetBoxOutline().Minimum_Point
      longest_vp_max_pt = longest_vp.GetBoxOutline().MaximumPoint
    highest_vp_height = abs(highest_vp_max_pt.Y - highest_vp_min_pt.Y)
    longest_vp_length = abs(longest_vp_max_pt.X - longest_vp_min_pt.X)
    vp_length = abs(vp_max_pt.X - vp_min_pt.X)
    vp_height = abs(vp_max_pt.Y - vp_min_pt.Y)
    if vp_length >= longest_vp_length:
      max_length = vp_length
      longest_viewport = vp
    if vp_height >= highest_vp_height:
      max_height = vp_height
      highest_viewport = vp
  return {"length": max_length, "height": max_height}

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
  max_height_vp = get_max_viewport_dimensions(view, viewports)["height"]
  max_length_vp = get_max_viewport_dimensions(view, viewports)["length"]
  is_room_above = False
  is_room_below = False
  is_room_left = False
  is_room_right = False
  if (max_height_vp * whitespace_percent) < above_dist:
    is_room_above = True
  if (max_height_vp * whitespace_percent) < below_dist:
    is_room_below = True
  if (max_length_vp * whitespace_percent) < left_dist:
    is_room_left = True
  if (max_length_vp * whitespace_percent) < right_dist:
    is_room_right= True
  return {"above": is_room_above, "below": is_room_below\
        ,"left": is_room_left, "right": is_room_right}

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

## VARIABLES
cf_sched_name = "CONTINUOUS FOOTING SCHEDULE"
sf_sched_name = "SPREAD FOOTING SCHEDULE"
foundation_notes_name = "S-111_SHEET NOTES"
foundation_material_key_name = "PLAN SYMBOLS KEY - FDN SPREAD FOOTINGS"
foundation_sheet_name = "FOUNDATION/FIRST FLOOR PLAN"
viewport_type_name = "IMEG_No View Title"

view_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_Views)\
                .WhereElementIsNotElementType()
schedule_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_Schedules)\
                .WhereElementIsNotElementType()
sheet_collector = FilteredElementCollector(doc)\
                  .OfCategory(BuiltInCategory.OST_Sheets)\
                  .WhereElementIsNotElementType()
viewport_type_collector = FilteredElementCollector(doc)\
                          .OfCategory(BuiltInCategory.OST_Viewports)\
                          # .WhereElementIsElementType()


view_list = list(view_collector)
schedule_list = list(schedule_collector)
sheet_list = list(sheet_collector)
vp_type_list = list(viewport_type_collector)

view_plans = [view for view in view_list\
             if view.ViewType == ViewType.EngineeringPlan]

drafting_views = [view for view in view_list\
                 if view.ViewType == ViewType.DraftingView]

legends =  [view for view in view_list\
             if view.ViewType == ViewType.Legend]

cf_sched = [sched for sched in schedule_list\
            if Element.Name.GetValue(sched) == cf_sched_name][0]

sf_sched = [sched for sched in schedule_list\
            if Element.Name.GetValue(sched) == sf_sched_name][0]

foundation_notes = [view for view in drafting_views\
            if Element.Name.GetValue(view) == foundation_notes_name][0]

foundation_sheet = [sheet for sheet in sheet_list\
                   if Element.Name.GetValue(sheet) == foundation_sheet_name][0]

foundation_material_key = [legend for legend in legends\
                   if Element.Name.GetValue(legend) == foundation_material_key_name][0]

vp_type_id = [vp.GetTypeId() for vp in vp_type_list\
          if Element.Name.GetValue(vp)\
          == viewport_type_name][0]

with revit.Transaction('Add Schedules and Notes'):

  current_sheet = active_view
  # User input - get the outline for the useable sheet space
  selection = uidoc.Selection
  pb = selection.PickBox(Selection.PickBoxStyle.Enclosing)

  pb_pt_click1 = pb.Min
  pb_pt_click2 = pb.Max

  sheet_pts_sorted = sort_min_max_pts(pb_pt_click1 , pb_pt_click2)
  sheet_min_pt = sheet_pts_sorted["min"]
  sheet_max_pt = sheet_pts_sorted["max"]

  sheet_outline = Outline(sheet_min_pt, sheet_max_pt)

  # Get the extents of the plan viewport on sheet
  plan_viewport = None
  existing_viewport_ids = active_view.GetAllViewports()
  vp_list = list(existing_viewport_ids)
  existing_viewports = [doc.GetElement(vp) for vp in vp_list]
  largest_viewport = get_largest_viewport(view, existing_viewports)
  plan_viewport = largest_viewport

  views_to_add = [cf_sched, sf_sched, foundation_notes\
                 ,foundation_material_key]
  viewports_added = []

  ## Creating viewports from views to add and placing at 0,0,0
  for view in views_to_add:
    if type(view) == ViewDrafting or type(view) == View:
      viewport = Viewport.Create(doc, current_sheet.Id, view.Id, XYZ(0,0,0))
      viewports_added.append(viewport)
    if type(view) == ViewSchedule:
      viewport = ScheduleSheetInstance.Create(doc, current_sheet.Id, view.Id, XYZ(0,0,0))
      viewports_added.append(viewport)

  ## determing where there is space and transforming viewports
  is_room_for_viewports = is_room_for_viewports(current_sheet, sheet_outline, plan_viewport, viewports_added)
  notes_mkeys = []
  schedules = []

  for vp in viewports_added:
    if type(vp) == ScheduleSheetInstance:
      schedules.append(vp)
    else:
      notes_mkeys.append(vp)

  margin = 0.02
  if is_room_for_viewports["above"]:
    anchor_pt = sheet_outline.MaximumPoint
    for vp in notes_mkeys:
      vp_height = get_viewport_dimensions(current_sheet, vp)["height"]
      vp_length = get_viewport_dimensions(current_sheet, vp)["length"]
      move_pt = XYZ(anchor_pt.X - vp_length/2, anchor_pt.Y - vp_height/2, 0)
      vp.SetBoxCenter(move_pt)
      vp_anchor_pt = vp.GetBoxOutline().MaximumPoint
      anchor_pt = XYZ(vp_anchor_pt.X - (vp_length + margin), vp_anchor_pt.Y, 0)
      vp.ChangeTypeId(vp_type_id)
    for schedule in schedules:
      y_offset = .02
      schedule_length = get_viewport_dimensions(current_sheet, schedule)["length"]
      schedule_height = get_viewport_dimensions(current_sheet, schedule)["height"]
      schedule_point = XYZ(anchor_pt.X - schedule_length\
                        , anchor_pt.Y - y_offset, 0)
      schedule.Point = schedule_point
      anchor_pt = XYZ(schedule_point.X - margin, schedule_point.Y + y_offset, 0)

  elif is_room_for_viewports["below"]:
    max_pt = sheet_outline.MaximumPoint
    min_pt = sheet_outline.MinimumPoint
    anchor_pt = XYZ(max_pt.X, min_pt.Y, 0)
    for vp in notes_mkeys:
      vp_height = get_viewport_dimensions(current_sheet, vp)["height"]
      vp_length = get_viewport_dimensions(current_sheet, vp)["length"]
      move_pt = XYZ(anchor_pt.X - vp_length/2, anchor_pt.Y + vp_height/2, 0)
      vp.SetBoxCenter(move_pt)
      vp_max_pt = vp.GetBoxOutline().MaximumPoint
      vp_min_pt = vp.GetBoxOutline().MinimumPoint
      vp_anchor_pt = XYZ(vp_max_pt.X, vp_min_pt.Y, 0)
      anchor_pt = XYZ(vp_anchor_pt.X - (vp_length + margin), vp_anchor_pt.Y, 0)
      vp.ChangeTypeId(vp_type_id)
    for schedule in schedules:
      y_offset = .02
      schedule_length = get_viewport_dimensions(current_sheet, schedule)["length"]
      schedule_height = get_viewport_dimensions(current_sheet, schedule)["height"]
      schedule_point = XYZ(anchor_pt.X - schedule_length\
                           ,anchor_pt.Y + y_offset + schedule_height, 0)
      schedule.Point = schedule_point
      anchor_pt = XYZ(schedule_point.X - margin, schedule_point.Y - + y_offset - schedule_height, 0)






