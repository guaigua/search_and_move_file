#!/usr/bin/env python
"""
Info Program Search and move for file 
Example:

python3 searchandmove_file.py  XXXXXX.pdf 
argv[1] -------------------------------^
"""
#imports

import sys
import os
import glob
import shutil
import logging
import textract
import re

# start editable vars 

original_folder = "./serverfolder/source/"    	# folder to move files from
new_folder = "./serverfolder/destination/"      # folder to move files to
error_folder = "./serverfolder/unprocessed/"    # folder to move files with errors
logfile = "./serverfolder/logs/log.log"   		# log file to record what has happened
files_success = 0                               # count files
files_with_errors = 0							# count files with errors
size = 0.0                                      # size
found = ''										# found is empty
pattern_to_search ='Fecha:(.+?) Hora:'          # pattern to search
# end editable vars

# start function definitions 

#log

def log(level,msg,tofile=True):
	print (msg)
	
	if tofile == True:
		if level == 0:
			logger.info(msg)
		else:
			logger.error(msg)
	
def end(code):
	log(0,"End...")	
	log(0,"----------------------------------------------------------------------------------")


def extractext(file):	
	try:
		text = str(textract.process(file))
		found = re.search(pattern_to_search, text).group(1)
		print (found)
	except AttributeError:
		found = ''
	return found
# end function definitions 


# start process #
logger = logging.getLogger("cuarch")
hdlr = logging.FileHandler(logfile)
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
log(0,"Initialising Cron...")

filename = os.path.basename(sys.argv[1])
folder=os.path.splitext(filename)[0]
srcfile = os.path.join(original_folder, filename)	
errorfile = os.path.join(error_folder, filename)
if os.stat(srcfile):		
    found = extractext(srcfile)			
    if found:	
        size = size + (os.path.getsize(srcfile) / (1024*1024.0))
        named = os.path.join(new_folder,folder)
        try:
            #Create folder
            os.mkdir(named)
            log(0,"Successfully created the directory %s " % named)

        except OSError:
            log(1,"Creation of the directory %s failed" % named)
        
        
        destfile = os.path.join(named, filename)
        destfile			
        if not os.path.exists(destfile):
            shutil.move(srcfile, destfile)
            log(0,"Archived '" + filename + "'.")
            files_success = files_success + 1
        else:
            shutil.move(srcfile, errorfile)
            log(1,"File Exists '" + filename + "'.")
            files_with_errors = files_with_errors + 1
    else:
        shutil.move(srcfile, errorfile)
        log(1,"Archived '" + filename + "'.")
        files_with_errors = files_with_errors + 1

log(0,"Successfully achieved " + str(files_success) + " files, totalling " + str(round(size,2)) + "MB. files with errors " + str(files_with_errors))
end(0)


