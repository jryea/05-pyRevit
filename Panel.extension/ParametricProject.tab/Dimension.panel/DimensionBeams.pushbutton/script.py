from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
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

# Grids must be parallel\
def is_closest_grid(beam, target_grid, grid_list):
  direction = get_direction(beam)
  closest_grid = target_grid
  beam_point = beam.Location.Curve.GetEndPoint(0)
  beam_coordinate = get_coordinate(direction, beam_point)

  for grid in grid_list:
    grid_point = grid.Curve.GetEndPoint(0)
    grid_coordinate = get_coordinate(direction, grid_point)
    closest_grid_point = closest_grid.Curve.GetEndPoint(0)
    closest_grid_coordinate = get_coordinate(direction, closest_grid_point)
    if abs(beam_coordinate - grid_coordinate)\
      < abs(beam_coordinate - closest_grid_coordinate):
      closest_grid = grid
  if target_grid.Id == closest_grid.Id:
    return True
  else:
    return False

def create_beam_grid_groupings(beams, grids, tolerance):
  horiz_beam_grid_groups = []
  vert_beam_grid_groups = []
  for grid in grids:
    beam_list = []
    grid_direction = get_direction(grid)
    grid_pt = grid.Curve.GetEndPoint(0)
    grid_coordinate = get_coordinate(grid_direction, grid_pt)
    for beam in beams:
      beam_direction = get_direction(beam)
      beam_pt = beam.Location.Curve.GetEndPoint(0)
      beam_coordinate = get_coordinate(beam_direction, beam_pt)
      if grid_direction == beam_direction:
        if abs(beam_coordinate - grid_coordinate) > tolerance:
          if is_closest_grid(beam, grid, grids) == True:
            beam_list.append(beam)
    if len(beam_list) > 0:
      if grid_direction == "horiz":
        horiz_beam_grid_groups.append((grid, beam_list))
      else:
        vert_beam_grid_groups.append((grid, beam_list))
  return {"horiz": horiz_beam_grid_groups, "vert": vert_beam_grid_groups}

framing_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.  OST_StructuralFraming)\
            .WhereElementIsNotElementType()
grid_collector = FilteredElementCollector(doc)\
                .OfClass(Grid)\
                .WhereElementIsNotElementType()

framing_list = list(framing_collector)
grid_list = list(grid_collector)
offset = 2

beam_list = [beam for beam in framing_list if type(beam.Host) != BeamSystem]

# print(len(framing_list))
# print(len(beam_list))

# all_horiz_beams = [beam for beam in beam_list if beam.Location.Curve.Direction\
#                   .IsAlmostEqualTo(beam.Location.Curve.Direction.BasisX)
#                   or beam.Location.Curve.Direction.IsAlmostEqualTo(-(beam.Location.Curve.Direction.BasisX))]

# all_vert_beams = [beam for beam in beam_list if beam.Location.Curve.Direction\
#                   .IsAlmostEqualTo(beam.Location.Curve.Direction.BasisY)
#                   or beam.Location.Curve.Direction.IsAlmostEqualTo(-(beam.Location.Curve.Direction.BasisY))]

# horiz_beams = [beam for beam in all_horiz_beams if type(beam.Host) != BeamSystem]
# vert_beams = [beam for beam in all_vert_beams if type(beam.Host) != BeamSystem]

# horiz_grids = [grid for grid in grid_list if grid.Curve.Direction.IsAlmostEqualTo(grid.Curve.Direction.BasisX)\
#             or grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisX))]
# vert_grids = [grid for grid in grid_list if grid.Curve.Direction.IsAlmostEqualTo(grid.Curve.Direction.BasisY)\
#             or grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisY))]

tolerance = 0.25/12

grid_beam_groupings = create_beam_grid_groupings(beam_list, grid_list, tolerance)
# print(grid_beam_groupings)

print(len(grid_beam_groupings["horiz"]))
print(len(grid_beam_groupings["vert"]))

