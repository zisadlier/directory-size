import os
import sys
import getopt

hidden = []

def add_color(string, color, col):
	"""
	Add color to a string for console output
	"""

	if col is False:
		return string

	COLORS = {
		'red': '\033[0;31m',
		'green': '\033[0;32m',
		'yellow': '\033[0;33m',
		'cyan': '\033[0;36m',
	}

	if color not in COLORS.keys():
		raise IndexError("Invalid color")

	color_code = COLORS[color]
	no_color = '\033[0m'

	return color_code + string + no_color

def get_sizes_start(start_path, total_size):
	"""
	Finds the size of the starting directory, and returns a list of all directories
	and files within the starting directory. The lists contain tuples of the format
	(name, size)

		-start_path: Path to begin the walk
		-total_size: A single element list for size, simulates pass by reference
	"""
	directories = []
	files = []

	if os.path.isfile(start_path):
		total_size[0] = os.path.getsize(start_path)
		return total_size[0], directories, files

	get_sizes_recursive(start_path, directories, files, total_size)

	for d in directories:
		if d[0] == start_path:
			directories.remove(d)
			break

	return total_size[0], directories, files

def get_sizes_recursive(start_path, directories, files, total_size):
	"""
	Recursive helper function to get directory and file lists
	"""

	try:
		os.listdir(start_path)
	except OSError:
		hidden.append(start_path)
		return 0

	nodes = list(os.walk(start_path))[0]

	size = 0
	dirpath, dirnames, filenames = nodes

	for f in filenames:
		fp = os.path.join(dirpath, f)
		fs = 0
		if os.path.isfile(fp):
			fs = os.path.getsize(fp)
			files.append((fp, fs))
			size += fs
		total_size[0] += fs

	for d in dirnames:
		dp = os.path.join(dirpath, d)
		size += get_sizes_recursive(dp, directories, files, total_size)
	
	directories.append((dirpath, size))

	return size


def format_size(size_in_bytes):
	"""
	Converts an integer number of bytes to KB, MB or GB depending on how large
	it is, returns a string with units appended
	"""
	size = None
	units = 'B'

	if size_in_bytes >= 1024 ** 3:
		size = float(size_in_bytes)/(1024 ** 3)
		units = 'GB'

	elif size_in_bytes >= 1024 ** 2:
		size = float(size_in_bytes)/(1024 ** 2)
		units = 'MB'

	elif size_in_bytes >= 1024:
		size = float(size_in_bytes)/(1024)
		units = 'KB'
	else:
		size = size_in_bytes

	return str('{0:.2f}'.format(size)) + ' ' + units

def unformat_size(size):
	"""
	Takes storage size of format "size-units" and converts it to numerical bytes
	"""
	toks = size.split('-')

	size = float(toks[0])
	units = toks[1].upper()

	if units == 'GB':
		size = size * (1024 ** 3)
	if units == 'MB':
		size = size * (1024 ** 2)
	if units == 'KB':
		size = size * 1024

	return size


def main():
	#Parse command line arguments
	opts, args = getopt.getopt(sys.argv[1:], "cfden:p:m:")

	count = None
	col = True
	empty = False
	min_size = None
	get_file = True
	get_dir = True
	start_path = '.'

	for flag, val in opts:
		if flag == '-n':
			count = int(val)
		elif flag == '-e':
			empty = True
		elif flag == '-p':
			start_path = val
		elif flag == '-m':
			min_size = val
		elif flag == '-f':
			get_dir = False
		elif flag == '-d':
			get_file = False
		elif flag == '-c':
			col = False


	#Get the total size, directory and file lists
	total_size = [0]
	size, dirs, files = get_sizes_start(start_path, total_size)
	empty_dirs = []

	#Sort the directory and file lists by size
	dirs = sorted(dirs, key=lambda d: d[1], reverse=True)
	files = sorted(files, key=lambda f: f[1], reverse=True)

	#Handle passed in flags
	if empty is True:
		for d in dirs:
			if d[1] == 0:
				empty_dirs.append(d)

	if count is not None:
		dirs = dirs[:count]
		files = files[:count]

	if min_size is not None:
		min_size = unformat_size(min_size)
		dirs = [d for d in dirs if d[1] >= min_size]
		files = [f for f in files if f[1] >= min_size]

	#Print out size information
	print("")
	if hidden != []:
		print("The following directories could not be accessed:")
		for h in hidden:
			print(h)
		print("")

	if get_dir:
		print("Directories:")
		for d in dirs:
				print(add_color(d[0], 'green', col) + ' | ' + add_color(format_size(d[1]), 'cyan', col))
	print("")

	if empty is True:
		print("Empty directories:")
		for ed in empty_dirs:
			print(add_color(ed[0], 'green', col) + ' | ' + add_color(format_size(ed[1]), 'cyan', col))
		print("")

	if get_file:
		print("Files:")
		for f in files:
			print(add_color(f[0], 'green', col) + ' | ' + add_color(format_size(f[1]), 'cyan', col))

	print("\nTotal size: " + add_color(format_size(size), 'red', col))


if __name__ == "__main__":
	main()