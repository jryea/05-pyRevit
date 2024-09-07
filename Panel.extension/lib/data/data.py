import utilities as util
detail_data = (
{'2200-03': {'name': 'COLUMN FOOTING DETAIL',
  'members': {
    'structural': ['co_st', 'fl_co', 'sf'],
    'architectural': None
              },
  'connections':[['co_st', 'sf']]},

'2200-04': {'name': 'STEEL JOIST BEARING AT WF COLUMN',
'members': {
  'structural':['co_st', 'bm_st_ks', 'bm_st_ks'],
  'architectural': None
            },
 'connections': [['co_st', 'bm_st_ks'], ['co_st','bm_st_sk']]}})

# def data_test():
#   print('and this is the data file!')