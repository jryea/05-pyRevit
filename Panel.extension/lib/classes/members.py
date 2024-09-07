class Member:
  def __init__(self, member_key):
    self.member_key = member_key
    member_key_list = member_key.split('_')
    category_key = member_key_list[0]
    material_key = None
    member_type_key = None
    if len(member_key_list) > 1:
      material_key = member_key_list[1]
    if len(member_key_list) > 2:
      member_type_key = member_key_list[2]

    self.category_key = category_key
    self.material_key = material_key
    self.member_type_key = member_type_key

  def __repr__(self):
    return self.__class__.__name__ + "(" + self.member_key + ")"

class FloorMember(Member):
  def __init__(self, member_key):
    self.member_key = member_key

class SpreadFootingMember(Member):
  def __init__(self, member_key):
    self.member_key = member_key

class ContFootingMember(Member):
  def __init__(self, member_key):
    self.member_key = member_key
    
class ColumnMember(Member):
  def __init__(self, member_key):
    self.member_key = member_key