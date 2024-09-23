import math
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from pyrevit import revit, forms, script
from utilities import geometry, sheets, views
from utilities.collection import Collection

### VARIABLES ###
viewport_type_name = "IMEG_No View Title"
framing_sheet_name = "STEEL BUILDING CROSS-SECTIONS / FRAME ELEVATIONS"
framing_template_name = 'S - Framing Elevation (document)'
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

framing_sheet = Collection.get_sheet_by_name(doc, framing_sheet_name)
framing_views = Collection.get_views_by_template_name(doc, framing_template_name)

titleblock = sheets.get_most_used_titleblock(doc)
tb_working_area = sheets.get_titleblock_working_area(doc, titleblock)
tb_min_pt = tb_working_area['min_pt']
tb_max_pt = tb_working_area['max_pt']

tb_width = tb_max_pt.X - tb_min_pt.X
tb_height = tb_max_pt.Y - tb_min_pt.Y

h_margin = 0.1
v_margin = 0.1

with revit.Transaction('Put Elevations on Sheet'):
  ## View scales = 32,48,64
  # viewports = sheets.add_views_to_sheet(doc, framing_views, framing_sheet)
  # num_of_viewports = (len(viewports))

  #Set initial view scale
  ## Set back to 32 when ready to test scale adjustment
  view_scale = 64
  for view in framing_views:
    view.Scale = view_scale

  viewports = sheets.add_views_to_sheet(doc, framing_views, framing_sheet)

  # Get viewport scale
  # max_loop = 0
  # is_area = False
  # while is_area == False and max_loop < 8:
  #   is_area = sheets.is_area_for_viewports(framing_sheet, viewports,
  #         tb_working_area, h_margin, v_margin)
  #   max_loop += 1
  #   view_scale += 16
  #   for view in framing_views:
  #     view.Scale = view_scale
  #   for vp in viewports:
  #     framing_sheet.DeleteViewport(vp)

  ## Assuming viewport widths are similiar
  ## PLACE VIEWPORTS ON SHEET
  row_start_index = 0
  num_of_row_vps = sheets.get_num_of_vps_in_row(framing_sheet, viewports, tb_width, h_margin, row_start_index)
  row_end_index = num_of_row_vps - 1
  row_vps = viewports[row_start_index : row_end_index]
  max_height_vp = sheets.get_max_height_viewport(framing_sheet, row_vps)
  vp_max_height = sheets.get_viewport_dimensions(framing_sheet, max_height_vp)['height']
  last_vp_index = len(viewports) - 1
  anchor_pt_x = tb_min_pt.X + h_margin
  anchor_pt_y = tb_max_pt.Y - (vp_max_height + v_margin)
  anchor_pt = XYZ(anchor_pt_x, anchor_pt_y, 0)
  
  # for vp in row_vps:
  #   sheets.move_viewport_to_pt(framing_sheet, vp, anchor_pt, 'bl')
  #   vp_width = sheets.get_viewport_dimensions(framing_sheet, vp)['width']
  #   anchor_pt = anchor_pt.Add(XYZ().BasisX.Multiply(vp_width + h_margin))
  
  i = 0
  while i < last_vp_index:
    # print('row start index:')
    # print(row_start_index)
    # print('row end index:')
    # print(row_end_index)
    for vp in row_vps:
      sheets.move_viewport_to_pt(framing_sheet, vp, anchor_pt, 'bl')
      vp_width = sheets.get_viewport_dimensions(framing_sheet, vp)['width']
      anchor_pt = anchor_pt.Add(XYZ().BasisX.Multiply(vp_width + h_margin))
      i = i+1
    row_start_index = row_end_index
    num_of_row_vps = sheets.get_num_of_vps_in_row(framing_sheet, viewports, tb_width, h_margin, row_start_index)
    if num_of_row_vps == 0:
      break
    row_end_index = row_end_index + (1 + num_of_row_vps)
    # if row_end_index == last_vp_index:
    #   row_end_index = last_vp_index
    row_vps = viewports[row_start_index : row_end_index]
    max_height_vp = sheets.get_max_height_viewport(framing_sheet, row_vps)
    vp_max_height = sheets.get_viewport_dimensions(framing_sheet, max_height_vp)['height']
    anchor_pt_x = tb_min_pt.X + h_margin
    anchor_pt_y = anchor_pt.Y - (vp_max_height + v_margin)
    anchor_pt = XYZ(anchor_pt_x, anchor_pt_y, 0)


  # print(str(num_of_viewports) + ' framing elevations placed on sheet')
      # sheets.set_elevations_on_sheet(doc, viewports, framing_sheet, h_margin, v_margin)











