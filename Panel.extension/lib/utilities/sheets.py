import math
from Autodesk.Revit.DB import *
from utilities.collection import Collection
from utilities import stopwatch, geometry

## SHEETS ##
def add_views_to_sheet(doc, view_list, sheet):
  base_pt = XYZ(0,0,0)
  viewports_created = []
  for view in view_list:
    vp = None
    if type(view) == ViewSchedule:
      vp = ScheduleSheetInstance.Create(doc, sheet.Id, view.Id, base_pt )
    else:
      vp = Viewport.Create(doc, sheet.Id, view.Id, base_pt)
    if vp:
      viewports_created.append(vp)
  return viewports_created

## VIEWPORTS ##
def get_largest_viewport(viewport_list):
  largest_viewport = viewport_list[0]
  max_area = 0
  for vp in viewport_list:
    min_pt = XYZ(0,0,0)
    max_pt = XYZ(0,0,0)
    if type(vp) == ScheduleSheetInstance:
      min_pt = vp.get_BoundingBox().Min
      max_pt = vp.get_BoundingBox().Max
    else:
      outline = vp.GetBoxOutline()
      min_pt = outline.MinimumPoint
      max_pt = outline.MaximumPoint
    length = abs(max_pt.X - min_pt.X)
    height = abs(max_pt.Y - min_pt.Y)
    area = length * height
    if area >= max_area:
      max_area = area
      largest_viewport = vp
  return largest_viewport

def get_max_height_viewport(view, viewport_list):
  max_height_vp = viewport_list[0]
  max_vp_height = get_viewport_dimensions(view, max_height_vp)['height']
  for vp in viewport_list:
    vp_height = get_viewport_dimensions(view, vp)['height']
    if vp_height > max_vp_height:
      max_height_vp = vp
      max_vp_height = vp_height
  return max_height_vp

def get_max_height_viewports(view, viewport_list, num):
  current_vps = viewport_list[:]
  max_height_vps = []
  for x in range(num):
    max_height_vp = get_max_height_viewport(view, current_vps)
    max_height_vps.append(max_height_vp)
    vp_index = current_vps.index(max_height_vp)
    current_vps.pop(vp_index)
  return max_height_vps

def get_max_width_viewport(view, viewport_list):
  max_width_vp = viewport_list[0]
  max_vp_width = get_viewport_dimensions(view, max_width_vp)['width']
  for vp in viewport_list:
    vp_width = get_viewport_dimensions(view, vp)['width']
    if vp_width > max_vp_width:
      max_width_vp = vp
      max_vp_width = vp_width
  return max_width_vp

def get_viewport_dimensions(view, viewport):
  vp_min = None
  vp_max = None
  if type(viewport) == ScheduleSheetInstance:
    print(viewport)
    vp_bb = viewport.get_BoundingBox(view)
    print(vp_bb)
    vp_min = viewport.get_BoundingBox(view).Min
    vp_max = viewport.get_BoundingBox(view).Max
    width = vp_max.X - vp_min.X
    height = vp_max.Y - vp_min.Y
  else:
    vp_min = viewport.GetBoxOutline().MinimumPoint
    vp_max = viewport.GetBoxOutline().MaximumPoint
    width = vp_max.X - vp_min.X
    height = vp_max.Y - vp_min.Y
  return {"width": width, "height": height}

def get_sum_of_vp_heights(viewports, sheet):
  total_sum = 0
  for vp in viewports:
    total_sum += get_viewport_dimensions(sheet, vp)['height']
  return total_sum

def get_sum_of_vp_widths(viewports, sheet):
  total_sum = 0
  for vp in viewports:
    total_sum += get_viewport_dimensions(sheet, vp)['width']
  return total_sum

def move_viewport_to_pt(view, viewport, location_pt, offset_location):
  vp_height = get_viewport_dimensions(view, viewport)['height']
  vp_width = get_viewport_dimensions(view, viewport)['width']
  if offset_location == 'bl':
    offset_pt_x = location_pt.X + (vp_width/2)
    offset_pt_y = location_pt.Y + (vp_height/2)
  offset_pt = XYZ(offset_pt_x, offset_pt_y, 0)
  viewport.SetBoxCenter(offset_pt)

def get_num_of_vps_in_row(view, viewports, area_width, h_margin, start_index):
  i = start_index
  count = 0
  total_width = h_margin
  while total_width < area_width\
    and i < (len(viewports)) - 1:
    vp_width = get_viewport_dimensions(view, viewports[i])['width']
    total_width += vp_width + h_margin
    i += 1
    count +=1
  return count

