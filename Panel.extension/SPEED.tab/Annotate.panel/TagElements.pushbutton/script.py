from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script
from utilities.collection import Collection
from utilities import geometry
import time

## FUNCTIONS ###
def get_perp_vector(vector):
  perp_vector = vector.CrossProduct(XYZ(0,0,1))
  return perp_vector

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

### VARIABLES ###
beam_tag_family_name = "IMEG_Structural Framing Tag"
beam_tag_type_name = "Standard"
column_tag_family_name = "IMEG_Structural Column Tag"
column_tag_type_name = "45"
foundation_tag_family_name = "IMEG_Foundation Tag"
foundation_tag_type_name = "Mark Only"
tag_offset = 1 # use view scale to alter this value

column_tag = Collection.get_tag_type(doc, column_tag_family_name, column_tag_type_name)
beam_tag = Collection.get_tag_type(doc, beam_tag_family_name, beam_tag_type_name)
foundation_tag = Collection.get_tag_type(doc, foundation_tag_family_name, foundation_tag_type_name)

columns = Collection().add_columns(doc, active_view).to_list()
foundations = Collection().add_foundations(doc, active_view).to_list()
beams = Collection().add_beams(doc, active_view).to_list()

with revit.Transaction('Tag Elements'):

  if column_tag.IsActive == False:
    column_tag.Activate()
  if foundation_tag.IsActive == False:
    beam_tag.Activate()
  if foundation_tag.IsActive == False:
    foundation_tag.Activate()
  doc.Regenerate()

  for footing in foundations:
    point = None
    # Spread footings
    if type(footing.Location) == LocationPoint:
      midpoint = footing.Location.Point
      size = footing.Symbol.LookupParameter("Spread Footing Length").AsDouble()
      offset_direction = XYZ(0,1,0)
      total_offset = ((size/2) + tag_offset)
      point = midpoint.Add(offset_direction.Multiply((total_offset)))

    # Continuous footings
    else:
      wall_id = footing.WallId
      wall = doc.GetElement(wall_id)
      line = wall.Location.Curve
      midpoint = line.Evaluate(0.5, True)
      perp_vector = get_perp_vector(line.Direction)
      size = footing.get_Parameter(BuiltInParameter.CONTINUOUS_FOOTING_WIDTH).AsDouble()
      total_offset = ((size/2) + tag_offset)
      point = midpoint.Add(perp_vector.Multiply(total_offset))

    tag = IndependentTag.Create(doc, foundation_tag.Id, active_view.Id, Reference(footing), False, TagOrientation.AnyModelDirection, point)

  for column in columns:
    # Logic to deal with levels: element levels are from speckle, view levels are from PSW
    column_base_constraint_param_id = column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).AsElementId()
    column_base_constraint_elevation = doc.GetElement(column_base_constraint_param_id).ProjectElevation
    current_level_elev = active_view.GenLevel.ProjectElevation
    tolerance = 1
    point = column.Location.Point

    if geometry.are_numbers_similiar(column_base_constraint_elevation, current_level_elev, tolerance):
      tag = IndependentTag.Create(doc, column_tag.Id, active_view.Id, Reference(column), False, TagOrientation.AnyModelDirection, point)

  for beam in beams:
    line = beam.Location.Curve
    midpoint = line.Evaluate(0.5, True)
    perp_vector = get_perp_vector(line.Direction)
    point = midpoint.Add(perp_vector.Multiply(tag_offset))
    tag = IndependentTag.Create(doc, beam_tag.Id, active_view.Id, Reference(beam), False, TagOrientation.AnyModelDirection, point)













