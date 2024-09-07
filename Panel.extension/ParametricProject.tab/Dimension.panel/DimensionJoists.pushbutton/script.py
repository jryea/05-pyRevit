from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections.Generic import List

def group_beams_by_beam_system(beam_list):
  grouped_beams = {}
  for beam in beam_list:
    if BeamSystem.BeamBelongsTo(beam):
      beam_system = BeamSystem.BeamBelongsTo(beam)
      key = str(beam_system.Id)
      values = grouped_beams.get(key)
      if values:
        values.append(beam)
      else:
        values = [beam]
      updated_beams = {key: values}
      grouped_beams.update(updated_beams)
  return grouped_beams

def find_closest_grid(point, grids):
  point_x = point.X
  closest_grid = grids[0]
  for grid in grids:
    closest_grid_x = closest_grid.Curve.GetEndPoint(0).X
    grid_x = grid.Curve.GetEndPoint(0).X
    if abs(point_x - grid_x) < abs(point_x - closest_grid_x):
      closest_grid = grid
  return closest_grid

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

grids_collector = FilteredElementCollector(doc)\
                     .OfCategory(BuiltInCategory.OST_Grids)\
                     .WhereElementIsNotElementType()
plan_view_collector = FilteredElementCollector(doc)\
                     .OfClass(ViewPlan)\
                     .WhereElementIsNotElementType()

grid_list = list(grids_collector)
plan_view_list = list(plan_view_collector)
placed_plans = []

for plan in plan_view_list:
  if plan.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced:
    placed_plans.append(plan)
  else:
    continue

with revit.Transaction('Create Joist Dimensions'):
  for plan_view in placed_plans:

    beam_collector = FilteredElementCollector(doc, plan_view.Id)\
                    .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                    .WhereElementIsNotElementType()

    beam_list = list(beam_collector)
    grouped_bs_beams = group_beams_by_beam_system(beam_list)

    for key in grouped_bs_beams.keys():
      beam_system = doc.GetElement(ElementId(int(key)))
      beams = grouped_bs_beams.get(key)
      beam_system_bb = beam_system.get_BoundingBox(plan_view)
      bs_min_pt = beam_system_bb.Min
      bs_max_pt = beam_system_bb.Max
      min_grid = find_closest_grid(bs_min_pt, grid_list)
      max_grid = find_closest_grid(bs_max_pt, grid_list)
      min_grid_x = min_grid.Curve.GetEndPoint(0).X
      max_grid_x = max_grid.Curve.GetEndPoint(0).X
      beam_curve = beams[0].Location.Curve
      point_y = beam_curve.Evaluate(0.3, True).Y
      beam_system_ref_arr = ReferenceArray()
      beam_system_ref_arr.Append(Reference(min_grid))
      beam_system_ref_arr.Append(Reference(max_grid))
      start_pt = XYZ(min_grid_x, point_y, 0)
      end_pt = XYZ(max_grid_x, point_y, 0)
      dim_line = Line.CreateBound(start_pt, end_pt)
      num_of_bays = len(beams) + 1
      dim = doc.Create.NewDimension(plan_view, dim_line, beam_system_ref_arr)
      dim.Prefix = str(num_of_bays) + " EQ SP = "











