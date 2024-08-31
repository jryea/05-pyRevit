from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections.Generic import List

def get_vector_from_elem(line_based_elem, elem_type):
  line = None
  if elem_type.lower() == "grid":
    line = line_based_elem.Curve
  elif elem_type.lower() == "beam"\
    or elem_type.lower() == "wall":
    line = line_based_elem.Location.Curve
  else:
    print("Please select a beam or grid")
    return None
  startpoint = line.GetEndPoint(0)
  endpoint = line.GetEndPoint(1)
  vector = endpoint - startpoint
  normalized_vector = vector.Normalize()
  return normalized_vector

def get_min_max_walls(walls_list, direction = 'horiz'):
  min_wall = walls_list[0]
  max_wall = walls_list[0]
  if direction.lower() == "horiz" \
  or direction.lower() == "horizontal":
    for wall in walls_list:
      wall_y = wall.Location.Curve.GetEndPoint(0).Y
      max_wall_y = max_wall.Location.Curve.GetEndPoint(0).Y
      min_wall_y = min_wall.Location.Curve.GetEndPoint(0).Y
      if wall_y > max_wall_y:
        max_wall = wall
      if wall_y < min_wall_y:
        min_wall = wall
  if direction.lower() == "vert" \
  or direction.lower() == "vertical":
    for wall in walls_list:
      wall_x = wall.Location.Curve.GetEndPoint(0).X
      max_wall_x = max_wall.Location.Curve.GetEndPoint(0).X
      min_wall_x = min_wall.Location.Curve.GetEndPoint(0).X
      if wall_x > max_wall_x:
        max_wall = wall
      if wall_x < min_wall_x:
        min_wall = wall
  return {"max_wall": max_wall, "min_wall": min_wall}

def get_min_max_endpoints(line):
  max_x = None
  min_x = None
  max_y = None
  min_y = None
  start_pt_x = line.GetEndPoint(0).X
  start_pt_y = line.GetEndPoint(0).Y
  end_pt_x = line.GetEndPoint(1).X
  end_pt_y = line.GetEndPoint(1).Y
  if start_pt_x >= end_pt_x:
    min_x = end_pt_x
    max_x = start_pt_x
  else:
    min_x = start_pt_x
    max_x = end_pt_x
  if start_pt_y >= end_pt_y:
    min_y = end_pt_y
    max_y = start_pt_y
  return {"min_x": min_x, "max_x": max_x, "min_y": min_y, "max_y":max_y}

# From Michael Killkelly's demo on wall dimensioning
# https://github.com/kilkellym/RAA_HowTo_DimensionElements/blob/master/RAA_HowTo_DimensionElements/Command1.cs

def get_face(elem, orientation):
  return_face = None
  solids = get_solids(elem)
  for solid in solids:
    for face in solid.Faces:
      if type(face) == PlanarFace:
        planar_face = face
        # Determines whether 2 vectors are the same withing a given tolerance
        if planar_face.FaceNormal.IsAlmostEqualTo(orientation):
          return_face = planar_face
  return return_face

def get_solids(elem):
  return_list = []

  options = Options()
  options.ComputeReferences = True
  options.DetailLevel = ViewDetailLevel.Fine

  geometry_elem = elem.get_Geometry(options)

  for geometry in geometry_elem:
    if type(geometry) == Solid:
      solid = geometry
      if solid.Faces.Size > 0 and solid.Volume > 0.0:
        return_list.append(solid)
  return return_list

def get_offset_by_wall_orientation(point, orientation, value):
  new_vector = orientation.Multiply(value)
  return_point = point.Add(new_vector)

def is_line_vert(line):
  if line.Direction.IsAlmostEqualTo(XYZ.BasisZ)\
     or line.Direction.IsAlmostEqualTo(-XYZ.BasisZ):
    return True
  else:
    return False

