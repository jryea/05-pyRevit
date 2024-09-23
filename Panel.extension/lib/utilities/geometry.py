from Autodesk.Revit.DB import *

### INTEGERS AND FLOATS  ###
def are_numbers_similiar(value1, value2, tolerance):
  if value1 < value2 + tolerance and value1 > value2 - tolerance:
    return True
  else:
    return False

### POINTS  ###
def sort_min_max_pts(pt1, pt2):
  # Takes 2 points that define a box
  # Returns 2 points, the min being the lower left point
  # the max being the upper right point
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

  return (min_pt, max_pt)

### LINES  ###
def group_lines_by_xy_direction(lines):
  horiz_lines = []
  vert_lines = []
  for line in lines:
    tol = 0.01
    direction = line.Direction
    if (direction.IsAlmostEqualTo(XYZ().BasisX, tol)
        or direction.IsAlmostEqualTo(-XYZ().BasisX, tol)):
      horiz_lines.append(line)
    if (direction.IsAlmostEqualTo(XYZ().BasisY, tol)
        or direction.IsAlmostEqualTo(-XYZ().BasisY, tol)):
      vert_lines.append(line)
  return {'horiz': horiz_lines, 'vert': vert_lines}





