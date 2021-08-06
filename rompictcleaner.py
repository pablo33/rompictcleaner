#!/usr/bin/python3
# -*- encoding: utf-8 -*-

__version__ = "0.0"
__author__  = "pablo33"

'''
    This program cleans your snapshot pictures folder by matching
    your roms folder
    usage on command line preferible on relative paths.

    params on command line input:
    --rom   path/to/roms/folder
    --bios  path/to/bios/folder
    --snap  path/to/pictures folder

    '''

# Standard libray imports
import os, argparse, sqlite3

# Error classes
class NotStringError(ValueError):
	pass
class MalformedPathError(ValueError):
	pass


# Functions

def itemcheck(pointer):
	''' returns what kind of a pointer is '''
	if type(pointer) is not str:
		raise NotStringError ('Bad input, it must be a string')
	if pointer.find("//") != -1 :
		raise MalformedPathError ('Malformed Path, it has double slashes')
	if os.path.isfile(pointer):
		return 'file'
	if os.path.isdir(pointer):
		return 'folder'
	if os.path.islink(pointer):
		return 'link'
	return ""

def addslash (text):
	''' Returns an ending slash in a path if it doesn't have one '''
	if type(text) is not str:
		raise NotStringError ('Bad input, it must be a string')

	if text == "":
		return text

	if text [-1] != '/':
		text += '/'
	return text


def printlist (mylist):
	for i in mylist:
		print (i)


# Defaults:
romfolder	= "roms"
biosfolder	= "bios"
snapfolder	= "snap"
dbpath		= "romsDB.sqlite"

# main
if __name__ == '__main__':
	########################################
	# Retrieve cmd line parameters
	########################################
	parser = argparse.ArgumentParser()

	parser.add_argument("-r", "--roms", default=romfolder,
						help="rom folder path")
	parser.add_argument("-b", "--bios",
						help="bios folder path")
	parser.add_argument("-s", "--snap", default=snapfolder,
						help="snapshots picture folder path")

	args = parser.parse_args()
	
	# adding ending slashes to pahts
	romfolder = addslash(args.roms)
	snapfolder = addslash(args.snap)
	biosfolder = addslash(args.bios)

	# Checking parameters
	errorlist 	= []
	warninglist	= []
	if itemcheck(romfolder) 	!= "folder":
		errorlist.append ("error in rom parameter:(--rom {}), folder does not exist.".format(romfolder,))
	if itemcheck(snapfolder) 	!= "folder":
		errorlist.append ("error in snapshot parameter: (--snap {}),  folder does not exist.".format(snapfolder))
	if biosfolder == None:
		warninglist.append ("no bios folder has been defined.")
	elif itemcheck(biosfolder) 	!= "folder":
		errorlist.append ("error in bios parameter: (--bios {}), folder does not exist.".format(biosfolder))

	# Showing errors and exitting if errors
	if len (warninglist) > 0:
		printlist (warninglist)
	if len (errorlist) > 0:
		errorlist.append ("Please revise errors and try again")
		printlist (errorlist)
		exit()

	########################################
	# Init Database
	########################################

	if itemcheck (dbpath) == 'file':
		os.remove (dbpath)
		print ("Older database found, it has been deleted.")

	con = sqlite3.connect (dbpath) # it creates one if file doesn't exists
	cursor = con.cursor() # object to manage queries

	cursor.execute ('CREATE TABLE roms (\
		ID INT PRIMARY KEY NOT NULL,\
		Fullfilepath char NOT NULL ,\
		Filename char NOT NULL ,\
		Fileext char\
		)')

	cursor.execute ('CREATE TABLE snap (\
		ID INT PRIMARY KEY NOT NULL,\
		Fullfilepath char NOT NULL ,\
		Pictname char NOT NULL ,\
		Fileext char\
		)')

	cursor.execute ('CREATE TABLE bios (\
		ID INT PRIMARY KEY NOT NULL,\
		Fullfilepath char NOT NULL ,\
		Biosname char NOT NULL ,\
		Biosext char\
		)')

	con.commit()

print ("Done!")


