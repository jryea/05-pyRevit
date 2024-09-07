import math
from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from System.Collections.Generic import List

### VARIABLES ###
elevation_view_type_name = "Show View Name"
view_classification = "DOCUMENT"
elevation_template_name = "S - Structural Framing (document)"
elev_name = "FRAMING ELEVATION "
beam_tag_family_name = "IMEG_Structural Framing Tag"
beam_tag_type_name = "Standard"
column_tag_family_name = "IMEG_Structural Column Tag"
column_tag_type_name = "45"
tag_offset = 0.75
text_note_type_name = 'IMEG_3/32" Arial (arrow)'
elevation_beam_text = "STEEL BEAM - SEE PLAN"
elevation_column_text = "STEEL COLUMN - SEE PLAN"

def is_framing_direction_taggable(view_direction, framing_elem):
  framing_elem_FO = framing_elem.FacingOrientation
  if view_direction.IsAlmostEqualTo(XYZ.BasisY)\
  or view_direction.IsAlmostEqualTo(-(XYZ.BasisY)):
    if framing_elem_FO.IsAlmostEqualTo(XYZ.BasisX)\
    or framing_elem_FO.IsAlmostEqualTo(-(XYZ.BasisX)):
      return False
    else:
      return True
  else:
    if framing_elem_FO.IsAlmostEqualTo(XYZ.BasisY)\
    or framing_elem_FO.IsAlmostEqualTo(-(XYZ.BasisY)):
      return False
    else:
      return True


def get_perp_vector_positive_Z(vector, facing_vector):
  perp_vector = vector.CrossProduct(facing_vector)
  if perp_vector.Z < 0:
    perp_vector = perp_vector.Negate()
  return perp_vector

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
  if abs(x) > abs(y):
    return 'y'
  else:
    return 'x'

def get_min_max_numbers(numbers):
  sorted_numbers = sorted(numbers)
  min_num = sorted_numbers[0]
  max_num = sorted_numbers[-1]
  return {"min": min_num, "max": max_num}

def get_brace_min_max_coord(axis, brace1, brace2):
  min_coord = None
  max_coord = None
  b1_curve = brace1.Location.Curve
  b2_curve = brace2.Location.Curve
  brace_coord_list = []
  if axis.lower() == 'x':
    brace_coord_list.append(b1_curve.GetEndPoint(0).X)
    brace_coord_list.append(b1_curve.GetEndPoint(1).X)
    brace_coord_list.append(b2_curve.GetEndPoint(0).X)
    brace_coord_list.append(b2_curve.GetEndPoint(1).X)
  else:
    brace_coord_list.append(b1_curve.GetEndPoint(0).Y)
    brace_coord_list.append(b1_curve.GetEndPoint(1).Y)
    brace_coord_list.append(b2_curve.GetEndPoint(0).Y)
    brace_coord_list.append(b2_curve.GetEndPoint(1).Y)
  min_coord = get_min_max_numbers(brace_coord_list)["min"]
  max_coord = get_min_max_numbers(brace_coord_list)["max"]
  return {"min": min_coord, "max": max_coord}

def is_facing_orientation_equal(b1_FO, b2_FO):
  if b1_FO.IsAlmostEqualTo(b2_FO) or b1_FO.IsAlmostEqualTo(-(b2_FO)):
    return True
  else:
    return False

def are_coords_same(coord1, coord2, tolerance):
  if (coord1 < coord2 + tolerance
  and coord1 > coord2 - tolerance):
    return True
  else:
    return False

def do_brace_pair_extents_overlap(axis, bp1, bp2):
  b1_bp1 = bp1[0]
  b2_bp1 = bp1[1]
  b1_bp2 = bp2[0]
  b2_bp2 = bp2[1]
  bp1_extents = get_brace_min_max_coord(axis, b1_bp1, b2_bp1)
  bp1_min = bp1_extents["min"]
  bp1_max = bp1_extents["max"]
  bp2_extents = get_brace_min_max_coord(axis, b1_bp2, b2_bp2)
  bp2_min = bp2_extents["min"]
  bp2_max = bp2_extents["max"]
  if bp2_min > bp1_max or bp2_max < bp1_min:
    return False
  else:
    return True

