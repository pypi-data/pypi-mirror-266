#!/usr/bin/python3

'''
	~/adventures/vaccines-tavern
	
	nano ~/adventures/vaccines-tavern
		#!/usr/bin/python3
		python3 /media/treasury-1/water/status600.com/pypi/reptilian_climates/modules_series_4/vaccines/modules/structures/vaccines/bin/vaccines-tavern.py
	
	
	PATH=$PATH:/media/treasury-1/water/status600.com/pypi/reptilian_climates/modules_series_4/vaccines/modules/structures/vaccines/bin
	
	vaccines-tavern
'''

import pathlib
from os.path import dirname, join, normpath
import sys
def add_paths_to_system (paths):	
	this_folder = pathlib.Path (__file__).parent.resolve ()	
	for path in paths:
		sys.path.insert (0, normpath (join (this_folder, path)))

add_paths_to_system ([
	'../../structures',
	'../../structures_pip'
])

import vaccines
vaccines.clique ()