def create_wall_dim_string(grids, walls, wall_dim_base, dim_offset):
  wall_faces = [get_face(wall, wall.Orientation) for wall in walls]
  edge_loops = [wall_face.EdgeLoops.get_Item(0) for wall_face\
                                in wall_faces]
  edge_list_list = []
  for edge_loop in edge_loops:
    edge_list = []
    for edge in edge_loop:
      edge_line = edge.AsCurve()
      if is_line_vert(edge_line):
        edge_list.append(edge)
    edge_list_list.append(edge_list)

  ref_array = ReferenceArray()
  for grid in grids:
    ref_array.Append(Reference(grid))

  for edges_list in edge_list_list:
    ref_array.Append(edges_list[0].Reference)

  string_elems = walls + grids

  wall_dim_base_line = wall_dim_base.Location.Curve

  start_pt_x = None
  start_pt_y = None
  end_pt_x = None
  end_pt_y = None
  print(wall_dim_base_line.Direction)
  print(wall_dim_base)
  if wall_dim_base_line.Direction.IsAlmostEqualTo(XYZ.BasisY)\
     or wall_dim_base_line.Direction.IsAlmostEqualTo(-XYZ.BasisY):
    print('True!')

    start_pt_x = wall_dim_base_line.GetEndPoint(0).X + dim_offset
    end_pt_x = start_pt_x

    if type(string_elems[0]) == Grid:
      start_pt_y = string_elems[0].Curve.GetEndPoint(0).Y
      end_pt_y = string_elems[-1].Curve.GetEndPoint(0).Y
    else:
      start_pt_y = string_elems[0].Location.Curve.GetEndPoint(0).Y
      end_pt_y = string_elems[-1].Curve.GetEndPoint(0).Y

  elif wall_dim_base_line.Direction.IsAlmostEqualTo(XYZ.BasisX)\
    or wall_dim_base_line.Direction.IsAlmostEqualTo(-XYZ.BasisX):
    print('False!')
    start_pt_y = wall_dim_base_line.GetEndPoint(0).Y + dim_offset
    end_pt_y = start_pt_y

    if type(string_elems[0]) == Grid:
      start_pt_x = string_elems[0].Curve.GetEndPoint(0).X
      end_pt_x = string_elems[-1].Curve.GetEndPoint(0).X
    else:
      start_pt_x = string_elems[0].Location.Curve.GetEndPoint(0).X
      end_pt_x = string_elems[-1].Curve.GetEndPoint(0).X

  start_pt = XYZ(start_pt_x, start_pt_y, 0)
  end_pt = XYZ(end_pt_x, end_pt_y, 0)

  dim_line = Line.CreateBound(start_pt, end_pt)
  return_dim_string = doc.Create.NewDimension(active_view, dim_line, ref_array)

  return return_dim_string

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

wall_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_Walls)\
                .WhereElementIsNotElementType()
grid_collector = FilteredElementCollector(doc)\
                .OfClass(Grid)\
                .WhereElementIsNotElementType()

wall_list = list(wall_collector)
grid_list = list(grid_collector)

found_walls = [wall for wall in wall_list if "concrete" in Element.Name.GetValue(wall.WallType).lower()]

horiz_walls = [wall for wall in found_walls\
               if abs(int(get_vector_from_elem(wall, "wall").X)) == 1]
vert_walls = [wall for wall in found_walls\
              if abs(int(get_vector_from_elem(wall, "wall").Y)) == 1]

horiz_grids = [grid for grid in grid_list\
              if abs(int(get_vector_from_elem(grid, "grid").X)) == 1]
vert_grids = [grid for grid in grid_list if abs(int(get_vector_from_elem(grid, "grid").Y)) == 1]

# Getting the walls at the furthest extents
top_wall = get_min_max_walls(horiz_walls,'horiz')["max_wall"]
bottom_wall = get_min_max_walls(horiz_walls,'horiz')["min_wall"]
right_wall = get_min_max_walls(vert_walls,'vert')["max_wall"]
left_wall = get_min_max_walls(vert_walls,'vert')["min_wall"]

x_midpoint = abs((left_wall.Location.Curve.GetEndPoint(0).X + right_wall.Location.Curve.GetEndPoint(0).X)/2)
y_midpoint = abs((bottom_wall.Location.Curve.GetEndPoint(0).Y + top_wall.Location.Curve.GetEndPoint(0).Y)/2)

east_string_walls = [wall for wall in horiz_walls\
                      if get_min_max_endpoints(wall.Location.Curve)["max_x"] > x_midpoint]
west_string_walls = [wall for wall in horiz_walls\
                     if get_min_max_endpoints(wall.Location.Curve)["min_x"] < x_midpoint]
north_string_walls = [wall for wall in vert_walls\
                      if get_min_max_endpoints(wall.Location.Curve)["max_y"] > y_midpoint]
south_string_walls = [wall for wall in vert_walls\
                      if get_min_max_endpoints(wall.Location.Curve)["min_y"] < y_midpoint]


with revit.Transaction('Dimension Walls'):
  dim_offset = 6
  east_dim_string = create_wall_dim_string(horiz_grids, east_string_walls, right_wall, dim_offset)
  west_dim_string = create_wall_dim_string(horiz_grids, west_string_walls, left_wall, dim_offset)
  north_dim_string = create_wall_dim_string(vert_grids, north_string_walls, top_wall, dim_offset)
  south_dim_string = create_wall_dim_string(vert_grids, south_string_walls, bottom_wall, dim_offset)