def get_brace_pair_group_extents(brace_pair_group):
  bp1 = brace_pair_group[0]
  bpg_z_coords =[]
  bpg_xy_coords = []
  b1 = bp1[0]
  b1_FO = b1.FacingOrientation
  #Get axis
  axis = get_brace_axis(b1_FO)
  #Get axis coord
  axis_coord = None
  if axis == 'x':
    axis_coord = b1.Location.Curve.GetEndPoint(0).Y
  else:
    axis_coord = b1.Location.Curve.GetEndPoint(0).X

  for bp in brace_pair_group:
    b1 = bp[0]
    b1_curve = b1.Location.Curve
    b2 = bp[1]
    b2_curve = b2.Location.Curve
    #Get Z min and max for each pair and add to total
    b1_z1 = b1_curve.GetEndPoint(0).Z
    b1_z2 = b1_curve.GetEndPoint(1).Z
    b2_z1 = b2_curve.GetEndPoint(0).Z
    b2_z2 = b2_curve.GetEndPoint(1).Z
    z_coord_list = [b1_z1,b1_z2,b2_z1,b2_z2]
    bpg_z_coords.extend(z_coord_list)
    #Get XY extents coordinates
    xy_coord_extents = get_brace_min_max_coord(axis, b1, b2)
    xy_coord_list = [xy_coord_extents["min"], xy_coord_extents["max"]]
    bpg_xy_coords.extend(xy_coord_list)
  z_extents = get_min_max_numbers(bpg_z_coords)
  xy_extents = get_min_max_numbers(bpg_xy_coords)
  min_z = z_extents["min"]
  max_z = z_extents["max"]
  min_xy = xy_extents["min"]
  max_xy = xy_extents["max"]
  return {"axis": axis, "axis_coord": axis_coord,"min_z": min_z, "max_z": max_z, "min_xy": min_xy, "max_xy": max_xy}

def create_brace_pairs(braces):
  brace_list = braces
  brace_ids_found = []
  brace_pairs = []
  tolerance = .01
  for brace1 in brace_list:
    b1_int_id = brace1.Id.IntegerValue
    if b1_int_id not in brace_ids_found:
      brace_pair = []
      brace_ids_found.append(b1_int_id)
      brace_pair.append(brace1)
      b1_HO = brace.HandOrientation
      b1_FO = brace1.FacingOrientation
      b1_axis = get_brace_axis(b1_FO)
      b1_curve = brace1.Location.Curve
      b1_base_z = get_base_elev(b1_curve)
      closest_brace = None
      closest_dist = 100
      for brace2 in brace_list:
        b2_int_id = brace2.Id.IntegerValue
        # Check to see if brace 2 not already added to brace pairs
        if b2_int_id not in brace_ids_found:
          b2_curve = brace2.Location.Curve
          b2_FO = brace2.FacingOrientation
          b2_base_z = get_base_elev(brace2.Location.Curve)
          ## Checking if braces are on the same elevation
          if (b1_base_z < b2_base_z + tolerance and b1_base_z > b2_base_z - tolerance):
            ## Checking if braces have the same orientation
            if b1_FO.IsAlmostEqualTo(b2_FO) or b1_FO.IsAlmostEqualTo(-(b2_FO)):
              dist = dist_between_closest_curve_points(b1_axis, b1_curve, b2_curve)
              if dist < closest_dist:
                closest_dist = dist
                closest_brace = brace2
      closest_brace_id = closest_brace.Id.IntegerValue
      brace_ids_found.append(closest_brace_id)
      brace_pair.append(closest_brace)
      brace_pairs.append(brace_pair)
  return brace_pairs

def get_vertical_brace_pairs(brace_pairs):
  elev_dif_tolerance = 4
  all_brace_pairs_vert = []
  brace_pair_ids = []
  # get_brace_axis(facing_orientation)
  for i1, bp1 in enumerate(brace_pairs):
    brace_pairs_vert = []
    b1 = bp1[0]
    b1_int_id = b1.Id.IntegerValue
    if b1_int_id not in brace_pair_ids:
      brace_pair_ids.append(b1_int_id)
      brace_pairs_vert.append(bp1)
      b1_curve = b1.Location.Curve
      b1_FO = b1.FacingOrientation
      bp1_base_elev = get_base_elev(b1_curve)
      bp1_axis = get_brace_axis(b1_FO)
      for i2, bp2 in enumerate(brace_pairs):
        b2 = bp2[0]
        b2_int_id = b2.Id.IntegerValue
        b2_FO = b2.FacingOrientation
        b2_curve = b2.Location.Curve
        bp2_base_elev = get_base_elev(b2_curve)
        # Check to see if brace pair has already been added
        if b2_int_id not in brace_pair_ids:
          # Check to see if elevation is different
          if are_coords_same(bp1_base_elev, bp2_base_elev, elev_dif_tolerance) == False:
              # Check to see if axis is the same
              if is_facing_orientation_equal(b1_FO, b2_FO):
                #Check to see if brace pair xy extents fall within second brace pair xy extents
                  if do_brace_pair_extents_overlap(bp1_axis, bp1, bp2):
                    brace_pair_ids.append(b2_int_id)
                    brace_pairs_vert.append(bp2)
      all_brace_pairs_vert.append(brace_pairs_vert)
  return all_brace_pairs_vert

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

