from Autodesk.Revit.DB import *
import math

### INTEGERS AND FLOATS  ###
def are_numbers_similiar(value1, value2, tolerance):
  if value1 < value2 + tolerance and value1 > value2 - tolerance:
    return True
  else:
    return False

def get_rounded_int(double):
  int(round(double))

### POINTS  ###

def get_points_from_lines(lines):
  all_points = []
  for line in lines:
    endpt1 = line.GetEndPoint(0)
    endpt2 = line.GetEndPoint(1)
    all_points.append(endpt1)
    all_points.append(endpt2)
  return all_points

def get_corner_points(pts):
  #Find max y and min y extents
  max_y = pts[0].Y
  min_y = pts[0].Y
  for pt in pts:
    if pt.Y > max_y:
      max_y = pt.Y
    if pt.Y < min_y:
      min_y = pt.Y
  max_y_pts = [pt for pt in pts if are_numbers_similiar(pt.Y, max_y, 1)]
  min_y_pts = [pt for pt in pts if are_numbers_similiar(pt.Y, min_y, 1)]

  # print('top pts list: ')
  # print(max_y_pts)
  # print('bottom pts list: ')
  # print(min_y_pts)

  tr_pt = max_y_pts[0]
  tr_x = tr_pt.X
  tl_pt = max_y_pts[0]
  tl_x = tl_pt.X
  br_pt = min_y_pts[0]
  br_x = br_pt.X
  bl_pt = min_y_pts[0]
  bl_x = bl_pt.X

  for pt in max_y_pts:
    pt_x = pt.X
    if pt_x > tr_x:
      tr_x = pt_x
      tr_pt = pt
    if pt_x < tl_x:
      tl_x = pt_x
      tl_pt = pt
  for pt in min_y_pts:
    pt_x = pt.X
    if pt_x > br_x:
      br_x = pt_x
      br_pt = pt
    if pt_x < bl_x:
      bl_x = pt_x
      bl_pt = pt

  return {'tl': tl_pt, 'tr': tr_pt, 'bl': bl_pt, 'br': br_pt}

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

def get_coords_from_pts(pts):
  x_coords = []
  y_coords = []
  z_coords = []
  for pt in pts:
    x_coords.append(pt.X)
    y_coords.append(pt.Y)
    z_coords.append(pt.Z)
  return {'x':x_coords, 'y':y_coords, 'z':z_coords}

def get_min_max_extents_from_pts(pt_list):
  x_min = pt_list[0].X
  y_min = pt_list[0].Y
  z_min = pt_list[0].Z
  x_max = pt_list[0].X
  y_max = pt_list[0].Y
  z_max = pt_list[0].Z
  x_coords = get_coords_from_pts(pt_list)['x']
  y_coords = get_coords_from_pts(pt_list)['y']
  z_coords = get_coords_from_pts(pt_list)['z']

  for coord in x_coords:
    if coord < x_min:
      x_min = coord
    if coord > x_max:
      x_max = coord
  for coord in y_coords:
    if coord < y_min:
      y_min = coord
    if coord > x_max:
      x_max = coord
  for coord in z_coords:
    if coord < z_min:
      z_min = coord
    if coord > z_max:
      z_max = coord

  return {'min': XYZ(x_min, y_min, z_min), 'max': XYZ(x_max, y_max, z_max)}


  start_pt = line.GetEndPoint(0)
  end_pt = line.GetEndPoint(1)

  # get vectors from line and point to line start point
  line_direction = (end_pt - start_pt).Normalize()
  point_direction = (point - start_pt).Normalize()

  # Check direction
  is_collinear = (line_direction.IsAlmostEqualTo(point_direction)
                  or line_direction.IsAlmostEqualTo(-point_direction))
  if is_collinear == False:
    return False
  
  # Check if the point is within the line segment bounds
  start_to_end_distance = start_pt.DistanceTo(end_pt)
  start_to_point_distance = start_pt.DistanceTo(point)
  end_to_point_distance = end_pt.DistanceTo(point)

  # Does the point lie withing the start and end distance?
  return_bool = abs(start_to_end_distance - (start_to_point_distance + end_to_point_distance)) < tolerance

  return return_bool

def is_point_on_line(line, point, tolerance):
  dist = get_dist_from_point_to_line(point, line)
  if dist < tolerance:
    return True
  else:
    return False

def get_dist_from_point_to_line(point, line):
  x0 = point.X
  y0 = point.Y
  x1 = line.GetEndPoint(0).X
  y1 = line.GetEndPoint(0).Y
  x2 = line.GetEndPoint(1).X
  y2 = line.GetEndPoint(1).Y

  dist = (abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1)
          / math.sqrt((y2-y1)**2 + (x2-x1)**2))

  return dist

def get_closest_point_on_line(point, line):
    # Extract coordinates for clarity
    x1 = point.X
    y1 = point.Y
    z1 = point.Z
    
    line_start = line.GetEndPoint(0)
    xa = line_start.X
    ya = line_start.Y
    za = line_start.Z
    
    line_end = line.GetEndPoint(1)
    xb = line_end.X
    yb = line_end.Y
    zb = line_end.Z
 
    # Direction vector of the line
    dx = xb - xa
    dy = yb - ya
    dz = zb - za

    # Vector from line_start (A) to point (P)
    apx = x1 - xa
    apy = y1 - ya
    apz = z1 - za

    # Dot products for projection
    dot_ap_d = apx * dx + apy * dy + apz * dz
    dot_d_d = dx * dx + dy * dy + dz * dz

    # Parameter t for the projection formula
    t = dot_ap_d / dot_d_d

    # Closest point on line
    closest_x = xa + t * dx
    closest_y = ya + t * dy
    closest_z = za + t * dz

    return XYZ(closest_x, closest_y, closest_z)


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

### BOUNDING BOX ###
def get_bb_center(bb):
  bb_min = bb.Min
  bb_max = bb.Max
  line = Line.CreateBound(bb_min, bb_max)
  center_pt = line.Evaluate(0.5, True)
  return center_pt

### VECTORS ####
def convert_rad_to_deg(rad, integer=False):
  degrees = rad * (180/math.pi)
  if integer:
    degrees = int(round(degrees))
  return degrees






