#rompictcleaner
A mame rom and picture matching and cleaner  

# History
This piece of software aims to solve a couple of problems managing mame roms.  

I use MALA 1.74 as frontend and I have some problems.  

Mala uses a folder to retrieve a list of roms.
On the other hand it matches this roms with their correspondent picture at snap folder.  

There can be more pictures than the strictly needed, so you can delete a rom, but you also need to delete their picture.  

Mame needs bios files beside the roms to work, and MALA will also retrieve them.  

The idea is to make MALA lists without bios and clean the picture folder.  

The software will:  
  * move apart useless pictures to a new folder.
  * separate bios from roms folder
  * rename all files to lowercase

You need a separate folder with bios files. The software will match these bios on roms folder an will delete them. After refreshing your lists in MALA, you will want to copy the bios files again among the roms files.


## Input parameters on command line
* roms folder ("roms" by default) --rom , -r
* snapshot folder ("snap" by default) --snap , -s
* bios folder ("bios" by default) --bios  ,  -b

Input example:
rompictcleaner --rom roms/ --snap snap/ --bios bios/

Getting command line help:
rompictcleaner --help


It uses a SQLite3 Data base for better performance and for future functions.