selection = uidoc.Selection
selected_element_ids = selection.GetElementIds()
selected_elements = [doc.GetElement(element_id) for element_id in selected_element_ids]

### COLLECTORS ###
framing_collector = FilteredElementCollector(doc)\
                    .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                    .WhereElementIsNotElementType()

vft_collector = FilteredElementCollector(doc)\
                        .OfClass(ViewFamilyType)\

view_plan_collector = FilteredElementCollector(doc)\
                      .OfCategory(BuiltInCategory.OST_Views)\
                      .WhereElementIsNotElementType()

view_type_collector = FilteredElementCollector(doc)\
                      .OfCategory(BuiltInCategory.OST_Views)\

framing_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralFramingTags)\
                        .WhereElementIsElementType()

column_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralColumnTags)\
                        .WhereElementIsElementType()

text_note_type_collector = FilteredElementCollector(doc)\
                          .OfCategory(BuiltInCategory.OST_TextNotes)\
                          # .WhereElementIsElementType()

framing_list = list(framing_collector)
vft_list = list(vft_collector)
view_plans = list(view_plan_collector)
view_type_list = list(view_type_collector)
view_templates = [view for view in view_type_list if view.IsTemplate]
framing_template = [view for view in view_templates if Element.Name.GetValue(view) == elevation_template_name][0]
framing_tag_types = list(framing_tag_collector)
column_tag_types = list(column_tag_collector)
text_note_type_list = list(text_note_type_collector)
text_note_type = [text for text in text_note_type_list\
                  if Element.Name.GetValue(text)][0]
text_note_type_id = text_note_type.GetTypeId()

brace_list = [brace for brace in framing_list\
              if brace.StructuralType\
              == Structure.StructuralType.Brace]

beam_tag = [tag for tag in framing_tag_types\
            if Element.Name.GetValue(tag) == beam_tag_type_name\
            and tag.FamilyName == beam_tag_family_name][0]

column_tag = [tag for tag in column_tag_types\
             if Element.Name.GetValue(tag) ==  column_tag_type_name\
              and tag.FamilyName == column_tag_family_name][0]

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

framing_elevations = []

with revit.Transaction('Create Framing Elevations'):
  brace_pairs = create_brace_pairs(brace_list)
  brace_pair_ids = []
  brace_pair_groups_vertical = get_vertical_brace_pairs(brace_pairs)
  for index, bpg in enumerate(brace_pair_groups_vertical):
    bpg_extents = get_brace_pair_group_extents(bpg)
    axis = bpg_extents["axis"]
    axis_coord = bpg_extents["axis_coord"]
    min_z = bpg_extents["min_z"]
    max_z = bpg_extents["max_z"]
    mid_z = ((min_z + max_z) / 2)
    min_xy = bpg_extents["min_xy"]
    max_xy = bpg_extents["max_xy"]
    mid_xy = ((min_xy + max_xy) / 2)
    height = abs(max_z - min_z)
    width = abs(max_xy - min_xy)
    elevation_marker_offset = 6
    framing_view_border = 3
    point = None
    elev_marker = None
    framing_elev = None
    elev_name_suffix = None
    if index < 10:
      elev_name_suffix = "0" + str(index+1)
    else:
      elev_name_suffix = str(index+1)
    framing_elev_name = elev_name  + elev_name_suffix

    if axis.lower() == 'x':
      point = XYZ(mid_xy, axis_coord - elevation_marker_offset, mid_z)
      elev_marker = ElevationMarker.CreateElevationMarker(doc, view_family_type.Id, point, 50)
      framing_elevation = elev_marker.CreateElevation(doc,active_view.Id,1)
      depth_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
      depth_param.Set(12)
      bb = framing_elevation.get_BoundingBox(None)
      bb.Min = XYZ(point.X - width/2 - framing_view_border, point.Z - height/2 - framing_view_border, 0)
      bb.Max = XYZ(point.X + width/2 + framing_view_border, point.Z + height/2 + framing_view_border, 0)
      framing_elevation.CropBox = bb
      framing_elevation.ViewTemplateId = framing_template.Id
      framing_elevation.Name = framing_elev_name
      depth_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
      depth_param.Set(12)
      framing_elevations.append(framing_elevation)
      annotation_crop_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE)
      annotation_crop_param.Set(True)

    else:
      point = XYZ(axis_coord  + elevation_marker_offset, mid_xy, mid_z)
      elev_marker = ElevationMarker.CreateElevationMarker(doc, view_family_type.Id, point, 50)
      framing_elevation = elev_marker.CreateElevation(doc,active_view.Id,0)
      framing_elevation.Name = framing_elev_name
      bb = framing_elevation.get_BoundingBox(None)
      bb.Min = XYZ(point.Y - width/2 - framing_view_border, point.Z - height/2 - framing_view_border, 0)
      bb.Max = XYZ(point.Y + width/2 + framing_view_border, point.Z + height/2 + framing_view_border, 0)
      framing_elevation.CropBox = bb
      framing_elevation.ViewTemplateId = framing_template.Id
      depth_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_BOUND_OFFSET_FAR)
      depth_param.Set(12)
      framing_elevations.append(framing_elevation)
      annotation_crop_param = framing_elevation.get_Parameter(BuiltInParameter.VIEWER_ANNOTATION_CROP_ACTIVE)
      annotation_crop_param.Set(True)

