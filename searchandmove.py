#!/usr/bin/env python
"""
Info
"""
#imports
import sys
import os
import glob
import shutil
import time
import logging
from datetime import datetime, date, timedelta

# start editable vars 

original_folder = "./serverfolder/source/"    	# folder to move files from
new_folder = "./serverfolder/destination/"		# folder to move files to
error_folder = "./serverfolder/unprocessed/"	# folder to move files with errors
logfile = "./serverfolder/logs/log.log"   		# log file to record what has happened
count = 0                                       # count
size = 0.0                                      # size
# end editable vars

# start function definitions 

def log(level,msg,tofile=True):
	print (msg)
	
	if tofile == True:
		if level == 0:
			logger.info(msg)
		else:
			logger.error(msg)
			
def end(code):
	log(0,"End.")
	log(0,"-------------------------")
# end function definitions #logging.getLogger("cuarch")

# start process #

logger = logging.getLogger("cuarch")
hdlr = logging.FileHandler(logfile)
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)

log(0,"Initialising...")

for filename in glob.glob1(original_folder, "*.*"):
    srcfile = os.path.join(original_folder, filename)
    #create carpeta con nuevo destino
    destfile = os.path.join(new_folder, filename)
    #Condicional
    if os.stat(srcfile):   
    	if not os.path.isfile(destfile):
            print ("Test")
    		size = size + (os.path.getsize(srcfile) / (1024*1024.0))

	        shutil.move(srcfile, destfile)        
	        log(0,"Archived '" + filename + "'.")
	        count = count + 1

log(0,"Archived " + str(count) + " files, totalling " + str(round(size,2)) + "MB.")
end(0)
