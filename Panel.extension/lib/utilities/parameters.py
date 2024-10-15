from Autodesk.Revit.DB import *
from utilities.collection import Collection

def set_double_parameter_value(family_symbol, param_name, value):
  for param in family_symbol.Parameters:
    if Element.Name.GetValue(param) == param_name:
      param.Set(value)