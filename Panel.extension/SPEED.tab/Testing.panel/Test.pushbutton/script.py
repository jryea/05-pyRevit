from Autodesk.Revit.DB import *
from pyrevit import revit
from utilities import sheets, geometry, stopwatch
from utilities.collection import Collection



def get_titleblock_working_area(doc):
  
  def filter_lines_by_visibility_param(lines):
  return_lines = []
  for line in lines:
    vis_param = line.get_Parameter(BuiltInParameter.IS_VISIBLE_PARAM)
    if vis_param.UserModifiable == False:
      return_lines.append(line)
  return return_lines

def find_max_dist_between_lines(lines, direction):
  largest_gap = 0
  largest_gap_index = None
  min_coord = None
  max_coord = None
  for i in range(len(lines) - 1):
    cur_line = horiz_lines[i]
    cur_pt = cur_line.GetEndPoint(0)
    next_line = horiz_lines[i+1]
    next_pt = next_line.GetEndPoint(0)
    gap = None
    if direction == 'horiz':
      gap = next_pt.Y - cur_pt.Y
    elif direction == 'vert':
      gap = next_pt.X - cur_pt.X
    else:
      forms.alert('Direction entered is not recognized in the' + find_max_dist_between_lines.__name__ + 'function')
    if gap > largest_gap:
      largest_gap = gap
      largest_gap_index = i
  min_line = lines[largest_gap_index]
  max_line = lines[largest_gap_index + 1]
  min_pt = min_line.GetEndPoint(0)
  max_pt = max_line.GetEndPoint(0)
  if direction == 'horiz':
    min_coord = min_pt.Y
    max_coord = max_pt.Y
  if direction == 'vert':
    min_coord = min_pt.X
    max_coord = max_pt.X
  return {'min': min_coord, 'max': max_coord}
  
  titleblock = sheets.get_most_used_titleblock(doc)

  tb_doc = doc.EditFamily(titleblock.Symbol.Family)
  #Get titleblock lines

  tb_curve_elements = Collection.get_detail_lines(tb_doc)

  ## filter out by visibility parameter (UserModifiable == False)
  tb_curve_elements = filter_lines_by_visibility_param(tb_curve_elements)

  tb_lines = ([elem.GeometryCurve for elem
              in tb_curve_elements
              if type(elem.GeometryCurve) == Line])

  ## Group lines into horizontal and vertical
  horiz_lines = geometry.group_lines_by_xy_direction(tb_lines)['horiz']
  vert_lines = geometry.group_lines_by_xy_direction(tb_lines)['vert']

  ## sort horizontal and vertical lines
  def x_pt_sort(line):
    pt = line.GetEndPoint(0)
    return pt.X
  def y_pt_sort(line):
    pt = line.GetEndPoint(0)
    return pt.Y
  horiz_lines.sort(key=y_pt_sort)
  vert_lines.sort(key=x_pt_sort)

  ## filter out shorter lines
  tb_full_height = (horiz_lines[-1].GetEndPoint(0).Y
                    - horiz_lines[0].GetEndPoint(0).Y)

  tb_full_width =  (vert_lines[-1].GetEndPoint(0).X
                    - vert_lines[0].GetEndPoint(0).X)

  horiz_lines = [line for line in horiz_lines if line.Length > (tb_full_width * 0.8)]

  vert_lines = [line for line in horiz_lines if line.Length > (tb_full_height * 0.8)]

  print(len(horiz_lines))
  print(len(vert_lines))

  min_y = find_max_dist_between_lines(horiz_lines, 'horiz')['min']
  max_y = find_max_dist_between_lines(horiz_lines, 'horiz')['max']
  min_x = find_max_dist_between_lines(vert_lines, 'vert')['min']
  max_x = find_max_dist_between_lines(vert_lines, 'vert')['max']

  min_sheet_pt = XYZ(min_x, min_y, 0)
  max_sheet_pt = XYZ(max_x, max_y, 0)

  return {'min_pt': min_sheet_pt, 'max_pt':max_sheet_pt}





