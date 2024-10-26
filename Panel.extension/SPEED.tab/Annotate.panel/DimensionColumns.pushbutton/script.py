from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from utilities.collection import Collection
from utilities import datum, families, geometry, selection
from System.Collections.Generic import List

# def is_line_vert(line):
#   line_direction = line.Direction
#   basis_y = line_direction.BasisY
#   if line_direction.IsAlmostEqualTo(basis_y)\
#     or line_direction.IsAlmostEqualTo(-(basis_y)):
#     return True
#   else:
#     return False

# def get_direction(elem):
#   curve = None
#   direction = None
#   if type(elem) == FamilyInstance:
#     curve = elem.Location.Curve
#   else:
#     curve = elem.Curve
#   if is_line_vert(curve) == True:
#     direction = 'vert'
#   else:
#     direction = 'horiz'
#   return direction

# def get_coordinate(direction, point):
#   coordinate = None
#   if direction == "horiz":
#     coordinate = point.Y
#   else:
#     coordinate = point.X
#   return coordinate

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

def get_closest_grid(point, grid_list):
  closest_grid = grid_list[0]
  closest_dist = geometry.get_dist_from_point_to_line(point, closest_grid.Curve)
  for grid in grid_list:
    line = grid.Curve
    dist = geometry.get_dist_from_point_to_line(point, line)
    if dist < closest_dist:
      closest_dist = dist
      closest_grid = grid
  return closest_grid

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
        closest_perp_grid = get_closest_grid(column.Location.Point, perp_grids)
        if len(sub_column_list) > 0:
          prev_column_perp_grid = get_closest_grid(sub_column_list[-1].Location.Point, perp_grids)
          column_perp_grid = get_closest_grid(column.Location.Point, perp_grids)
          if prev_column_perp_grid.Id.Equals(column_perp_grid.Id):
            sub_column_list.append(column)
          else:
            column_list.append(sub_column_list)
            sub_column_list = [column]
        else:
          sub_column_list.append(column)
    if len(sub_column_list) > 0:
      column_list.append(sub_column_list)
    if len(column_list) > 0:
      grid_column_groupings.append((grid, column_list))
  return grid_column_groupings

def offset_dim(dim_segment, dim_line, view_scale, dim_threshold):
  dim_center_pt = dim_line.Evaluate(0.5, True)
  dir_vector = dim_line.Direction
  direction = None
  if abs(dir_vector.X) > abs(dir_vector.Y):
    direction = 'horiz'
  else:
    direction = 'vert'
  offset_amount = 0.25/12 * view_scale
  if dim_segment.Value / view_scale < dim_threshold:
    text_pos = dim_segment.TextPosition
    new_text_pos = None
    if direction == 'horiz':
      if text_pos.X > dim_center_pt.X:
        new_text_pos = text_pos.Add(XYZ().BasisX.Multiply(offset_amount))
      else:
        new_text_pos = text_pos.Add(-XYZ().BasisX.Multiply(offset_amount))
    else:
      if text_pos.Y > dim_center_pt.Y:
        new_text_pos = text_pos.Add(XYZ().BasisY.Multiply(offset_amount))
      else:
        new_text_pos = text_pos.Add(-XYZ().BasisY.Multiply(offset_amount))
    dim_segment.TextPosition = new_text_pos

def offset_small_dims(dim, dim_line, view_scale, dim_threshold):
  offset_amount = 0.25/12 * view_scale
  if dim.HasOneSegment():
    offset_dim(dim, dim_line, view_scale, dim_threshold)
  else:
    dim_segment_arr = dim.Segments
    for dim_segment in dim_segment_arr:
      offset_dim(dim_segment, dim_line, view_scale, dim_threshold)

def offset_dim_line(doc, view, view_scale, dim_line):
  offset = 0.25/12 * view_scale
  dir_vector = dim_line.Direction
  direction = None
  if abs(dir_vector.X) > abs(dir_vector.Y):
    direction = 'horiz'
  else:
    direction = 'vert'
  grids = Collection.get_grids(doc)
  horiz_grids = datum.get_grids_by_angle(grids, 180)
  vert_grids = datum.get_grids_by_angle(grids, 90)
  start_point = dim_line.GetEndPoint(0)
  end_point = dim_line.GetEndPoint(1)
  new_dim_line = None
  if direction == 'horiz':
    closest_grid = get_closest_grid(start_point, horiz_grids)
    grid_y = closest_grid.Curve.GetEndPoint(0).Y
    point_y = start_point.Y
    if point_y > grid_y:
      new_start_point = start_point.Add(XYZ().BasisY.Multiply(offset))
      new_end_point = end_point.Add(XYZ().BasisY.Multiply(offset))
      new_dim_line = Line.CreateBound(new_start_point, new_end_point)
    else:
      new_start_point = start_point.Add(-XYZ().BasisY.Multiply(offset))
      new_end_point = end_point.Add(-XYZ().BasisY.Multiply(offset))
      new_dim_line = Line.CreateBound(new_start_point, new_end_point)
  else:
    closest_grid = get_closest_grid(start_point, vert_grids)
    grid_x = closest_grid.Curve.GetEndPoint(0).X
    point_x = start_point.X
    if point_x > grid_x:
      new_start_point = start_point.Add(XYZ().BasisX.Multiply(offset))
      new_end_point = end_point.Add(XYZ().BasisX.Multiply(offset))
      new_dim_line = Line.CreateBound(new_start_point, new_end_point)
    else:
      new_start_point = start_point.Add(-XYZ().BasisX.Multiply(offset))
      new_end_point = end_point.Add(-XYZ().BasisX.Multiply(offset))
      new_dim_line = Line.CreateBound(new_start_point, new_end_point)
  return new_dim_line

def create_dimensions_from_grid_col_groupings(view, grid_col_groupings, view_scale, dim_threshold):
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
      offset_line = offset_dim_line(doc, view, view_scale, dim_line)
      new_dim = doc.Create.NewDimension(view, offset_line, ref_array)
      doc.Regenerate()
      offset_small_dims(new_dim, dim_line,view_scale, dim_threshold)

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

offset = 2
tolerance = 2.0/12
dim_segment_threshold = 0.375/12

with revit.Transaction('Dimension Columns'):

  view_scale = active_view.Scale

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

  create_dimensions_from_grid_col_groupings(active_view, horiz_grid_col_groupings, view_scale, dim_segment_threshold)

  create_dimensions_from_grid_col_groupings(active_view, vert_grid_col_groupings, view_scale, dim_segment_threshold)


















