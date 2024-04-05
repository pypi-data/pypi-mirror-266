
'''
	python3 status.proc.py "_status/checks/1/status_1.py"
'''

import somatic

import time

def check_1 ():
	import pathlib
	from os.path import dirname, join, normpath
	this_directory = pathlib.Path (__file__).parent.resolve ()
	structures = normpath (join (this_directory, "shares"))

	somatic_harbor = somatic.start ({
		"directory": structures,
		"relative path": structures
	});
	
	port = somatic_harbor.port;
	
	print ()
	print ('got the somatic port')
	print ()
	
	import requests
	r = requests.get (f'http://localhost:{ port }')
	assert (r.status_code == 200)

	time.sleep (2)
	
	somatic_harbor.stop ()

	return;
	
	
checks = {
	"check 1": check_1
}