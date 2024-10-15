from Autodesk.Revit.DB import *
from utilities.collection import Collection
from System.Collections.Generic import List

def find_closest_level_from_elevation(doc, elevation):
  levels = Collection.get_levels(doc)
  closest_level = levels[0]
  for level in levels:
    level_elev = level.ProjectElevation
    closest_level_elev = closest_level.ProjectElevation
    level_elev_diff = abs(elevation - level_elev)
    closest_level_elev_diff = abs(elevation - closest_level_elev)
    if level_elev_diff < closest_level_elev_diff:
      closest_level = level
  return closest_level

def get_top_level(doc):
  levels = Collection.get_levels(doc)
  top_level = levels[0]
  for level in levels:
    level_elevation = level.ProjectElevation
    top_level_elevation = top_level.ProjectElevation
    if level_elevation > top_level_elevation:
      top_level = level
  return top_level

def get_base_level(doc):
  levels = Collection.get_levels(doc)
  base_level = levels[0]
  for level in levels:
    level_elevation = level.ProjectElevation
    base_level_elevation = base_level.ProjectElevation
    if level_elevation < base_level_elevation:
      base_level = level
  return base_level

def get_level_above(doc, current_level):
  current_level_elevation = current_level.ProjectElevation
  levels = Collection.get_levels(doc)
  level_above = get_top_level(doc)
  if Element.Name.GetValue(level_above) == Element.Name.GetValue(current_level):
    return None
  for level in levels:
    level_above_elevation = level_above.ProjectElevation
    level_elevation = level.ProjectElevation
    if level_elevation > current_level_elevation\
    and level_elevation < level_above_elevation:
        level_above = level
  return level_above

def get_level_below(doc, current_level):
  current_level_elevation = current_level.ProjectElevation
  levels = Collection.get_levels(doc)
  level_below = get_base_level(doc)
  if Element.Name.GetValue(level_below) == Element.Name.GetValue(current_level):
    return None
  for level in levels:
    level_below_elevation = level_below.ProjectElevation
    level_elevation = level.ProjectElevation
    if level_elevation < current_level_elevation\
    and level_elevation > level_below_elevation:
        level_below = level
  return level_below
