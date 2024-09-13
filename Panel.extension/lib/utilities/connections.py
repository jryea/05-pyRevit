from Autodesk.Revit.DB import *
from utilities import column as col
from utilities import framing as fr

def create_bb_from_pt(pt, size):
  ptx = pt.X
  pty = pt.Y
  ptz = pt.Z
  bb_min = XYZ(ptx - (size/2), pty - (size/2), ptz - (size/2))
  bb_max = XYZ(ptx + (size/2), pty + (size/2), ptz + (size/2))

  bb = BoundingBoxXYZ()
  bb.Min = bb_min
  bb.Max = bb_max
  return bb

def is_pt_within_bb(bb, point):
  bb_min = bb.Min
  bb_max = bb.Max

  bb_min_x = bb_min.X
  bb_min_y = bb_min.Y
  bb_min_z = bb_min.Z

  bb_max_x = bb_max.X
  bb_max_y = bb_max.Y
  bb_max_z = bb_max.Z

  pt_x = point.X
  pt_y = point.Y
  pt_z = point.Z

  if ((pt_x > bb_min_x and pt_x < bb_max_x)
  and (pt_y > bb_min_y and pt_y < bb_max_y)
  and (pt_z > bb_min_z and pt_z < bb_max_z)):
    return True

  return False

def beam2_to_column(doc, beams, column, location):
  connection_box_size = 1.0
  col_top_pt = col.get_column_endpts(doc,column)[location]
  beam_endpts = []
  beam_endpts_in_bb = 0
  beam_direction = beams[0].HandOrientation
  for beam in beams:
    beam_endpts.extend(fr.get_framing_endpoints(beam))
  bb = create_bb_from_pt(col_top_pt, connection_box_size)
  for endpt in beam_endpts:
    if is_pt_within_bb(bb, endpt):
      beam_endpts_in_bb += 1
  if beam_endpts_in_bb >= 2:
    return (True, beam_direction)
