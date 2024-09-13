from Autodesk.Revit.DB import *

def get_column_endpts(doc, column):
  base_level_param_id = column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).AsElementId()
  top_level_param_id = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).AsElementId()

  base_level_offset = column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).AsDouble()
  top_level_offset = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM).AsDouble()

  base_level = doc.GetElement(base_level_param_id)
  top_level = doc.GetElement(top_level_param_id)

  base_level_elevation = base_level.ProjectElevation
  top_level_elevation = top_level.ProjectElevation

  location_pt = column.Location.Point
  ptx = location_pt.X
  pty = location_pt.Y

  top_ptz = top_level_elevation + top_level_offset
  base_ptz = base_level_elevation + base_level_offset

  top_pt = XYZ(ptx, pty, top_ptz)
  base_pt = XYZ(ptx, pty, base_ptz)

  return {"base": base_pt, "top": top_pt}

