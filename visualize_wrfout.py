import os, pprint, sys, math, numpy
from optparse import OptionParser
from netCDF4 import Dataset

def dir_entries(dir_path='', subdir=False, *args):
	'''Return a list of file names found in directory 'dir_path'
	If 'subdir' is True, recursively access subdirectories under 'dir_path'.
	Additional arguments, if any, are file extensions to match filenames. Matched
		file names are added to the list.
	If there are no additional arguments, all files found in the directory are
		added to the list.
	Example usage: fileList = dirEntries(r'H:\TEMP', False, 'txt', 'py')
		Only files with 'txt' and 'py' extensions will be added to the list.
	Example usage: fileList = dirEntries(r'H:\TEMP', True)
		All files and all the files in subdirectories under H:\TEMP will be added
		to the list.
	'''
	dir_path = os.getcwd() + os.sep + dir_path

	fileList = []
	for file in os.listdir(dir_path):
		dirfile = os.path.join(dir_path, file)
		if os.path.isfile(dirfile):
			if not args:
				fileList.append(dirfile)
			else:
				if os.path.splitext(dirfile)[1][1:] in args:
					fileList.append(dirfile)
		# recursively access file names in subdirectories
		elif os.path.isdir(dirfile) and subdir:
			fileList.extend(dir_entries(dirfile, subdir, *args))
	return fileList

def get_keys_and_descriptions_and_shapes_and_max_values(infile, filter_search):
	return [
		(key, infile.variables[key].description.strip(), infile.variables[key].shape, numpy.max(infile.variables[key]))
		for key in infile.variables.keys()
		if hasattr(infile.variables[key], 'description') and (
			filter_search == '' or filter_search in key.lower() or filter_search in infile.variables[key].description.lower()
		) and (
			numpy.max(infile.variables[key]) != 0
		)
	]

def get_layer_index(infiles, variable_key):
	variable = infiles[0].variables[variable_key]
	if len(variable.shape) == 4:
		return input('Variable has %i vertical layers. Please specify layer index to show:' %(variable.shape[1]))
	return None

def get_longitude_and_latitude(infiles):
	longitude = numpy.degrees(infiles[0].variables['GLON'][0])
	latitude = numpy.degrees(infiles[0].variables['GLAT'][0])
	return longitude, latitude

parser = OptionParser()
parser.add_option("-a", "--all-files", action="store_true", dest="all_files")
(options, args) = parser.parse_args()
potential_filenames = [entry.rsplit('/', 1)[1] for entry in dir_entries()]
wrfout_filenames = [entry for entry in potential_filenames if entry.find('wrfout_') == 0]
if len(wrfout_filenames) == 0:
	print 'no wrfout files in this directory - aborting'
	sys.exit(1)
infiles = None
infile_names = None
if not options.all_files:
	print('List of the available wrfout-files in this directory. Choose one index to visualize.')
	print('\n'.join(["%i:\t%s" %(index, entry) for index, entry in enumerate(wrfout_filenames)]))
	file_index = input('Please enter one index:')
	wrfout_file_name = wrfout_filenames[file_index]
	infiles = [Dataset(wrfout_file_name)]
	infile_names = [wrfout_file_name]
else:
	infiles = []
	for wrfout_file_name in wrfout_filenames:
		try:
			infiles.append(Dataset(wrfout_file_name))
		except Exception as e:
			print "could not import file %s: %s" %(wrfout_file_name, str(e))
	infile_names = wrfout_filenames
filter_search = raw_input('Please enter a search term within variable descriptions or keys to filter by:')
filter_search = filter_search.lower().strip()
keys_and_descriptions_and_shapes_and_max_values = get_keys_and_descriptions_and_shapes_and_max_values(infiles[0], filter_search)
if len(keys_and_descriptions_and_shapes_and_max_values) == 0:
	print 'no variables found with that term in the description or key'
	sys.exit(1)
print('List of the available variables in this file. Choose one index to visualize.')
print ('\n'.join([
	"%i:\t%s%s%s (shape: %s, max value: %s)" %(
		index,
		key_and_description_and_shape[0],
		''.join([' ' for index in range(12-len(key_and_description_and_shape[0]))]),
		key_and_description_and_shape[1],
		key_and_description_and_shape[2],
		numpy.max(infiles[0].variables[key_and_description_and_shape[0]])
	)
	for index, key_and_description_and_shape in enumerate(keys_and_descriptions_and_shapes_and_max_values)
]))
variable_index = input('Please enter one index:')
print('visualizing %s for %s' %(str(keys_and_descriptions_and_shapes_and_max_values[variable_index]), wrfout_filenames[0]))
layer_index = get_layer_index(infiles, keys_and_descriptions_and_shapes_and_max_values[variable_index][0])
longitude, latitude = get_longitude_and_latitude(infiles)
min_longitude = numpy.min(longitude)
max_longitude = numpy.max(longitude)
min_latitude = numpy.min(latitude)
max_latitude = numpy.max(latitude)
print(
	'latitude from: %s, to: %s; longitude from: %s, to: %s' %(
		str(min_latitude),
		str(max_latitude),
		str(min_longitude),
		str(max_longitude)
	)
)
import matplotlib.pyplot as pyplot
from mpl_toolkits.basemap import Basemap
plot_map = Basemap(
	projection='lcc',
	lat_1=(max_latitude+min_latitude)/2,
	lat_0=(max_latitude+min_latitude)/2,
	lon_0=(max_longitude+min_longitude)/2,
	llcrnrlon=min_longitude,
	llcrnrlat=min_latitude,
	urcrnrlon=max_longitude,
	urcrnrlat=max_latitude,
	resolution='l'
)
plot_map.drawcountries()
plot_map.drawcoastlines()
plot_map.drawlsmask()
plot_map.drawrivers()
for index, infile in enumerate(infiles):
	variable = infile.variables[keys_and_descriptions_and_shapes_and_max_values[variable_index][0]]
	layer = None
	if len(variable.shape) == 2:
		layer = variable[:, :]
	elif len(variable.shape) == 3:
		layer = variable[0, :, :]
	elif len(variable.shape) == 4:
		layer = variable[0, layer_index, :, :]
	else:
		print 'unrecognized shape, only variables with two, three or four dimensions supported'
		sys.exit(1)
	min_value = numpy.min(layer)
	max_value = numpy.max(layer)
	color_mesh = plot_map.pcolormesh(
		longitude,
		latitude,
		layer,
		vmin=min_value,
		vmax=max_value,
		cmap=pyplot.get_cmap('spectral'),
		latlon=True
	)
	if index == 0:
		color_bar = pyplot.colorbar(color_mesh)
		color_bar.set_label(variable.units)
	plot = None
	if layer_index != None:
		pyplot.title("%s\nat vertical layer %i\n%s" %(variable.description, layer_index, infile_names[index]))
	else:
		pyplot.title(variable.description)
	if layer_index != None:
		pyplot.savefig("%s_layer%i_from_%s.png" %(
			keys_and_descriptions_and_shapes_and_max_values[variable_index][0],
			layer_index,
			infile_names[index]
		))
	else:
		pyplot.savefig("%s_from_%s.png" %(
			keys_and_descriptions_and_shapes_and_max_values[variable_index][0],
			infile_names[index]
		))
	infile.close()
