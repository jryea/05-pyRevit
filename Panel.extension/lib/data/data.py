import utilities as util
"""
STRUCTURAL MEMBERS

<structural member>_<material>_<section/family>_<size/symbol>

bm = beam
co = column
fl = floor
wa = wall
cf = continuous footing
sf = spread footing

st = steel
co = concrete

ks = k-series joist

STRUCTURAL CONNECTIONS

2b2c = 2 beams to column
c2f = column to footing
"""

detail_data = (
{'2200-03': {'name': 'COLUMN FOOTING DETAIL',
  'members': {
    'structural': ['co_st', 'fl_co', 'sf'],
    'architectural': None
              },
  'connections':[['co_st', 'sf']]},

'2200-04': {'name': 'STEEL JOIST BEARING AT WF COLUMN',
'members': {
  'structural':['co_st', 'bm_st_ks'],
  'architectural': None
            },
 'connections': [('2b2c', ['co_st', 'bm_st_ks']), ('c2f', ['co_st','bm_st_sk'])]}})

