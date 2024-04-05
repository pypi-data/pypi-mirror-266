
import glob
import os
import json

def start (
	directory = None,
	extension = None,
	relative_path = None,
	verbose = None,
	
	paths = None
):
	glob_param = directory + "/**/*" + extension;
	if (verbose >= 0):
		print ("searching glob:", glob_param)

	finds = glob.glob (glob_param, recursive = True)
	if (verbose >= 2):
		print ("finds:", json.dumps (finds, indent = 4))
	
	for find in finds:
		path = os.path.relpath (find, relative_path)
		name = path.split (extension) [0]
	
		paths.append ({
			"path": path,
			"name": name,
			"find": find
		})