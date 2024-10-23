from Autodesk.Revit.DB import *
from pyrevit import revit, forms
from utilities.collection import Collection
from utilities import floors, datum, geometry
from utilities import floors as floor_utils

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

## VARIABLES ##
graphic_style_name = 'IMEG_MISC_02'
## Assuming a single linked document
arch_doc = Collection.get_linked_docs(doc)[0].GetLinkDocument()
arch_shafts = Collection.get_shafts(arch_doc)

def get_elevations_from_shaft(doc, shaft):
  base_level_element_id = shaft.get_Parameter(BuiltInParameter.WALL_BASE_CONSTRAINT).AsElementId()
  base_level = doc.GetElement(base_level_element_id)
  base_level_elevation = base_level.ProjectElevation
  base_offset = shaft.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).AsDouble()
  unconnected_height = shaft.get_Parameter(BuiltInParameter.WALL_USER_HEIGHT_PARAM).AsDouble()
  base_elevation = base_level_elevation + base_offset
  top_elevation = base_elevation + unconnected_height
  return {'base': base_elevation, 'top': top_elevation}

graphic_styles = Collection.get_graphic_styles(doc)
graphic_style = [gs for gs in graphic_styles if Element.Name.GetValue(gs) == graphic_style_name][0]

plan_views = Collection.get_plan_views(doc)

new_shafts = []

with revit.Transaction('Add Shafts'):
  for shaft in arch_shafts:
    base_arch_shaft_elevation = get_elevations_from_shaft(arch_doc, shaft)['base']
    top_arch_shaft_elevation = get_elevations_from_shaft(arch_doc, shaft)['top']
    base_level = datum.find_closest_level_from_elevation(doc, base_arch_shaft_elevation)
    top_level = datum.find_closest_level_from_elevation(doc, top_arch_shaft_elevation)

    # Shift levels if bottom and top levels are the same
    if Element.Name.GetValue(base_level) == Element.Name.GetValue(top_level):
      top_level_above = datum.get_level_above(doc, top_level)
      if top_level_above:
        top_level = top_level_above
      else:
        base_level_below = datum.get_level_below(doc, base_level)
        base_level = base_level_below

    base_level_elevation = base_level.ProjectElevation
    top_level_elevation = top_level.ProjectElevation

    base_elevation_offset = base_arch_shaft_elevation - base_level_elevation
    top_elevation_offset = top_arch_shaft_elevation - top_level_elevation

    curve_array = shaft.BoundaryCurves
    new_shaft = doc.Create.NewOpening(base_level, top_level, curve_array)
    new_shaft.get_Parameter(BuiltInParameter.WALL_BASE_OFFSET).Set(base_elevation_offset)
    new_shaft.get_Parameter(BuiltInParameter.WALL_TOP_OFFSET).Set(top_elevation_offset)
    new_shafts.append(new_shaft)

  doc.Regenerate()
  ## Add shaft lines
  for plan in plan_views:
    floors = Collection().add_floors(doc, plan).to_list()
    shafts = Collection.get_shafts(doc, plan)
    for shaft in shafts:
      if floor_utils.does_shaft_intersect_floors(doc, shaft, floors):
        curve_array = shaft.BoundaryCurves
        all_lines = [l for l in curve_array]
        boundary_pts = geometry.get_points_from_lines(all_lines)
        corner_pts = geometry.get_corner_points(boundary_pts)
        tl_pt = corner_pts['tl']
        tr_pt = corner_pts['tr']
        bl_pt = corner_pts['bl']
        br_pt = corner_pts['br']

        opening_line1 = Line.CreateBound(tl_pt, br_pt)
        opening_det_line1 = doc.Create.NewDetailCurve(plan, opening_line1)
        opening_line2 = Line.CreateBound(tr_pt, bl_pt)
        opening_det_line2 = doc.Create.NewDetailCurve(plan, opening_line2)
        opening_det_line1.LineStyle = graphic_style
        opening_det_line2.LineStyle = graphic_style

