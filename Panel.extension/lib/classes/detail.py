from data.data import detail_data
from classes.members import *

class Detail:
  detail_keys = None
  detail = None

  def __init__(self, detail_key):

    detail_keys = detail_data.keys()
    detail = detail_data[detail_key]

    assert detail_key in detail_keys, 'imeg detail number cannot be found'

    self._detail_key = detail_key
    self._name = detail['name']
    self._connections = detail['connections']
    self._members = detail['members']

  def __repr__(self):
    return self.__class__.__name__ + "(" + self.__detail_key + ")"

  @property
  def name(self):
    return self._name
  @property
  def detail_key(self):
    return self._detail_key
  @property
  def connections(self):
    return self._connections
  @property
  def members(self):
    return self._members

  def get_category(self, member_key):
    member_key_list = member_key.split('_')
    category_key = member_key_list[0]
    return category_key

  def create_member(self, member_key):
    member = None
    category = self.get_category(member_key)
    print(category)
    if category == 'fl':
      member = FloorMember(member_key)
    elif category == 'co':
      member == ColumnMember(member_key)
    elif category == 'sf':
      member == SpreadFootingMember(member_key)
    elif category == 'cf':
      member == ContFootingMember(member_key)
    print(member)
    return member

  def get_view_detail_members(self, discipline):
    view_members = []
    if discipline == 'structural':
      member_keys = self.members['structural']
      for member_key in member_keys:
        member = self.create_member(member_key)
        print(member)
        view_members.append(member)
    return view_members