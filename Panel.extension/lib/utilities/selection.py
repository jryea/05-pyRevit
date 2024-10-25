from Autodesk.Revit.DB import *
from System.Collections.Generic import List

def return_selection(uidoc, elements):
  if type(elements) != list:
    elements = [elements]
  element_ids = [elem.Id for elem in elements]
  element_ids_ilist = List[ElementId](element_ids)
  uidoc.Selection.SetElementIds(element_ids_ilist)

def get_selection(doc, uidoc):
  selection_ids = uidoc.Selection.GetElementIds()
  selection = [doc.GetElement(elem_id) for elem_id in selection_ids]
  return selection