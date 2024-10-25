from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from utilities import datum, geometry
from utilities.collection import Collection

## Functions
# 0-44: Left, right, 45-135:Top, bottom, 136-180: left, right
def create_dim_locs_dict(locs_list):
  dim_locs_dict = {'top': False, 'bottom': False, 'left': False, 'right': False }
  if 'Top' in locs_list:
    dim_locs_dict.update({'top': True})
  if 'Bottom' in locs_list:
    dim_locs_dict.update({'bottom': True})
  if 'Left' in locs_list:
    dim_locs_dict.update({'left': True})
  if 'Right' in locs_list:
    dim_locs_dict.update({'right': True})
  return dim_locs_dict

def create_grid_dimensions(grids, view, offset, dim_axis):
  sorted_grids = sort_grids_by_axis(grids, dim_axis)
  ref_array = ReferenceArray()
  for grid in grids:
    ref_array.Append(Reference(grid))
  start_grid = grids[0]
  end_grid = grids[1]
  grid_direction = start_grid.Curve.Direction
  start_pt = grids[0].Curve.GetEndPoint(1)
  line_start_pt = start_pt.Add(grid_direction.Multiply(-offset))
  end_pt = grids[1].Curve.GetEndPoint(1)
  line_end_pt = end_pt.Add(grid_direction.Multiply(-offset))
  grid_line = Line.CreateBound(line_start_pt, line_end_pt)
  doc.Create.NewDimension(view, grid_line, ref_array)

def sort_grids_by_axis(grids, axis = 'X'):
  # Returns list
  sorted_grids = grids
  def sort_x(grid):
    return grid.Curve.GetEndPoint(0).X
  def sort_y(grid):
    return grid.Curve.GetEndPoint(0).Y
  if axis == 'X':
    sorted_grids.sort(key=sort_x)
  if axis == 'Y':
    sorted_grids.sort(key=sort_y)
  return sorted_grids

def get_min_or_max_grid(vector, grids, min_or_max = 'min'):
  if abs(vector.X) > abs(vector.Y):
    grids_sorted = sort_grids_by_axis(grids, 'Y')
  else:
    grids_sorted = sort_grids_by_axis(grids, 'X')
  if min_or_max == 'min':
    return grids_sorted[0]
  else:
    return grids_sorted[-1]

# Variables
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

# all_grids = Collection.get_grids(doc)

# Get plan views from user
# plan_views = forms.select_views(
#   title='Select views to dimension grids',
#   filterfunc = lambda x: x.ViewType == ViewType.EngineeringPlan
# )
# if (plan_views == None
#   or len(plan_views) == 0):
#   forms.alert("Please select at least one plan view", title='No plan views selected')
#   script.exit()

# Get grid dimension locations from user
# dim_locs_input = forms.SelectFromList.show(
#   ['Top', 'Bottom', 'Left', 'Right'],
#   title = 'Grid Dimension Locations',
#   group_selector_title='Select sides to dimension: ',
#   multiselect = True
# )

# Temporary grid dimension locations
dim_locs_input = ['Top', 'Bottom', 'Right', 'Left']

# Create dict from dimension locations
dim_locs = create_dim_locs_dict(dim_locs_input)

