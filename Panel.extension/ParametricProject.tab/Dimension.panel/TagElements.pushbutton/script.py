from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

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

### COLLECTING TAGS ###
framing_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralFramingTags)\
                        .WhereElementIsElementType()
column_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralColumnTags)\
                        .WhereElementIsElementType()
foundation_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralFoundationTags)\
                        .WhereElementIsElementType()
level_collector = FilteredElementCollector(doc)\
                  .OfCategory(BuiltInCategory.OST_Levels)\
                  .WhereElementIsNotElementType()
plan_view_collector = FilteredElementCollector(doc)\
                     .OfClass(ViewPlan)\
                     .WhereElementIsNotElementType()

framing_tag_types = list(framing_tag_collector)
column_tag_types = list(column_tag_collector)
foundation_tag_types = list(foundation_tag_collector)

beam_tag = [tag for tag in framing_tag_types\
            if Element.Name.GetValue(tag) == beam_tag_type_name\
            and tag.FamilyName == beam_tag_family_name][0]

column_tag = [tag for tag in column_tag_types\
             if Element.Name.GetValue(tag) ==  column_tag_type_name\
              and tag.FamilyName == column_tag_family_name][0]

foundation_tag = [tag for tag in foundation_tag_types\
                  if Element.Name.GetValue(tag)\
                  == foundation_tag_type_name\
                  and tag.FamilyName == foundation_tag_family_name][0]

column_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralColumns)\
                .WhereElementIsNotElementType()
beam_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
foundation_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()

columns = list(column_collector)
foundations = list(foundation_collector)
beams_all = list(beam_collector)
beams = [beam for beam in beams_all if beam.StructuralType\
         != Structure.StructuralType.Brace]

levels = list(level_collector)
structural_plans = list(plan_view_collector)
placed_plans = []

for plan in structural_plans:
  if plan.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced:
    placed_plans.append(plan)
  else:
    continue

with revit.Transaction('Create Beams and Joists'):

  if column_tag.IsActive == False:
      beam_symbol.Activate()
  if beam_tag.IsActive == False:
      beam_tag.Activate()
  if foundation_tag.IsActive == False:
      beam_tag.Activate()
  doc.Regenerate()

  for current_plan in placed_plans:

    for beam in beams:
      line = beam.Location.Curve
      midpoint = line.Evaluate(0.5, True)
      perp_vector = get_perp_vector(line.Direction)
      point = midpoint.Add(perp_vector.Multiply(tag_offset))
      tag = IndependentTag.Create(doc, beam_tag.Id, current_plan.Id, Reference(beam), False, TagOrientation.AnyModelDirection, point)

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

      tag = IndependentTag.Create(doc, foundation_tag.Id, current_plan.Id, Reference(footing), False, TagOrientation.AnyModelDirection, point)

    for column in columns:
      column_base_constraint_param_id = column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_PARAM).AsElementId()
      column_base_constraint_elevation = doc.GetElement(column_base_constraint_param_id).ProjectElevation
      column_base_offset_elevation = column.get_Parameter(BuiltInParameter.FAMILY_BASE_LEVEL_OFFSET_PARAM).AsDouble()
      column_base_elevation = column_base_constraint_elevation + column_base_offset_elevation
      closest_level_elevation = current_plan.GenLevel.ProjectElevation
      closest_level = current_plan.GenLevel

      for plan in placed_plans:
        level_elevation = plan.GenLevel.ProjectElevation
        if abs(level_elevation - column_base_elevation) < abs(closest_level_elevation - column_base_elevation):
          closest_level_elevation = level_elevation
          closest_level = plan.GenLevel

      point = column.Location.Point

      if current_plan.GenLevel.Id == closest_level.Id:
        tag = IndependentTag.Create(doc, column_tag.Id, current_plan.Id, Reference(column), False, TagOrientation.AnyModelDirection, point)












