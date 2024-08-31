from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

def create_grid_dimensions(grids, view, offset, dim_axis):
  sorted_grids = sort_grids_by_axis(grids, dim_axis)
  ref_array = ReferenceArray()
  for grid in grids:
    ref_array.Append(Reference(grid))
  start_grid = grids[0]
  end_grid = grids[1]
  grid_direction = start_grid.Curve.Direction
  start_pt = grids[0].Curve.GetEndPoint(1)
  line_start_pt = start_pt.Add(grid_direction.Multiply(-offset))
  end_pt = grids[1].Curve.GetEndPoint(1)
  line_end_pt = end_pt.Add(grid_direction.Multiply(-offset))
  grid_line = Line.CreateBound(line_start_pt, line_end_pt)
  doc.Create.NewDimension(view, grid_line, ref_array)


def set_grid_direction(grids, view):
  for grid in grids:
    grid_line = grid.GetCurvesInView(DatumExtentType.Model, view)[0]
    grid_direction = grid_line.Direction
    print(grid_direction)
    if grid_direction.IsAlmostEqualTo((grid_direction.BasisX))\
      or grid_direction.IsAlmostEqualTo(-(grid_direction.BasisY)):
      print('Need to reverse!')
      new_grid_line = grid_line.CreateReversed()
      grid.SetCurveInView(DatumExtentType.Model, view, new_grid_line)
    return None

def sort_grids_by_axis(grids, axis = 'X'):
  # Returns list
  sorted_grids = grids
  def sort_x(grid):
    return grid.Curve.GetEndPoint(0).X
  def sort_y(grid):
    return grid.Curve.GetEndPoint(0).Y
  if axis == 'X':
    sorted_grids.sort(key=sort_x)
  if axis == 'Y':
    sorted_grids.sort(key=sort_y)
  return sorted_grids

def get_min_or_max_grid(vector, grids, min_or_max = 'min'):
  if abs(vector.X) > abs(vector.Y):
    grids_sorted = sort_grids_by_axis(grids, 'Y')
  else:
    grids_sorted = sort_grids_by_axis(grids, 'X')
  if min_or_max == 'min':
    return grids_sorted[0]
  else:
    return grids_sorted[-1]

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView


grids_col = FilteredElementCollector(doc)\
          .OfClass(Grid)\
          .WhereElementIsNotElementType()
plan_view_collector = FilteredElementCollector(doc)\
                  .OfClass(ViewPlan)\
                  .WhereElementIsNotElementType()

grids_list = list(grids_col)
plan_list = list(plan_view_collector)

placed_plans = []

for plan in plan_list:
  if plan.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced:
    placed_plans.append(plan)
  else:
    continue

with revit.Transaction('Create Grids'):

  grids_horiz = [grid for grid in grids_list if grid.Curve.Direction\
                    .IsAlmostEqualTo(grid.Curve.Direction.BasisX) or\
                      grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisX))]
  grids_vert = [grid for grid in grids_list if grid.Curve.Direction\
                    .IsAlmostEqualTo(grid.Curve.Direction.BasisY) or\
                      grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisY))]
  sorted_grids_horiz = sort_grids_by_axis(grids_horiz, axis = 'Y')
  sorted_grids_vert = sort_grids_by_axis(grids_vert, axis = 'X')
  
  overall_horiz = [sorted_grids_horiz[0], sorted_grids_horiz[-1]]
  overall_vert = [sorted_grids_vert[0], sorted_grids_vert[-1]]
    
  for plan in placed_plans:
    
    overall_grid_dims_X = create_grid_dimensions(overall_vert, plan, 2, 'X')
    overall_grid_dims_Y = create_grid_dimensions(overall_horiz, plan, 2, 'Y')
    
    grid_dims_X = create_grid_dimensions(grids_vert, plan, 6, 'X')
    grid_dims_Y = create_grid_dimensions(grids_horiz, plan, 6, 'Y')
  
 
#   # Create dimension strings
#   horiz_
#   for grid in grids_horiz:
#     overall_reference_array = ReferenceArray()
#     grid_reference_array = ReferenceArray()

#     for grid in grids:
#       grid_curve = grid.GetCurvesInView(DatumExtentType.ViewSpecific, current_view)[0]
#       grid_start = grid_curve.GetEndPoint(0)
#       grid_end = grid_curve.GetEndPoint(1)
#       grid_reference_array.Append(Reference(grid))
#     overall_reference_array.Append(Reference(min_grid))
#     overall_reference_array.Append(Reference(max_grid))
#     doc.Create.NewDimension(current_view, overall_dim_line, overall_reference_array)
#     doc.Create.NewDimension(current_view, grid_dim_line, grid_reference_array)














