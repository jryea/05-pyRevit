from Autodesk.Revit.DB import *
from classes.detail import Detail
from classes.members import *
from data import data

detail1 = Detail('2200-03')
detail2 = Detail('2200-04')

view_members = detail1.get_view_detail_members('structural')

# member = Member('co_st')
# column_member = ColumnMember('co_st')

print(view_members)
# print(column_member)