for grouping in grid_beam_groupings["horiz"]:
  print(len(grouping[1]))

# horiz_beam_grid_pairs = []
# vert_beam_grid_pairs = []

# # It would be nice to not duplicate code here
# for beam in horiz_beams:
#   beam_pt_y = beam.Location.Curve.GetEndPoint(0).Y
#   closest_grid = horiz_grids[0]
#   for grid in horiz_grids:
#     closest_grid_y = closest_grid.Curve.GetEndPoint(0).Y
#     grid_y = grid.Curve.GetEndPoint(0).Y
#     if abs(grid_y - beam_pt_y) < abs(closest_grid_y - beam_pt_y):
#       closest_grid = grid
#   closest_grid_y = closest_grid.Curve.GetEndPoint(0).Y
#   if abs(beam_pt_y - closest_grid_y) >= tolerance:
#     horiz_beam_grid_pairs.append((beam, closest_grid))

# for beam in vert_beams:
#   beam_pt_x = beam.Location.Curve.GetEndPoint(0).X
#   closest_grid = vert_grids[0]
#   for grid in vert_grids:
#     closest_grid_x = closest_grid.Curve.GetEndPoint(0).X
#     grid_x = grid.Curve.GetEndPoint(0).X
#     if abs(grid_x - beam_pt_x) < abs(closest_grid_x - beam_pt_x):
#       closest_grid = grid
#   closest_grid_x = closest_grid.Curve.GetEndPoint(0).X
#   if abs(beam_pt_x - closest_grid_x) >= tolerance:
#     vert_beam_grid_pairs.append((beam, closest_grid))

with revit.Transaction('Dimension Beams'):
  for group in grid_beam_groupings["horiz"]:
    grid = group[0]
    beams = group[1]
    ## Will need to sort grids here. Create function
    last_beam = beams[-1]
    last_beam_pt = last_beam.Location.Curve.GetEndPoint(0)
    start_pt = last_beam_pt.Add(last_beam_pt.BasisX.Multiply(-offset))
    grid_pt = grid.Curve.GetEndPoint(0)
    end_pt = XYZ(start_pt.X, grid_pt.Y, start_pt.Z)
    dim_line = Line.CreateBound(start_pt, end_pt)
    ref_array = ReferenceArray()
    ref_array.Append(Reference(grid))
    for beam in beams:
      ref_array.Append(Reference(beam))
    print(len(list(ref_array)))
    doc.Create.NewDimension(active_view, dim_line, ref_array)
    
  for group in grid_beam_groupings["vert"]:
    grid = group[0]
    beams = group[1]
    ## Will need to sort grids here. Create function
    last_beam = beams[-1]
    last_beam_pt = last_beam.Location.Curve.GetEndPoint(0)
    start_pt = last_beam_pt.Add(last_beam_pt.BasisY.Multiply(offset))
    grid_pt = grid.Curve.GetEndPoint(0)
    end_pt = XYZ(grid_pt.X, start_pt.Y, start_pt.Z)
    dim_line = Line.CreateBound(start_pt, end_pt)
    ref_array = ReferenceArray()
    ref_array.Append(Reference(grid))
    for beam in beams:
      ref_array.Append(Reference(beam))
    doc.Create.NewDimension(active_view, dim_line, ref_array)
    
  # for dim_pair in vert_beam_grid_pairs:
  #   beam_pt = dim_pair[0].Location.Curve.GetEndPoint(0)
  #   dim_pt = dim_pair[1].Curve.GetEndPoint(0)
  #   start_pt = beam_pt
  #   end_pt = XYZ(dim_pt.X, beam_pt.Y,beam_pt.Z)
  #   dim_line = Line.CreateBound(start_pt, end_pt)
  #   ref_array = ReferenceArray()
  #   ref_array.Append(Reference(dim_pair[0]))
  #   ref_array.Append(Reference(dim_pair[1]))
  #   doc.Create.NewDimension(active_view, dim_line, ref_array)











