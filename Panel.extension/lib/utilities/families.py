from Autodesk.Revit.DB import *
from utilities.collection import Collection

# family_path = r`C:\temp\Test Family.rfa
## is family loaded - if not, load it
def is_family_loaded(doc, family_name):
  doc_families = Collection.get_families(doc)
  doc_family_names = [Element.Name.GetValue(family) for family in doc_families]
  if family_name in doc_family_names:
    return True
  else:
    return False

def load_family(doc, family_name, family_path):
  if doc.LoadFamily(family_path):
    print('Loaded Family: ' + family_name)
  else:
    print('Could not load family!')

def load_family_symbol(doc, family_path, family_symbol_name):
  print(family_path)
  print(family_symbol_name)
  doc.LoadFamilySymbol(family_path, family_symbol_name)
  # if doc.LoadFamilySymbol(family_path, family_symbol_name):
  #   print('Loaded Family Type: ' + family_symbol_name)
  # else:
  #   print('Could not find family type!')

def does_family_symbol_exist(doc, family, family_symbol_name):
  family_symbols = Collection.get_family_symbols_from_family(doc, family)
  for symbol in family_symbols:
    if Element.Name.GetValue(symbol).lower() == family_symbol_name.lower():
      return True
  return False

def create_family_symbol(doc, family, family_symbol_name):
  family_symbols = Collection.get_family_symbols_from_family(doc, family)
  family_symbol = family_symbols[0]
  new_family_symbol = family_symbol.Duplicate(family_symbol_name)
  print('Created family symbol ' + family_symbol_name)
  return new_family_symbol

#does family have symbol - if not, create it
#insert family