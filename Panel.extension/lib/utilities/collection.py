from Autodesk.Revit.DB import *
from pyrevit import forms

class Collection:
  def __init__(self):
    self.list = []

  def first():
    return self.list[0]

  def to_list(self):
    return self.list

  def length(self):
    return len(self.list)

  def _create_collector(self, doc, view):
    if view:
      self.collector = FilteredElementCollector(doc, view.Id)
    else:
      self.collector = FilteredElementCollector(doc)
    return self.collector

  def add_columns(self, doc, view = None):
    self.collector = self._create_collector(doc, view)

    self.collector.OfCategory(BuiltInCategory.OST_StructuralColumns)\
                      .WhereElementIsNotElementType()
    self.elem_list = list(self.collector)

    self.list.extend(self.elem_list)
    return self

  def add_floors(self, doc, view = None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_Floors)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    self.list.extend(elem_list)
    return self

  def add_beams(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    elem_list = [elem for elem in elem_list if elem.StructuralType == Structure.StructuralType.Beam and type]
    self.list.extend(elem_list)
    return self

  def add_braces(self, doc, view=None):
    self.collector = self._create_collector(doc, view)
    self.collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    self.elem_list = list(self.collector)
    self.elem_list = [elem for elem in self.elem_list if type(elem) == FamilyInstance]
    self.elem_list = [elem for elem in self.elem_list if elem.StructuralType == Structure.StructuralType.Brace]
    self.list.extend(self.elem_list)
    return self

  def add_foundations(self, doc, view=None):
    self.collector = self._create_collector(doc, view)
    self.collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    self.elem_list = list(self.collector)
    self.list.extend(self.elem_list)
    return self

  def add_framing(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    self.list.extend(elem_list)
    return self

  def add_spread_footings(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    self.list.extend(elem_list)
    return self

  def add_cont_footings(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == WallFoundation]
    self.list.extend(elem_list)
    return self

  ######################### STATIC METHODS #####################################

  @staticmethod
  def get_tag_type(doc, tag_family, tag_type):
    built_in_cat = None
    if 'framing' in tag_family.lower():
      built_in_cat = BuiltInCategory.OST_StructuralFramingTags
    elif 'column' in tag_family.lower():
      built_in_cat = BuiltInCategory.OST_StructuralColumnTags
    elif 'foundation' in tag_family.lower():
      built_in_cat = BuiltInCategory.OST_StructuralFoundationTags
    collector = FilteredElementCollector(doc)
    collector.OfCategory(built_in_cat).WhereElementIsElementType()
    for tag in collector:
      if Element.Name.GetValue(tag) == tag_type\
      and tag.FamilyName == tag_family:
        return tag
    forms.alert('Tag not found')

  @staticmethod
  def get_view_family_type(doc, vft_name):
    collector = FilteredElementCollector(doc)
    collector.OfClass(ViewFamilyType)
    for vft in collector:
      if Element.Name.GetValue(vft) == vft_name:
        return vft
    forms.alert('View Family Type not found')

  @staticmethod
  def get_sheets(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Sheets)
    collector.WhereElementIsNotElementType()
    return list(collector)
  
  @staticmethod
  def get_sheet_by_name(doc, sheet_name):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Sheets)
    collector.WhereElementIsNotElementType()
    for sheet in collector:
      if Element.Name.GetValue(sheet) == sheet_name:
        return sheet
    forms.alert('Sheet not found')

  @staticmethod
  def get_view_template(doc, template_name):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    for elem in collector:
      if elem.IsTemplate:
        if Element.Name.GetValue(elem) == template_name:
          return elem
    forms.alert('View template not found')

  @staticmethod
  def get_views_by_template_name(doc, template_name):
    return_views = []
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views).WhereElementIsNotElementType()
    for elem in collector:
      view_template = doc.GetElement(elem.ViewTemplateId)
      if Element.Name.GetValue(view_template) == template_name:
        return_views.append(elem)
    if len(return_views) > 0:
      return return_views
    else:
      forms.alert('No views with specified view templates found')

  @staticmethod
  def get_plan_views(doc, view = None):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    collector.WhereElementIsNotElementType()
    elem_list = [elem for elem in collector if elem.ViewType == ViewType.EngineeringPlan]
    return elem_list

  @staticmethod
  def get_drafting_views(doc, view = None):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    collector.WhereElementIsNotElementType()
    elem_list = [elem for elem in collector if elem.ViewType == ViewType.DraftingView]
    return elem_list

  @staticmethod
  def get_schedules(doc, view = None):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Schedules)
    collector.WhereElementIsNotElementType()
    return list(collector)

  @staticmethod
  def get_schedules_by_name(doc, name_list):
    return_list = []
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Schedules)
    collector.WhereElementIsNotElementType()
    for elem in collector:
      elem_name = Element.Name.GetValue(elem)
      for name in name_list:
        if name.lower() == elem_name.lower():
          return_list.append(elem)
    return return_list

  @staticmethod
  def get_legends(doc, view = None):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    collector.WhereElementIsNotElementType()
    elem_list = [elem for elem in collector if elem.ViewType == ViewType.Legend ]
    return elem_list

  @staticmethod
  def get_legends_by_name(doc, name_list):
    return_list = []
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    collector.WhereElementIsNotElementType()
    elem_list = [elem for elem in collector if elem.ViewType == ViewType.Legend]
    for elem in elem_list:
      elem_name = Element.Name.GetValue(elem)
      for name in name_list:
        if name.lower() == elem_name.lower():
          return_list.append(elem)
    return return_list

  @staticmethod
  def get_viewport_type_by_name(doc, name):
    collector = FilteredElementCollector(doc)
    collector.OfClass(ElementType)
    # viewport = list(collector)[0]
    # print(element)
    # viewport_type_ids = viewport.GetValidTypes()
    # viewport_types = [doc.GetElement(elem_id) for elem_id in viewport_type_ids]
    for elem in collector:
      if Element.Name.GetValue(elem) == name:
        return elem
    forms.alert('No viewport types with this name can be found')

  @staticmethod
  def get_titleblocks(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_TitleBlocks)
    collector.WhereElementIsNotElementType()
    # elem_list = [elem for elem in collector if elem.ViewType == ViewType.Legend ]
    return list(collector)

  @staticmethod
  def get_note_type(doc, text_note_type_name):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_TextNotes)
    for elem in collector:
      print(Element.Name.GetValue(elem))
      if Element.Name.GetValue(elem) == text_note_type_name:
        return elem.Symbol
    forms.alert('Text note type not found')

  @staticmethod
  def get_detail_lines(doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(CurveElement)
    return list(collector)
  
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