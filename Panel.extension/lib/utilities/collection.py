from Autodesk.Revit.DB import *
from pyrevit import forms

class Collection:
  def __init__(self):
    self._list = []
  def __len__(self):
    return len(self._list)

  def first():
    return self._list[0]

  def to_list(self):
    return self._list

  def length(self):
    return len(self._list)

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

    self._list.extend(self.elem_list)
    return self

  def add_floors(self, doc, view = None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_Floors)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    self._list.extend(elem_list)
    return self

  @staticmethod
  def get_floor_types(doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(FloorType)
    return list(collector)

  @staticmethod
  def get_floor_type_if_name_contains(floor_type_list, include_name, include_name2=None, exclude_name=None):
    for floor_type in floor_type_list:
      floor_type_name = Element.Name.GetValue(floor_type)
      if include_name2 and exclude_name:
        if include_name.lower() in floor_type_name.lower()\
        and include_name2.lower() in floor_type_name.lower()\
        and exclude_name.lower() not in floor_type_name.lower():
          return floor_type
      elif include_name2:
        if include_name.lower() in floor_type_name.lower()\
        and include_name2.lower() in floor_type_name.lower():
          return floor_type
      elif exclude_name:
        if include_name.lower() in floor_type_name.lower()\
        and exclude_name.lower() not in floor_type_name.lower():
          return floor_type

  def add_beams(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    elem_list = [elem for elem in elem_list if elem.StructuralType == Structure.StructuralType.Beam and type]
    self._list.extend(elem_list)
    return self

  def add_braces(self, doc, view=None):
    self.collector = self._create_collector(doc, view)
    self.collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    self.elem_list = list(self.collector)
    self.elem_list = [elem for elem in self.elem_list if type(elem) == FamilyInstance]
    self.elem_list = [elem for elem in self.elem_list if elem.StructuralType == Structure.StructuralType.Brace]
    self._list.extend(self.elem_list)
    return self

  def add_foundations(self, doc, view=None):
    self.collector = self._create_collector(doc, view)
    self.collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    self.elem_list = list(self.collector)
    self._list.extend(self.elem_list)
    return self

  def add_framing(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFraming)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    self._list.extend(elem_list)
    return self

  def add_spread_footings(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == FamilyInstance]
    self._list.extend(elem_list)
    return self

  def add_cont_footings(self, doc, view=None):
    collector = self._create_collector(doc, view)
    collector.OfCategory(BuiltInCategory.OST_StructuralFoundation)\
                .WhereElementIsNotElementType()
    elem_list = list(collector)
    elem_list = [elem for elem in elem_list if type(elem) == WallFoundation]
    self._list.extend(elem_list)
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
    elif 'floor' in tag_family.lower():
      built_in_cat = BuiltInCategory.OST_FloorTags
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
  def get_plan_views(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Views)
    collector.WhereElementIsNotElementType()
    elem_list = [elem for elem in collector if elem.ViewType == ViewType.EngineeringPlan]
    return elem_list

  @staticmethod
  def get_drafting_views(doc):
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
      if Element.Name.GetValue(elem) == text_note_type_name:
        return elem.Symbol
    forms.alert('Text note type not found')

  @staticmethod
  def get_scope_boxes(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_VolumeOfInterest)
    return list(collector)

  ##Reduce filter by materials if possible
  def filter_columns_by_material(self, material_key):
    if material_key == 'st':
      for elem in self._list[:]:
        if elem.StructuralType == Structure.StructuralType.Column:
          if elem.StructuralMaterialType != Structure.StructuralMaterialType.Steel:
            self._list.remove(elem)
    else:
      pass
    return self

  @staticmethod
  def get_columns_from_elements(element_list):
    column_list = []
    for elem in element_list:
      if type(elem) == FamilyInstance:
        if elem.StructuralType:
          if elem.StructuralType == Structure.StructuralType.Column:
            column_list.append(elem)
    return column_list

  def filter_beams_by_material(self, material_key):
    if material_key == 'st':
      for elem in self._list[:]:
        if elem.StructuralType == Structure.StructuralType.Beam:
          if elem.StructuralMaterialType != Structure.StructuralMaterialType.Steel:
            self._list.remove(elem)
    else:
      pass
    return self

  @staticmethod
  def get_beams_from_elements(element_list):
    beam_list = []
    for elem in element_list:
      if type(elem) == FamilyInstance:
        if elem.StructuralType:
          if elem.StructuralType == Structure.StructuralType.Beam:
            beam_list.append(elem)
    return beam_list

  @staticmethod
  def get_spread_footings_from_elements(element_list):
    spread_footings = []
    for elem in element_list:
      if type(elem) == FamilyInstance:
        if elem.StructuralType:
          if elem.StructuralType == Structure.StructuralType.Footing:
            spread_footings.append(elem)
    return spread_footings

  def filter_floors_by_material(self, material_key):
    if material_key == 'co':
      for elem in self._list[:]:
        if type(elem) == Floor:
          floor_type_name = Element.Name.GetValue(elem.FloorType)
          if 'concrete' not in floor_type_name.lower():
            self._list.remove(elem)
    else:
      pass
    return self

  def filter_beams_by_type(self, family_key):
    fam_name = "K-Series Bar Joist-Angle Web"
    if family_key == 'ks':
      for elem in self._list[:]:
        if elem.StructuralType == Structure.StructuralType.Beam:
          if elem.Symbol.FamilyName != fam_name:
            self._list.remove(elem)
    return self._list

###################### OPENINGS #####################

  @staticmethod
  def get_shafts(doc, view=None):
    if view:
      collector = FilteredElementCollector(doc, view.Id)
    else:
      collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_ShaftOpening)
    collector.WhereElementIsNotElementType()
    return list(collector)

  #################### DOCUMENTS ######################

  @staticmethod
  def get_linked_docs(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_RvtLinks)
    collector.WhereElementIsNotElementType()
    return list(collector)

  ############## DATUM ELEMENTS ############

  @staticmethod
  def get_levels(doc):
    collector = FilteredElementCollector(doc)
    collector.OfCategory(BuiltInCategory.OST_Levels)
    collector.WhereElementIsNotElementType()
    return list(collector)
  
  @staticmethod
  def get_grids(doc, view=None):
    if view:
      collector = (FilteredElementCollector(doc, view.Id)
                 .OfCategory(BuiltInCategory.OST_Grids)
                 .WhereElementIsNotElementType())
      return list(collector)
    else:
      collector = (FilteredElementCollector(doc)
                  .OfCategory(BuiltInCategory.OST_Grids)
                  .WhereElementIsNotElementType())
      return list(collector)


  ############## LINES ############

  @staticmethod
  def get_detail_lines(doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(CurveElement)
    return list(collector)

  @staticmethod
  def get_graphic_styles(doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(GraphicsStyle)
    return list(collector)

  ############## FAMILIES AND SYMBOLS ############
  @staticmethod
  def get_families(doc):
    collector = FilteredElementCollector(doc)
    collector.OfClass(Family)
    return list(collector)

  @staticmethod
  def get_family_by_name(doc, family_name):
    doc_families = Collection.get_families(doc)
    for family in doc_families:
      if Element.Name.GetValue(family) == family_name:
        return family
    print(family_name + ' Family not found')
    return None

  @staticmethod
  def get_family_symbols_from_family(doc, family):
    return_list = []
    symbol_ids_list = family.GetFamilySymbolIds()
    for symbol_id in symbol_ids_list:
      return_list.append(doc.GetElement(symbol_id))
    return return_list

  @staticmethod
  def get_family_symbol_by_name(doc, family, symbol_name):
    family_symbols = get_family_symbols_from_family(doc, family)
    for symbol in family_symbols:
      if Element.Name.GetValue(symbol).lower() == symbol_name.lower():
        return symbol


