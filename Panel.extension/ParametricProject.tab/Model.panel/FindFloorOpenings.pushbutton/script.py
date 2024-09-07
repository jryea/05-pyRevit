import json
from Autodesk.Revit.DB import *
from pyrevit import revit
from System.Collections.Generic import List

### HOLD OFF ON THIS UNTIL I KNOW HOW WE'RE IMPORTING FROM GRASSHOPPER

uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = doc.ActiveView

floor_collector = FilteredElementCollector(doc)\
            .OfCategory(BuiltInCategory.OST_Floors)\
            .WhereElementIsNotElementType()

floor_list = list(floor_collector)
floors_curve_list = []

for floor in floor_list:
  floor_curves = []
  curve_ar_array = doc.GetElement(floor.SketchId).Profile
  for curve_array in curve_ar_array:
      for curve in curve_array:
        floor_curves.append(curve)
  floors_curve_list.append(floor_curves)

print('Floors: ')
print (len(floor_list))

print('Floor curve list: ')
print (len(floors_curve_list))


curve_loop_list = []
extra_curves = []


for floor_curves in floors_curve_list:
  curve_loop = CurveLoop()
  for curve in floor_curves:
    curve_loop.Append(curve)
    # try:
    #   curve_loop.Append(curve)
    #   print(curve)
    # except Exception:
    #   extra_curves.append(curve)
  curve_loop_list.append(curve_loop)

print('Curve Loop list: ')
print(len(curve_loop_list))

## VARIABLES
# curve_loop_list = [curve_loop]
# floor_type_id = Floor.GetDefaultFloorType(doc, False)
# floor_level_id = floor_list[0].LevelId

## Floors just for testing curve loops
# with revit.Transaction('Find Floor Openings'):
  
#   new_floor = Floor.Create(doc, curve_loop_list, floor_type_id, floor_level_id)
  
#   print(new_floor)