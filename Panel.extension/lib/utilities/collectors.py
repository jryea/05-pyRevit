from Autodesk.Revit.DB import *
from pyrevit import forms

class Collection:
  def __init__(self, list = []):
    try:
      self.list = list
    except TypeError:
      forms.alert('Collection needs a list')

  def get_columns(self, document = None, view = None):

    if document:
      self.document = document
    else:
      self.document = doc

    self.view = view

    if self.view:
      column_collector = FilteredElementCollector(self.document, self.view.Id)
    else:
      column_collector = FilteredElementCollector(self.document)

    column_collector.OfCategory(BuiltInCategory.OST_StructuralColumns)\
                      .WhereElementIsNotElementType()
    columns_list = list(column_collector)
    self.list.extend(columns_list)
    return self.list

  def get_floors(self, doc, view = None):
    floor_collector = FilteredElementCollector(doc, view.Id)\
                .OfCategory(BuiltInCategory.OST_Floors)\
                .WhereElementIsNotElementType()
    floor_list = list(floor_collector)
    self.list.extend(floor_list)
    return self.list

  def get_beams(self, doc, view):
    framing_collector = FilteredElementCollector(doc, view.Id)\
                .OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    framing_list = list(framing_collector)
    beam_list = [framing for framing in framing_list if framing.StructuralType == Structure.StructuralType.Beam]
    return beam_list

  def get_foundations(self, doc, view):
    foundation_collector = FilteredElementCollector(doc, view.Id)\
                      .OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                      .WhereElementIsNotElementType()
    foundation_list = list(foundation_collector)
    return foundation_list

  def get_spread_footings(self, doc, view):
    foundation_list = collect_foundations(doc, view)
    spread_footing_list = [f for f in foundation_list if type(f) == FamilyInstance]
    return spread_footing_list

  def collect_cont_footings(doc, view):
    foundation_list = collect_foundations(doc, view)
    cont_footing_list = [f for f in foundation_list if type(f) == WallFoundation]
    return cont_footing_list

  ##Reduce filter by materials if possible
  def filter_columns_by_material(columns, material_key):
    column_list = None
    if material_key == 'st':
      column_list = [c for c in columns if c.StructuralMaterialType == Structure.StructuralMaterialType.Steel]
    else:
      pass
    return column_list

  def get_columns_from_elements(element_list):
    column_list = []
    for elem in element_list:
      if type(elem) == FamilyInstance:
        if elem.StructuralType:
          if elem.StructuralType == Structure.StructuralType.Column:
            column_list.append(elem)
    return column_list

  def filter_beams_by_material(beams, material_key):
    beam_list = None
    if material_key == 'st':
      beam_list = [b for b in beams if b.StructuralMaterialType == Structure.StructuralMaterialType.Steel]
    else:
      pass
    return beam_list

  def get_beams_from_elements(element_list):
    beam_list = []
    for elem in element_list:
      if type(elem) == FamilyInstance:
        if elem.StructuralType:
          if elem.StructuralType == Structure.StructuralType.Beam:
            beam_list.append(elem)
    return beam_list

  def filter_floors_by_material(floors, material_key):
    floor_list = None
    if material_key == 'co':
      floor_list  = [f for f in floors if "concrete" in Element.Name.GetValue(f.FloorType).lower()]
    else:
      pass
    return floor_list

  def filter_framing_by_type(framing, family_key):
    fam_name = "K-Series Bar Joist-Angle Web"
    framing_list = None
    if family_key == 'ks':
      framing_list = [f for f in framing if f.Symbol.FamilyName == fam_name]
    return framing_list