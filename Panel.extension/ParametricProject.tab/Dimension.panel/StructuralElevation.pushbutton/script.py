from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections.Generic import List

## FUNCTIONS ###
def dist_between_closest_curve_points(axis, curve1, curve2):
  if axis.lower() == 'x':
    c1_1 = curve1.GetEndPoint(0).X
    c1_2 = curve1.GetEndPoint(1).X
    c2_1 = curve2.GetEndPoint(0).X
    c2_2 = curve2.GetEndPoint(1).X
  if axis.lower() == 'y':
    c1_1 = curve1.GetEndPoint(0).Y
    c1_2 = curve1.GetEndPoint(1).Y
    c2_1 = curve2.GetEndPoint(0).Y
    c2_2 = curve2.GetEndPoint(1).Y
  dist = abs(c1_1 - c2_1)
  if abs(c1_1 - c2_2) < dist:
    dist = abs(c1_1 - c2_2)
  if abs(c1_2 - c2_1) < dist:
    dist = abs(c1_2 - c2_1)
  if abs(c1_2 - c2_2):
    dist = abs(c1_2 - c2_2)
  return dist

def get_base_elev(curve):
  base_elev = None
  pt1 = curve.GetEndPoint(0)
  pt2 = curve.GetEndPoint(1)
  if pt1.Z < pt2.Z:
    base_elev = pt1.Z
  else:
    base_elev = pt2.Z
  return base_elev

def get_brace_axis(facing_orientation):
  x = facing_orientation.X
  y = facing_orientation.Y
  if x > y:
    return 'y'
  else:
    return 'x'

def create_brace_pairs(braces):
  brace_list = braces
  brace_pairs = []
  tolerance = .01
  for i1, brace1 in enumerate(brace_list):
    brace_pair = []
    closest_dist = 100
    closest_brace_index = 0
    hand_orientation = brace.HandOrientation
    b1_FO = brace1.FacingOrientation
    axis = get_brace_axis(b1_FO)
    b1_curve = brace1.Location.Curve
    base_z1 = get_base_elev(b1_curve)
    brace_pair.append(brace_list.pop(i1))
    print(len(brace_list))
    for i2, brace2 in enumerate(brace_list):
      b2_curve = brace2.Location.Curve
      b2_FO = brace2.FacingOrientation
      base_z2 = get_base_elev(brace2.Location.Curve)
      ## Checking if braces are on the same elevation
      if (base_z1 < base_z2 + tolerance and base_z1 > base_z2 - tolerance):
        ## Checking if braces have the same orientation
        if b1_FO.IsAlmostEqualTo(b2_FO) or b1_FO.IsAlmostEqualTo(-(b2_FO)):
          dist = dist_between_closest_curve_points(axis, b1_curve, b2_curve)
          if dist < closest_dist:
            closest_brace_index = i2
            closest_dist = dist
      brace_pair.append(brace_list.pop(closest_brace_index))
      print(len(brace_list))
      brace_pairs.append(brace_pair)
      print(len(brace_pairs))
  return brace_pairs


uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

## Get user selected elements
selection = uidoc.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

### VARIABLES ###
elevation_view_type_name = "Show View Name"

### COLLECTORS ###
framing_collector = FilteredElementCollector(doc)\
                    .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                    .WhereElementIsNotElementType()

vft_collector = FilteredElementCollector(doc)\
                        .OfClass(ViewFamilyType)\

view_plan_collector = FilteredElementCollector(doc)\
                      .OfCategory(BuiltInCategory.OST_Views)\
                      .WhereElementIsNotElementType()

framing_list = list(framing_collector)
vft_list = list(vft_collector)
view_plans = list(view_plan_collector)

brace_list = [brace for brace in framing_list\
              if brace.StructuralType\
              == Structure.StructuralType.Brace]

# print('Length of brace list: ')
# print(len(brace_list))

placed_view_plans = []

for plan in view_plans:
  if plan.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced:
    placed_view_plans.append(plan)
  else:
    continue

view_family_type = None
for vft in vft_list:
  if Element.Name.GetValue(vft) == elevation_view_type_name:
    view_family_type = vft

view_fam_type_section = None
for vft in vft_list:
  if vft.ViewFamily == ViewFamily.Section:
    view_family_type_section = vft

with revit.Transaction('Create Beams and Joists'):
  brace_pairs = create_brace_pairs(brace_list)
  # for i, brace_pair in enumerate(brace_pairs):
    # print('brace pair ' + str(i) + ":")
    # print('brace 1:')
    # print(brace_pair[0].HandOrientation)
    # print(get_base_elev(brace_pair[0].Location.Curve))
    # print('brace 2:')
    # print(brace_pair[1].HandOrientation)
    # print(get_base_elev(brace_pair[1].Location.Curve))
    # print('-----------------------------------------------------')
  # print(len(brace_pairs))
  print(brace_pairs)
  brace_pair_ids = []
  for brace in brace_pairs:
    brace_pair_ids.append(brace[0].Id)
    brace_pair_ids.append(brace[1].Id)
  brace_pair_Ilist = List[ElementId](brace_pair_ids)
  uidoc.Selection.SetElementIds(brace_pair_Ilist)

#   point = XYZ(-2, -66, 42)
#   elev_marker = ElevationMarker.CreateElevationMarker(doc, view_family_type.Id, point, 50)
#   framing_elevation = elev_marker.CreateElevation(doc,active_view.Id,1)
#   bb = framing_elevation.get_BoundingBox(None)
#   bb.Min = XYZ(point.X - 25/2, point.Z - 45, 0)
#   bb.Max = XYZ(point.X + 25/2, point.Z + 5, 0)
#   framing_elevation.CropBox = bb

#   depth_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
#   depth_param.Set(12)

#   # framing_elevation.CropBox = elevation_bb