def set_elevations_on_sheet(doc, elevations, sheet, h_margin, v_margin):
  print('Scale is good, placing on sheets...')

def is_area_for_viewports(sheet, viewports, tb_area, h_margin, v_margin):
  ## Assumption that most views are a similiar width

  tb_height = tb_area['max_pt'].Y - tb_area['min_pt'].Y
  tb_width = tb_area['max_pt'].X - tb_area['min_pt'].X
  num_of_viewports = len(viewports)

  total_vps_width = get_sum_of_vp_widths(viewports, sheet)

  rows = int(math.ceil(total_vps_width + (h_margin * (num_of_viewports + 1)) / tb_width))

  if rows > num_of_viewports:
    return False

  max_height_vps = get_max_height_viewports(sheet, viewports, rows)
  max_vps_height = get_sum_of_vp_heights(max_height_vps, sheet)

  if (max_vps_height + (v_margin * (rows+1))) < tb_height:
    return True
  else:
    return False

## TITLEBLOCKS ##
def get_most_used_titleblock(doc):
  tb_family = None
  all_titleblocks = Collection.get_titleblocks(doc)
  titleblock_names = [Element.Name.GetValue(tb.Symbol.Family) for tb in all_titleblocks]
  titleblock_dict = {}

  ## Create dictionary - key = family names, values = count
  for tb in all_titleblocks:
    family_name = Element.Name.GetValue(tb.Symbol.Family)
    family_count = titleblock_names.count(family_name)
    titleblock_dict.update({family_name: family_count})
  most_used_tb_family_name = None
  highest_tb_count = 0

  # Get family name w/ highest count
  for key, value in titleblock_dict.items():
    if value > highest_tb_count:
      highest_tb_count = value
      most_used_tb_family_name = key
  titleblock_type_names = ([Element.Name.GetValue(tb.Symbol)
                            for tb in all_titleblocks if
                            Element.Name.GetValue(tb.Symbol.Family) == most_used_tb_family_name])

  # Create dictionary - key = type names, values = count
  titleblock_dict = {}
  for tb in all_titleblocks:
    tb_name = Element.Name.GetValue(tb.Symbol.Family)
    type_name = Element.Name.GetValue(tb.Symbol)
    if tb_name == most_used_tb_family_name:
      type_count = titleblock_names.count(tb_name)
      titleblock_dict.update({type_name: type_count})

  # Get most used titleblock type
  most_used_tb_type_name = None
  highest_tb_type_count = 0
  for key, value in titleblock_dict.items():
    if value > highest_tb_type_count:
      highest_tb_type_count = value
      most_used_tb_type_name = key

  for tb in all_titleblocks:
    tb_family_name = Element.Name.GetValue(tb.Symbol.Family)
    tb_symbol_name = Element.Name.GetValue(tb.Symbol)
    if ((tb_family_name == most_used_tb_family_name
         and tb_symbol_name == most_used_tb_type_name)):
      return tb

def get_titleblock_working_area(doc, titleblock):

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

  min_y = find_max_dist_between_lines(horiz_lines, 'horiz')['min']
  max_y = find_max_dist_between_lines(horiz_lines, 'horiz')['max']
  min_x = find_max_dist_between_lines(vert_lines, 'vert')['min']
  max_x = find_max_dist_between_lines(vert_lines, 'vert')['max']

  min_sheet_pt = XYZ(min_x, min_y, 0)
  max_sheet_pt = XYZ(max_x, max_y, 0)

  return {'min_pt': min_sheet_pt, 'max_pt':max_sheet_pt}


# Simplified for now
# def calc_rows_needed(sheet_height, sheet_width, viewports, vert_whitespace_percent, horiz_whitespace_percent):
#   row_count = None
#   total_vert_whitespace = sheet_height * vert_whitespace_percent
#   max_height_vps = get_max_height_viewports(viewports, 2)
#   vp_01_height = get_viewport_dimensions(max_height_vps[0])['height']
#   vp_02_height = get_viewport_dimensions(max_height_vps[1])['height']
#   total_vp_height = vp_01_height + vp_02_height + total_vert_whitespace
#   if total_vp_height < sheet_height:
#     if vp_01_height + total_vert_whitespace < sheet_height:
#       row_count = 1
#     else:
#       row_count = 2
#   return row_count