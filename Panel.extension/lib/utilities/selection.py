from Autodesk.Revit.DB import *
from utilities import selection as sel
from System.Collections.Generic import List

def return_selection(uidoc, elements):
  element_ids = [elem.Id for elem in elements]
  element_ids_ilist = List[ElementId](element_ids)
  uidoc.Selection.SetElementIds(element_ids_ilist)