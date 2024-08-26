import os
import sys
import re

import click

hidden = []

def add_color(string, color, col):
    if col is False:
        return string

    COLORS = {
        'red': '\033[0;31m',
        'green': '\033[0;32m',
        'yellow': '\033[0;33m',
        'cyan': '\033[0;36m',
    }

    if color not in COLORS.keys():
        raise IndexError('Invalid color')

    color_code = COLORS[color]
    no_color = '\033[0m'

    return color_code + string + no_color

def get_sizes_start(start_path, total_size):
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

def is_hidden(path):
    if re.match('^./', path):
        path = path[1:]

    if path.count('/.'):
        return True

    return False

@click.command()
@click.option('-n', '--count', type=int, help='Directory and file count limit')
@click.option('-c', '--color', is_flag=True, help='If present, uses colored text in some output')
@click.option('-e', '--empty', is_flag=True, help='If present, displays empty directories')
@click.option('-m', '--min-size', help='Minimum size for a file/directory to be counted')
@click.option('-d', '--get-dir', is_flag=True, help='If present, displays data for individual directories')
@click.option('-f', '--get-file', is_flag=True, help='If present, displays data for individual files')
@click.option('-s', '--show-hidden', is_flag=True, help='If present, displays data for hidden directories and files')
@click.option('-p', '--path', default='.', help='Path to get the directory size of')
def main(count: int, color: bool, empty: bool, min_size: str, get_dir: bool, get_file: bool, show_hidden: bool, path: str):
    #Get the total size, directory and file lists
    total_size = [0]
    size, dirs, files = get_sizes_start(path, total_size)
    empty_dirs = []

    #Sort the directory and file lists by size
    dirs = sorted(dirs, key=lambda d: d[1], reverse=True)
    files = sorted(files, key=lambda f: f[1], reverse=True)

    #Handle passed in flags
    if empty is True:
        for d in dirs:
            if d[1] == 0:
                empty_dirs.append(d)

    if show_hidden is False:
        dirs = [d for d in dirs if not is_hidden(d[0])]
        files = [f for f in files if not is_hidden(f[0])]

    if min_size is not None:
        min_size = unformat_size(min_size)
        dirs = [d for d in dirs if d[1] >= min_size]
        files = [f for f in files if f[1] >= min_size]

    if count is not None:
        dirs = dirs[:count]
        files = files[:count]

    #Print out size information
    print('')
    if hidden != []:
        print('The following directories could not be accessed:')
        for h in hidden:
            print(h)
        print('')

    if get_dir:
        print('Directories:')
        for d in dirs:
            print(add_color(d[0], 'green', color) + ' | ' + add_color(format_size(d[1]), 'cyan', color))
    print('')

    if empty is True:
        print('Empty directories:')
        for ed in empty_dirs:
            print(add_color(ed[0], 'green', color) + ' | ' + add_color(format_size(ed[1]), 'cyan', color))
        print('')

    if get_file:
        print('Files:')
        for f in files:
            print(add_color(f[0], 'green', color) + ' | ' + add_color(format_size(f[1]), 'cyan', color))

    print('\nTotal size: ' + add_color(format_size(size), 'red', color))

if __name__ == '__main__':
    main()
