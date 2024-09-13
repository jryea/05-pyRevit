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
tag_offset = 1 # use view scale to alter this value

### COLLECTING TAGS ###
framing_tag_collector = FilteredElementCollector(doc)\
                        .OfCategory(BuiltInCategory.OST_StructuralFramingTags)\
                        .WhereElementIsElementType()
plan_view_collector = FilteredElementCollector(doc)\
                     .OfClass(ViewPlan)\
                     .WhereElementIsNotElementType()

framing_tag_types = list(framing_tag_collector)

beam_tag = [tag for tag in framing_tag_types\
            if Element.Name.GetValue(tag) == beam_tag_type_name\
            and tag.FamilyName == beam_tag_family_name][0]

beam_collector = FilteredElementCollector(doc)\
                .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()

beams_all = list(beam_collector)
beams_culled = [beam for beam in beams_all if type(beam) != DirectShape]
beams = [beam for beam in beams_culled if beam.StructuralType\
         != Structure.StructuralType.Brace]

structural_plans = list(plan_view_collector)
placed_plans = []

for plan in structural_plans:
  if plan.GetPlacementOnSheetStatus() == ViewPlacementOnSheetStatus.CompletelyPlaced:
    placed_plans.append(plan)
  else:
    continue

with revit.Transaction('Create Beams and Joists'):

  if beam_tag.IsActive == False:
      beam_tag.Activate()
  doc.Regenerate()

  for current_plan in placed_plans:
    for beam in beams:
      line = beam.Location.Curve
      midpoint = line.Evaluate(0.5, True)
      perp_vector = get_perp_vector(line.Direction)
      point = midpoint.Add(perp_vector.Multiply(tag_offset))
      tag = IndependentTag.Create(doc, beam_tag.Id, current_plan.Id, Reference(beam), False, TagOrientation.AnyModelDirection, point)