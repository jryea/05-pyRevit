from Autodesk.Revit.DB import *
from utilities.collection import Collection
from utilities import geometry
from System.Collections.Generic import List

# LEVELS
def find_closest_level_from_elevation(doc, elevation):
  levels = Collection.get_levels(doc)
  closest_level = levels[0]
  for level in levels:
    level_elev = level.ProjectElevation
    closest_level_elev = closest_level.ProjectElevation
    level_elev_diff = abs(elevation - level_elev)
    closest_level_elev_diff = abs(elevation - closest_level_elev)
    if level_elev_diff < closest_level_elev_diff:
      closest_level = level
  return closest_level

def get_top_level(doc):
  levels = Collection.get_levels(doc)
  top_level = levels[0]
  for level in levels:
    level_elevation = level.ProjectElevation
    top_level_elevation = top_level.ProjectElevation
    if level_elevation > top_level_elevation:
      top_level = level
  return top_level

def get_base_level(doc):
  levels = Collection.get_levels(doc)
  base_level = levels[0]
  for level in levels:
    level_elevation = level.ProjectElevation
    base_level_elevation = base_level.ProjectElevation
    if level_elevation < base_level_elevation:
      base_level = level
  return base_level

def get_level_above(doc, current_level):
  current_level_elevation = current_level.ProjectElevation
  levels = Collection.get_levels(doc)
  level_above = get_top_level(doc)
  if Element.Name.GetValue(level_above) == Element.Name.GetValue(current_level):
    return None
  for level in levels:
    level_above_elevation = level_above.ProjectElevation
    level_elevation = level.ProjectElevation
    if level_elevation > current_level_elevation\
    and level_elevation < level_above_elevation:
        level_above = level
  return level_above

def get_level_below(doc, current_level):
  current_level_elevation = current_level.ProjectElevation
  levels = Collection.get_levels(doc)
  level_below = get_base_level(doc)
  if Element.Name.GetValue(level_below) == Element.Name.GetValue(current_level):
    return None
  for level in levels:
    level_below_elevation = level_below.ProjectElevation
    level_elevation = level.ProjectElevation
    if level_elevation < current_level_elevation\
    and level_elevation > level_below_elevation:
        level_below = level
  return level_below

# GRIDS
def get_grid_angle(grid):
  grid_vector = grid.Curve.Direction
  grid_angle_rad = grid_vector.AngleTo(XYZ().BasisX)
  grid_angle = geometry.convert_rad_to_deg(grid_angle_rad, integer=True)
  return grid_angle

def get_unique_grid_angles(grid_list):
  grid_angles = []
  for grid in grid_list:
    grid_angle = get_grid_angle(grid)
    grid_angles.append(grid_angle)
  grid_angles = list(set(grid_angles))
  return grid_angles

def sort_grids_by_angle(grid_list):
  grid_angles = get_unique_grid_angles(grid_list)
  grids_sorted_by_angle = []
  for grid_angle in grid_angles:
    grids_by_angle = []
    for grid in grid_list:
      cur_grid_angle = get_grid_angle(grid)
      if cur_grid_angle == grid_angle:
        grids_by_angle.append(grid)
    sort_parallel_grids(grids_by_angle)
    grids_sorted_by_angle.append(grids_by_angle)
  return grids_sorted_by_angle

def get_grids_by_angle(grids, angle):
  grids_by_angle = []
  for grid in grids:
    grid_angle = get_grid_angle(grid)
    if int(round(grid_angle)) == angle:
      grids_by_angle.append(grid)
  return grids_by_angle

def are_grids_parallel(grid_list):
  angle = get_grid_angle(grid_list[0])
  for grid in grid_list:
    grid_angle = get_grid_angle(grid)
    if grid_angle != angle:
      return False
  return True

def sort_parallel_grids(grid_list):
  if are_grids_parallel(grid_list) == False:
    print('Grids are not parallel')
    return None
  else:
    grid_angle = get_grid_angle(grid_list[0])
    if grid_angle > 45 and grid_angle < 135:
      grid_list.sort(key=lambda grid: grid.Curve.GetEndPoint(0).X)
    else:
      grid_list.sort(key=lambda grid: grid.Curve.GetEndPoint(0).Y)

