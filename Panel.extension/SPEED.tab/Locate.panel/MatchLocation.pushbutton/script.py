import clr
from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from utilities import selection
from System.Collections.Generic import List

def get_bb_center(bb):
  bb_min = bb.Min
  bb_max = bb.Max
  line = Line.CreateBound(bb_min, bb_max)
  center_pt = line.Evaluate(0.5, True)
  return center_pt

def get_line_intersection(line1, line2):
  results = clr.Reference[IntersectionResultArray]()
  result = line1.Intersect(line2, results)
  # Retrieve from C# strongbox
  int_result_array = results.Value
  if int_result_array:
    if result == SetComparisonResult.Overlap:
      int_pt = int_result_array.get_Item(0).XYZPoint
      return int_pt

## Return a list of lists: [y1,[X1, x2, x3, x4]][y2, [x1, x2, x3, x4]]
def get_line_intersections(lines):
  all_int_pts = []
  for i, line1 in enumerate(lines):
    other_lines = lines[i+1: -1]
    for line2 in other_lines:
      if get_line_intersection(line1, line2):
        line_int_pt = get_line_intersection(line1, line2)
        all_int_pts.append(line_int_pt)
  int_pts = all_int_pts
  return int_pts

def get_grid_curves(grids):
  grid_curves = []
  for grid in grids:
    grid_curve = grid.GetCurvesInView(DatumExtentType.ViewSpecific, active_view)[0]
    grid_curves.append(grid_curve)
  return grid_curves

def sort_x(pt):
  return pt.X

def sort_y(pt):
  return pt.Y

def get_min_max_pts(points):
  min_x_pt = points[0].X
  max_x_pt = points[0].X
  min_y_pt = points[0].Y
  max_y_pt = points[0].Y
  for pt in points:
    if pt.X < min_x_pt:
      min_x_pt = pt.X
    if pt.X > max_x_pt:
      max_x_pt = pt.X
    if pt.Y < min_y_pt:
      min_y_pt = pt.Y
    if pt.Y > max_y_pt:
      max_y_pt = pt.Y
  return {"min_x": min_x_pt, 'max_x': max_x_pt, 'min_y': min_y_pt,  'max_y': max_y_pt}

def get_grid_intersections(grids):
  grid_curves = get_grid_curves(grids)
  grid_pts = get_line_intersections(grid_curves)
  # grid_pts_sorted_y = sorted(grid_pts, key=sort_y)
  # sorted_y_pts = list(set(grid_pts_sorted_y))
  # for pt in sorted_y_pts:
  #   print(pt.Y)
  # grid_pts_sorted_x = sorted(grid_pts_sorted_y, key=sort_x)
  # grid_pts_sorted = grid_pts_sorted_x
  return grid_pts

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

floor_collector = FilteredElementCollector(doc)\
                  .OfCategory(BuiltInCategory.OST_Floors)
framing_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
column_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralColumns)\
                .WhereElementIsNotElementType()
direct_shape_collector = FilteredElementCollector(doc).OfClass(DirectShape)
grid_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_Grids)\
                .WhereElementIsNotElementType()

direct_shapes = list(direct_shape_collector)

grids = list(grid_collector)
floors = list(floor_collector)
framing = list(framing_collector)
columns = list(column_collector)

floor_ids = [elem.Id for elem in list(floors)]
framing_ids = [elem.Id for elem in list(framing_collector)]
column_ids = [elem.Id for elem in list(column_collector)]

all_element_ids = []
all_element_ids.extend(floor_ids)
all_element_ids.extend(framing_ids)
all_element_ids.extend(column_ids)
element_ids_List = List[ElementId](all_element_ids)

# print(len(direct_shapes))
# for shape in direct_shape_collector:
#   print(Element.Name.GetValue(shape))
# selection.return_selection(uidoc, list(direct_shapes))

if len(all_element_ids) == 0:
  forms.alert('No model elements found')
  script.exit()

if len(grids) == 0:
  forms.alert('Grids are needed to locate the imported model', title='Missing grids')
  script.exit()

grid_int_points = get_grid_intersections(grids)

min_x_pt = get_min_max_pts(grid_int_points)['min_x']
max_x_pt = get_min_max_pts(grid_int_points)['max_x']
min_y_pt = get_min_max_pts(grid_int_points)['min_y']
max_y_pt = get_min_max_pts(grid_int_points)['max_y']


import_sphere = None

error_title = 'Location'
error_message = "The imported model's location object not found"
if len(direct_shapes) > 0:
  for shape in direct_shapes:
    if (Element.Name.GetValue(shape) == 'import sphere'
    and shape.get_BoundingBox(None) != None):
      import_sphere = shape
      break
    else:
      forms.alert(error_message, error_title)
      script.exit()
else:
  forms.alert(error_message, error_title)
  script.exit()

bb = import_sphere.get_BoundingBox(None)

if bb == None:
  forms.alert('Location object not found')
  script.exit()

import_pt = get_bb_center(bb)
ll_grid_int_pt = XYZ(min_x_pt, min_y_pt, 0)

with revit.Transaction('Add Schedules and Notes'):
  move_group = doc.Create.NewGroup(element_ids_List)
  move_xyz = ll_grid_int_pt.Subtract(import_pt)
  ElementTransformUtils.MoveElement(doc, move_group.Id, move_xyz)
  move_group.UngroupMembers()
  doc.Delete(import_sphere.Id)