with revit.Transaction('Tag Elevations'):

  for elevation in framing_elevations:

    column_collector = FilteredElementCollector(doc, elevation.Id)\
                    .OfCategory(BuiltInCategory.OST_StructuralColumns)\
                    .WhereElementIsNotElementType()
    framing_collector = FilteredElementCollector(doc, elevation.Id)\
                    .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                    .WhereElementIsNotElementType()

    column_list = list(column_collector)
    framing_list = list(framing_collector)
    brace_list = [brace for brace in framing_list\
              if brace.StructuralType\
              == Structure.StructuralType.Brace]
    beam_list = [beam for beam  in framing_list\
                  if beam.StructuralType\
                  == Structure.StructuralType.Beam]

    view_direction = elevation.ViewDirection

    for brace in brace_list:
      brace_curve = brace.Location.Curve
      brace_facing_xyz = brace.FacingOrientation
      brace_hand_xyz = brace.HandOrientation

      offset_direction = get_perp_vector_positive_Z(brace_hand_xyz, brace_facing_xyz)
      midpoint = brace_curve.Evaluate(0.5, True)
      point = midpoint.Add(offset_direction.Multiply(tag_offset))

      if is_framing_direction_taggable(view_direction, brace):
        tag = IndependentTag.Create(doc, beam_tag.Id, elevation.Id, Reference(brace), False, TagOrientation.AnyModelDirection, point)

    beam_tag_offset = tag_offset + 0.2
    for beam in beam_list:
      beam_curve = beam.Location.Curve
      beam_facing_xyz = beam.FacingOrientation
      beam_hand_xyz = beam.HandOrientation

      offset_direction = get_perp_vector_positive_Z(beam_hand_xyz, beam_facing_xyz)
      midpoint = beam_curve.Evaluate(0.5, True)
      point = midpoint.Add(offset_direction.Multiply(beam_tag_offset + 0.3))

      beam_text_note_options = TextNoteOptions(text_note_type_id)
      beam_text_note_options.HorizontalAlignment = HorizontalTextAlignment.Center
      if is_framing_direction_taggable(view_direction, beam):
        text_note = TextNote.Create(doc, elevation.Id, point, elevation_beam_text, beam_text_note_options)

    for column in column_list:
      column_xy_point = column.Location.Point
      column_bb = column.get_BoundingBox(None)
      column_base_z = column_bb.Min.Z
      column_top_z = column_bb.Max.Z
      mid_z = (column_base_z + column_top_z)/2
      point = None

      if view_direction.IsAlmostEqualTo(XYZ.BasisX)\
        or view_direction.IsAlmostEqualTo(-(XYZ.BasisX)):
        point = XYZ(column_xy_point.X, column_xy_point.Y - (tag_offset + 0.5), mid_z)
      else:
        point = XYZ(column_xy_point.X - (tag_offset + 0.5),  column_xy_point.Y, mid_z)

      col_text_note_options = TextNoteOptions(text_note_type_id)
      col_text_note_options.HorizontalAlignment = HorizontalTextAlignment.Center
      col_text_note_options.Rotation = 90*math.pi/180
      text_note = TextNote.Create(doc, elevation.Id, point, elevation_column_text, col_text_note_options)














