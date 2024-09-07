from Autodesk.Revit.DB import *
from pyrevit import revit, forms, script

## FUNCTIONS ###
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
active_view = uidoc.ActiveView

### VARIABLES ###
titleblock_name = "Arcturis Standard"
master_sticker_family_path = r'C:\Users\Jon.R.Ryea\OneDrive - IMEG Corp\Desktop\08 Parametric Engineering Project\Phase 1 - Meramec FS+EC\Revit\Families\IMEG_Master Sticker.rfa'

print(master_sticker_family_path)

### COLLECTORS ###
titleblock_collector = FilteredElementCollector(doc)\
                       .OfCategory(BuiltInCategory.OST_TitleBlocks)\
                       .WhereElementIsNotElementType()

titleblock_list = list(titleblock_collector)

titleblock = [tb for tb in titleblock_list\
              if Element.Name.GetValue(tb)\
              == titleblock_name][0]

titleblock_family = doc.GetElement(titleblock.GetTypeId()).Family


tb_doc = doc.EditFamily(titleblock_family)

print(Family.CanLoadFamilies(tb_doc))
print(tb_doc.LoadFamily(master_sticker_family_path))

# with revit.Transaction('Open Titleblock Family'):
# doc.Regenerate()
# with revit.Transaction('Insert Master Sticker'):
  
  ## Only loads family if family isn't already loaded
  # print(doc.LoadFamily(master_sticker_family_path))
  # print(master_sticker_family)
