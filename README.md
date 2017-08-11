# Directory size tool

Get a the total size, largest subdirectories and largest files within a certain directory

## Flags
* -n <num>: Specify the maximum files and directories to list
* -e: Display a list of empty subdirectories
* -p <path>: Specify the root directory to begin th top down walk (default is .)
* -m <size>: Minimum file/directory size to be displayed
* -c: Disable colored output
* -f: Only list files
* -d: Only list subdirectories

Note: If both -f and -d are present only the total size of the root directory will be displayed

## Version
`
1.1.0
`

## Use

The following example displays both files and subdirectories of /tmp larger than 10 KB

`
python dirsize.py -p /tmp -m 10-kb
`

This next example shows the top 10 largest files and all empty subdirectories under .

`
python dirsize.py -n 10 -f -e
`
