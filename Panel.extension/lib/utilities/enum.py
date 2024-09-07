from enum import Enum

class Discipline(Enum):
  Structural = 1
  Architectural = 2

class Category(Enum):
  Column = 1
  Beam = 2
  Floor = 3
  Wall = 4
  ContFooting = 5
  SpreadFooting = 6

class Material(Enum):
  ColdForm = 1
  Concrete = 2
  Masonry = 3
  Precast = 4
  Steel = 5
  Wood = 6