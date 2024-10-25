from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from utilities.collection import Collection
from utilities import datum, families, geometry, selection
from System.Collections.Generic import List

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

def is_line_vert(line):
  line_direction = line.Direction
  basis_y = line_direction.BasisY
  if line_direction.IsAlmostEqualTo(basis_y)\
    or line_direction.IsAlmostEqualTo(-(basis_y)):
    return True
  else:
    return False

def get_direction(elem):
  curve = None
  direction = None
  if type(elem) == FamilyInstance:
    curve = elem.Location.Curve
  else:
    curve = elem.Curve
  if is_line_vert(curve) == True:
    direction = 'vert'
  else:
    direction = 'horiz'
  return direction

def get_coordinate(direction, point):
  coordinate = None
  if direction == "horiz":
    coordinate = point.Y
  else:
    coordinate = point.X
  return coordinate

def is_closest_grid(column, target_grid, grid_list):
  point = column.Location.Point
  closest_grid = target_grid
  closest_dist = geometry.get_dist_from_point_to_line(point, closest_grid.Curve)
  for grid in grid_list:
    line = grid.Curve
    dist = geometry.get_dist_from_point_to_line(point, line)
    if dist < closest_dist:
      closest_dist = dist
      closest_grid = grid
  if closest_grid.Id.Equals(target_grid.Id):
    return True
  else:
    return False

def get_closest_grid(column, grid_list):
  point = column.Location.Point
  closest_grid = grid_list[0]
  closest_dist = geometry.get_dist_from_point_to_line(point, closest_grid.Curve)
  for grid in grid_list:
    line = grid.Curve
    dist = geometry.get_dist_from_point_to_line(point, line)
    if dist < closest_dist:
      closest_dist = dist
      closest_grid = grid
  return closest_grid

# collects columns that are off grid
def get_columns_off_grid(columns, grids, tolerance):
  columns_off_grid = []
  for column in columns:
    is_column_off_grid = True
    point = column.Location.Point
    for grid in grids:
      line = grid.Curve
      if geometry.is_point_on_line(line, point, tolerance):
        is_column_off_grid = False
    if is_column_off_grid:
      columns_off_grid.append(column)
  return columns_off_grid

def create_grid_column_groupings(columns, grids, perp_grids):
  grid_column_groupings = []
  for grid in grids:
    column_list = []
    sub_column_list = []
    for column in columns:
      if is_closest_grid(column, grid, grids):
        closest_perp_grid = get_closest_grid(column, perp_grids)
        print('Parallel Grid: ')
        print(Element.Name.GetValue(grid))
        print('Perpendicular Grid: ')
        print(Element.Name.GetValue(closest_perp_grid))
        if len(sub_column_list) > 0:
          prev_column_perp_grid = get_closest_grid(sub_column_list[-1], perp_grids)
          # print('---------------------------------------')
          # print('Previous closest column grid: ')
          # print(Element.Name.GetValue(prev_column_perp_grid))
          column_perp_grid = get_closest_grid(column, perp_grids)
          # print('Current closest column grid: ')
          # print(Element.Name.GetValue(prev_column_perp_grid))
          # print('---------------------------------------')
          if prev_column_perp_grid.Id.Equals(column_perp_grid.Id):
            print('True')
            sub_column_list.append(column)
          else:
            column_list.append(sub_column_list)
            print('False')
            sub_column_list = [column]
        else:
          sub_column_list.append(column)
      if len(sub_column_list) > 0:
        column_list.append(sub_column_list)
    if len(column_list) > 0:
      grid_column_groupings.append((grid, column_list))
  return grid_column_groupings

def create_dimensions_from_grid_col_groupings(grid_col_groupings):
  for group in grid_col_groupings:
    grid = group[0]
    column_groups = group[1]
    for columns in column_groups:
      ref_array = ReferenceArray()
      ref_array.Append(Reference(grid))
      points = []
      ref_elems = []
      ref_elems.append(grid)
      for column in columns:
        col_pt = column.Location.Point
        points.append(col_pt)
        point_ref = families.get_family_instance_point_reference(column)
        ref_array.Append(point_ref) 
      grid_pt = geometry.get_closest_point_on_line(points[0], grid.Curve)
      points.append(grid_pt)
      dim_line = Line.CreateBound(points[0], points[-1])
      doc.Create.NewDimension(active_view, dim_line, ref_array)

offset = 2
tolerance = 2.0/12

with revit.Transaction('Dimension Columns'):
  columns = (Collection()
             .add_columns(doc, active_view)
             .to_list())
  grids = Collection.get_grids(doc, active_view)

  horiz_grids = datum.get_grids_by_angle(grids, 180)
  vert_grids = datum.get_grids_by_angle(grids, 90)

  columns_off_horiz_grids = get_columns_off_grid(columns, horiz_grids, tolerance)
  columns_off_vert_grids = get_columns_off_grid(columns, vert_grids, tolerance)

  horiz_grid_col_groupings = create_grid_column_groupings(columns_off_horiz_grids, horiz_grids, vert_grids)
  vert_grid_col_groupings = create_grid_column_groupings(columns_off_vert_grids,vert_grids, horiz_grids)

  create_dimensions_from_grid_col_groupings(horiz_grid_col_groupings)
  create_dimensions_from_grid_col_groupings(vert_grid_col_groupings)

















