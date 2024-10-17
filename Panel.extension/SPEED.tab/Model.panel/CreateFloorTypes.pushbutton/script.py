import clr
# import requests
clr.AddReferenceToFileAndPath("C:\\Windows\\Microsoft.NET\\assembly\\GAC_MSIL\\netstandard\\v4.0_2.0.0.0__cc7b13ffcd2ddd51\\netstandard.dll")
clr.AddReferenceToFileAndPath(r"C:\Users\Jon.R.Ryea\AppData\Roaming\McNeel\Rhinoceros\8.0\Plug-ins\SpeckleRhino2 (8dd5f30b-a13d-4a24-abdc-3e05c8c87143)\SpeckleCore2.dll")

from Speckle.Core.Credentials import *
from Speckle.Core.Api import *
from Speckle.Core.Transports import *
from Speckle.Core.Models import *

from pyrevit import forms

speckle_stream_url = forms.ask_for_string(default = 'url',
                     prompt= 'Speckle Stream URL',
                     title='Get Speckle Stream'
                     )

data = Helpers.Receive(speckle_stream_url).Result

# Use method GetDynamicMemberNames() on Base object to get children
outer_wrapper = data['Data']
base = outer_wrapper[r'@{0}'][0]
family_data = base['@familyData']

print(family_data)

# print(data_data.GetDynamicMemberNames())
# print(data2.GetDynamicMemberNames())

# account = AccountManager.GetDefaultAccount()
# client = Client(account)

# print(client.streams)

# branches = client.StreamGetBranches()
# branch = await client.BranchGet(streamId, branchName)
# print(account)
# print(client.List())

# print(Api.Client(account))
# Core.GetProperties()
# client = Client(account)
# print(client)

# ops = {'Sheet Set A': ['Item1', 'Item2', 'Item3'],
#        'Sheet Set B': ['ItemA', 'ItemB', 'ItemC']}
# res = forms.SelectFromList.show(ops,
#                                 multiselect=True,
#                                 # name_attr='Name',
#                                 group_selector_title='Sheet Sets',
#                                 title='Select Speckle Stream',
#                                 button_name='Select Sheets')
# if res.Id == viewsheet1.Id:
#     do_stuff()