def sync_grid_direction(grids, view):
  for grid in grids:
    grid_angle = get_grid_angle(grid)
    grid_curve = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)[0]
    grid_start = grid_curve.GetEndPoint(0)
    grid_end = grid_curve.GetEndPoint(1)
    grid_start_x = grid_start.X
    grid_end_x = grid_end.X
    grid_start_y = grid_start.Y
    grid_end_y = grid_end.Y
    is_start_bubble = grid.IsBubbleVisibleInView(DatumEnds.End0, view)
    is_end_bubble = grid.IsBubbleVisibleInView(DatumEnds.End1, view)
    if grid_angle > 45 and grid_angle < 135:
      if grid_end_y < grid_start_y:
        reversed_grid_curve = grid_curve.CreateReversed()
        grid.SetCurveInView(DatumExtentType.ViewSpecific, view, reversed_grid_curve)
        if is_end_bubble:
          grid.ShowBubbleInView(DatumEnds.End0, view)
        else:
          grid.HideBubbleInView(DatumEnds.End0, view)
        if is_start_bubble:
          grid.ShowBubbleInView(DatumEnds.End1, view)
        else:
          grid.HideBubbleInView(DatumEnds.End1, view)
        print('vertical grid reversed')
    else:
      if grid_end_x < grid_start_x:
        reversed_grid_curve = grid_curve.CreateReversed()
        grid.SetCurveInView(DatumExtentType.ViewSpecific, view, reversed_grid_curve)
        if is_end_bubble:
          grid.ShowBubbleInView(DatumEnds.End0, view)
        else:
          grid.HideBubbleInView(DatumEnds.End0, view)
        if is_start_bubble:
          grid.ShowBubbleInView(DatumEnds.End1, view)
        else:
          grid.HideBubbleInView(DatumEnds.End1, view)
        print('horizontal grid reversed')

## Assumes grids are sorted by angle
## Assumes grid direction is synced:
## left to right, bottom to top
def sort_grids_by_endpts(grids, view):
  grid_angle = get_grid_angle(grids[0])
  grids_by_startpts_grouped = []
  grids_by_endpts_grouped = []
  grids_by_startpts = []
  grids_by_endpts = []
  for i, grid in enumerate(grids):
    print('grid ' + str(i))
    grid_curve = grid.GetCurvesInView(DatumExtentType.ViewSpecific, view)[0]
    grid_startpt = grid_curve.GetEndPoint(0)
    grid_endpt = grid_curve.GetEndPoint(1)
    startpt_x = round(grid_startpt.X)
    endpt_x = round(grid_endpt.X)
    startpt_y = round(grid_startpt.Y)
    endpt_y = round(grid_endpt.Y)
    # Add first grid to both lists
    if len(grids_by_startpts) == 0:
      grids_by_startpts.append(grid)
      grids_by_endpts.append(grid)
      continue
    prev_startpt = (grids_by_startpts[-1]
                        .GetCurvesInView(DatumExtentType.ViewSpecific, view)[0]
                        .GetEndPoint(0))
    prev_endpt = (grids_by_endpts[-1]
                        .GetCurvesInView(DatumExtentType.ViewSpecific, view)[0]
                        .GetEndPoint(1))
    # Is grid vertical?
    if grid_angle > 45 and grid_angle < 135:
      startpt_coord = startpt_y
      endpt_coord = endpt_y
      prev_startpt_coord = round(prev_startpt.Y)
      prev_endpt_coord = round(prev_endpt.Y)
    # Is grid horizontal?
    else:
      startpt_coord = startpt_x
      endpt_coord = endpt_x
      prev_startpt_coord = round(prev_startpt.X)
      prev_endpt_coord = round(prev_endpt.X)

    if startpt_coord == prev_startpt_coord:
      grids_by_startpts.append(grid)
    else:
      grids_by_startpts_grouped.append(grids_by_startpts)
      grids_by_startpts = [grid]
    if endpt_coord == prev_endpt_coord:
      grids_by_endpts.append(grid)
    else:
      grids_by_endpts_grouped.append(grids_by_endpts)
      grids_by_endpts = [grid]
  grids_by_startpts_grouped.append(grids_by_startpts)
  grids_by_endpts_grouped.append(grids_by_endpts)
  return {'start_pts': grids_by_startpts_grouped, 'end_pts': grids_by_endpts_grouped}


