#!/usr/bin/python3
# -*- encoding: utf-8 -*-

__version__ = "0.1"
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
import os, argparse, sqlite3, shutil

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
biosfolder	= None
snapfolder	= "snap"
dbpath		= "romsDB.sqlite"

snap_mv 	= "no_rom_snap"	# foder where no matching pictures goes.

# main
if __name__ == '__main__':
	########################################
	# Retrieve cmd line parameters
	########################################
	parser = argparse.ArgumentParser()

	parser.add_argument("-r", "--roms", default=romfolder,
						help="rom folder path")
	parser.add_argument("-b", "--bios", default=biosfolder,
						help="bios folder path")
	parser.add_argument("-s", "--snap", default=snapfolder,
						help="snapshots picture folder path")

	args = parser.parse_args()
	
	# adding ending slashes to pahts
	romfolder = addslash(args.roms)
	snapfolder = addslash(args.snap)
	if (args.bios):
		biosfolder = addslash(args.bios)

	# Checking parameters
	errorlist 	= []
	warninglist	= []
	if itemcheck(romfolder) 	!= "folder":
		errorlist.append ("error in rom parameter:(--rom {}), folder does not exist.".format(romfolder,))
	if itemcheck(snapfolder) 	!= "folder":
		errorlist.append ("error in snapshot parameter: (--snap {}),  folder does not exist.".format(snapfolder))
	print (biosfolder)
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
		Romname char NOT NULL ,\
		Fileext char\
		)')

	cursor.execute ('CREATE TABLE snap (\
		Pictname char NOT NULL ,\
		Fileext char\
		)')

	cursor.execute ('CREATE TABLE bios (\
		Biosname char NOT NULL ,\
		Fileext char\
		)')

	con.commit()

	########################################
	# Populating DB
	########################################

	ficheros = os.listdir(romfolder)
	for i in ficheros:
		if itemcheck (os.path.join(romfolder,i)) == "file":
			data = os.path.splitext(os.path.basename(i))
			con.execute ("INSERT INTO ROMS (Romname, Fileext) VALUES (?,?)", data) 		

	ficheros = os.listdir(snapfolder)
	for i in ficheros:
		if itemcheck (os.path.join(snapfolder,i)) == "file":
			data = os.path.splitext(os.path.basename(i))
			con.execute ("INSERT INTO SNAP (Pictname, Fileext) VALUES (?,?)", data) 		

	if biosfolder:
		ficheros = os.listdir(biosfolder)
		for i in ficheros:
			if itemcheck (os.path.join(biosfolder,i)) == "file":
				data = os.path.splitext(os.path.basename(i))
				con.execute ("INSERT INTO BIOS (Biosname, Fileext) VALUES (?,?)", data) 		

	con.commit()

	########################################
	# Showing results and asking user
	########################################

	# number of pictures matching roms:
	# SELECT Pictname,Fileext FROM snap where lower(snap.Pictname) in (SELECT lower(Romname) from roms) order by Pictname

	# number of pictures that does not matches roms
	# SELECT Pictname,Fileext FROM snap where lower(snap.Pictname) not in (SELECT lower(Romname) from roms) order by Pictname

	# number of bios found
	# SELECT count(*) from bios

	# number of bios found on roms folder
	# SELECT Romname, lower(Fileext) from roms WHERE lower(Romname) in (SELECT lower(Biosname) from bios)

	Messages = []
	text = "Number of pictures found:"
	value = con.execute ("SELECT count(*) from snap").fetchone()[0]
	Messages.append ((text, value),)

	text = "Number of pictures that matches roms:"
	value = con.execute ("SELECT count(Pictname) FROM snap where lower(snap.Pictname) in (SELECT lower(Romname) from roms) order by Pictname").fetchone()[0]
	Messages.append ((text, value),)

	text = "Number of pictures to move:"
	value_pic = con.execute ("SELECT count(Pictname) FROM snap where lower(snap.Pictname) not in (SELECT lower(Romname) from roms) order by Pictname").fetchone()[0]
	Messages.append ((text, value_pic),)

	if biosfolder:
		text = "Number of bios found:"
		value = con.execute ("SELECT count(*) from bios").fetchone()[0]
		Messages.append ((text, value),)

		text = "Number of bios found on roms folder:"
		value = con.execute ("SELECT count(Romname) from roms WHERE lower(Romname) in (SELECT lower(Biosname) from bios)").fetchone()[0]
		Messages.append ((text, value),)

	for m in Messages:
		print (m[0], m[1])

	r = input ("Want to proceed? (y/n):")
	if r in ("nN"):
		exit()

	########################################
	# Processing files
	########################################

	# BIOS
	# Delete Bios on rom folder
	if biosfolder:
		print ("\tDeleting Bios on Rom folder")
		cursor = con.execute ("SELECT Romname||Fileext from roms WHERE lower(Romname) in (SELECT lower(Biosname) from bios)")
		for b in cursor:
			file = os.path.join(romfolder, b[0])
			print ("deleting: ", file, end=" > ")
			os.remove (file)
			print ("OK!")

	# PICT
	# Moving not matching pictures
	print ("\tMoving not matching pictures.")
	if value_pic > 0:
		mvpath = os.path.join(snapfolder,snap_mv)
		if itemcheck (mvpath) != "folder":
			os.makedirs (mvpath)
		cursor = con.execute ("SELECT Pictname||Fileext FROM snap where lower(snap.Pictname) not in (SELECT lower(Romname) from roms) order by Pictname")
		for p in cursor:
			file = os.path.join(snapfolder, p[0])
			mvfile = os.path.join(mvpath,p[0])
			print ("moving file: ", file, end=" > ")
			shutil.move (file, mvfile)
			print ("OK!")

	# Renaming files to lowercase
	Data = (
		{'name':"Pictures",	'table':"snap", 'field':"Pictname",	'folder':snapfolder},
		{'name':"Roms",		'table':"roms", 'field':"Romname",	'folder':romfolder},
		{'name':"Bios",		'table':"bios",	'field':"Biosname",	'folder':biosfolder},
	)

	for i in Data:
		upperelements = con.execute (f"SELECT COUNT({i['field']}||Fileext) FROM \
					{i['table']} WHERE\
					lower({i['field']})||lower(Fileext) != {i['field']}||Fileext").fetchone()[0]
		if upperelements > 0:
			print (f"\tRenaming {i['name']} to lowercase")
			cursor = con.execute (f"SELECT {i['field']}||Fileext AS origin, lower({i['field']}||Fileext) AS dest \
					FROM {i['table']} WHERE\
					lower({i['field']})||lower(Fileext) != {i['field']}||Fileext")
			for m in cursor:
				origin = os.path.join(i['folder'], m[0])
				dest = os.path.join(i['folder'],m[1])
				print ("renaming file: ", origin, " > ", dest, " : ", end=" > ")
				if itemcheck (origin) != "file":
					print ("origin file does not exist. Doing notthing", end=" > ")
				elif itemcheck (dest) == "file":
					print ("forcing renaming origin file", end=" > ")
					shutil.move (origin, origin+".tmp")
					shutil.move (origin+".tmp", dest)
				else:
					shutil.move (origin, dest)
				print ("OK!")


con.close()

print ("Done!")