# Start w/ single view, then loop through views later
with revit.Transaction('Create Grids'):


  # 1. Group grids by grid direction
  grids = Collection.get_grids(doc, active_view)

  # Confirm the view has grids
  if len(grids) == 0:
    forms.alert("You can't dimension grids if they don't exist", title='Grids not found')
    script.exit()

  # modify grids to have a consistent direction
  datum.sync_grid_direction(grids, active_view)

  # Creates a nested list of grids by angle + sorts them by position
  grids_sorted_by_angle = datum.sort_grids_by_angle(grids)

  grids_test_group = grids_sorted_by_angle[2]

  # Get one grid to each side
  # def get outer 

  # for grid_list in grids_sorted_by_angle:
  #   grids_sorted_by_pts = datum.sort_grids_by_endpts(grids_test_group , active_view)

  #   grids_sorted_by_startpts = grids_sorted_by_pts['start_pts']
  #   grids_sorted_by_endpts = grids_sorted_by_pts['end_pts']

  # for grids_by_angle in grids_sorted_by_angle:
  #   print('-----------------------------------')
  #   # 2. Create subgroups based on extents of grid ends
  #   grids_sorted_by_pts = datum.sort_grids_by_endpts(grids, active_view)
  #   grids_sorted_by_startpts = grids_sorted_by_pts['start_pts']
  #   grids_sorted_by_endpts = grids_sorted_by_pts['end_pts']
  #   print(datum.get_grid_angle(grids_by_angle[0]))
  #   print('groups of start points: ')
  #   print(len(grids_sorted_by_startpts))
  #   print('groups of start points: ')
  #   print(len(grids_sorted_by_endpts))
  #   print('-----------------------------------')
    # for grid in grids_by_angle:
    #   print(Element.Name.GetValue(grid))


  # for grids in grids_sorted_by_angle:
  #   grid_angle = datum.get_grid_angle(grids[0])
  #   # Get vertical grids
  #   if grid_angle > 45 and grid_angle < 135:
  #     # Check if user wants grid dimensions on top
  #     if dim_locs['top']:
  #       # Sort grids by extents
  #       for grid in grids:
  #         grid_curve = grid_curve = grid.GetCurvesInView(DatumExtentType.ViewSpecific, active_view)[0]
  #         grid_endpt = grid_curve.GetEndPoint(1)
  #         grid_pt_pairs.append((grid, grid_endpt))
  #       grid_pt_pairs.sort(key=lambda t:t[1].Y)

  #       first_coord = grid_pt_pairs[0][1].Y
  #       grid_pt_pairs_subgroup = [grid_pt_pairs[0]]

  #       # print(grid_pt_pairs)
  #       for grid_w_pt in grid_pt_pairs:
  #         # See if coordinate of current grid_pt_pair is equal to last grid_pt pair
  #         # print('Last extents coordinate: ')
  #         # print(grid_pt_pairs_subgroup[-1][1].Y)
  #         # print('Current extents coordinate: ')
  #         # print(grid_w_pt[1].Y)
  #         if round(grid_w_pt[1].Y) == round(grid_pt_pairs_subgroup[-1][1].Y):
  #           # print('grid extents match!!')
  #           grid_pt_pairs_subgroup.append(grid_w_pt)
  #         else:
  #           grid_pt_pairs_grouped.append(grid_pt_pairs_subgroup)
  #           grid_pt_pairs_subgroup = [grid_w_pt]
  #       # Append last subgroup
  #       grid_pt_pairs_grouped.append(grid_pt_pairs_subgroup)

  #       for grid_pt_subgroup in grid_pt_pairs_grouped:
  #         # grid_line.y = grid_pt_pairs[0][1].Y
  #         # grid_line_start_pt = grid_w_pt[0][1]
  #         # grid_line_end_pt = grid_w_pt[-1][1]
  #         # grid_line_end_pt = XYZ(grid_line_end_pt.X, grid_line_start_pt.Y, grid_line_end_pt.Z)
  #         for grid_pt in grid_pt_subgroup:
  #           print(Element.Name.GetValue(grid_pt[0]))
          # print(grid_w_pt)
          # print(grid_w_pt[0])
          # print(grid_w_pt[1])
          # grid_line = Line.CreateBound(grid_line_start_pt, grid_line_end_pt)
          # overall_grid_ref = 

        # print(top_grid_pts.Y)
      # if dim_locs['bottom']:


  # 3. Dimension from higher to lower
  # 4. Offset dimension strings: 3/8" x View Scale

#   grids_horiz = [grid for grid in grids_list if grid.Curve.Direction\
#                     .IsAlmostEqualTo(grid.Curve.Direction.BasisX) or\
#                       grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisX))]
#   grids_vert = [grid for grid in grids_list if grid.Curve.Direction\
#                     .IsAlmostEqualTo(grid.Curve.Direction.BasisY) or\
#                       grid.Curve.Direction.IsAlmostEqualTo(-(grid.Curve.Direction.BasisY))]
#   sorted_grids_horiz = sort_grids_by_axis(grids_horiz, axis = 'Y')
#   sorted_grids_vert = sort_grids_by_axis(grids_vert, axis = 'X')

#   overall_horiz = [sorted_grids_horiz[0], sorted_grids_horiz[-1]]
#   overall_vert = [sorted_grids_vert[0], sorted_grids_vert[-1]]

#   for plan in plan_views:
#     overall_grid_dims_X = create_grid_dimensions(overall_vert, plan, 2, 'X')
#     overall_grid_dims_Y = create_grid_dimensions(overall_horiz, plan, 2, 'Y')
#     grid_dims_X = create_grid_dimensions(grids_vert, plan, 6, 'X')
#     grid_dims_Y = create_grid_dimensions(grids_horiz, plan, 6, 'Y')















