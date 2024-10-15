from Autodesk.Revit.DB import *

def create_ref_section(doc, view, ref_view, pt, direction):
  sec_length = 5.0
  sec_offset = 3
  if direction.IsAlmostEqualTo(XYZ().BasisX)\
  or direction.IsAlmostEqualTo(-(XYZ().BasisX)):
    section_marker_pt = pt.Add(XYZ(0, sec_offset, 0))
    head_pt = section_marker_pt.Add(XYZ(-(sec_length/2), 0, 0))
    tail_pt = section_marker_pt.Add(XYZ((sec_length/2), 0, 0))
  else:
    section_marker_pt = pt.Add(XYZ(sec_offset, 0, 0))
    head_pt = section_marker_pt.Add(XYZ(0, -(sec_length/2), 0))
    tail_pt = section_marker_pt.Add(XYZ(0, (sec_length/2), 0))
  ViewSection.CreateReferenceSection(doc, view.Id, ref_view.Id, head_pt, tail_pt)
