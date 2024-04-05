

'''
	import somatic

	import pathlib
	from os.path import dirname, join, normpath
	this_dir = str (pathlib.Path (__file__).parent.resolve ())
	somatic_harbor.start ({
		"directory": this_dir,
		"relative path": this_dir
	});

	somatic_harbor.server.stop ()
'''

print ("__name__", __name__)

from somatic._clique import clique

from somatic.moves.start import start
