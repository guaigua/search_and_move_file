#!/usr/bin/env python

"""
Info Program Search and move for file 
Example:
python3 searchandmove_file.py serverfolder/source/PDF\ all.pdf dataofcompany dataoffundID dataofcompID dataofcatID dataofapproved
python3 searchandmove_file.py fileName.pdf  company fundID compID catID approved 
argv[1] -------------------------------^
argv[2] ---------------------------------------^
argv[3] ------------------------------------------------^
argv[4] -------------------------------------------------------^
argv[5] -------------------------------------------------------------^
argv[6] ---------------------------------------------------------------------^

"""
#imports

import sys
import os
import glob
import shutil
import logging
import textract
import re

import pymongo
import urllib.parse
from pymongo import MongoClient
from pprint import pprint
import os.path as path

# bd
username = urllib.parse.quote_plus('chew')
password = urllib.parse.quote_plus('zaq12Wsx')
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))

# start editable vars 

original_folder = "./serverfolder/source/"    	# folder to move files from
new_folder = "./serverfolder/destination/"      # folder to move files to
error_folder = "./serverfolder/unprocessed/"    # folder to move files with errors
logfile = "./serverfolder/logs/log.log"   		# log file to record what has happened
files_success = 0                               # count files
files_with_errors = 0							# count files with errors
size = 0.0                                      # size
pattern_to_search ='000 (.+?) Avenue'           # pattern to search is invID

invID = ''										# invID is empty
filename = os.path.basename(sys.argv[1])
company = os.path.basename(sys.argv[2])
fundID = os.path.basename(sys.argv[3])
compID = os.path.basename(sys.argv[4])
catID = os.path.basename(sys.argv[5])
approved = os.path.basename(sys.argv[6])




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
		invID = re.search(pattern_to_search, text).group(1)	
	except AttributeError:
		invID = ''
	return invID
# end function definitions 


# start process #
logger = logging.getLogger("cuarch")
hdlr = logging.FileHandler(logfile)
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
log(0,"Initialising Cron...")
folder=os.path.splitext(filename)[0]
srcfile = os.path.join(original_folder, filename)
errorfile = os.path.join(error_folder, filename)
try:
    filepath = os.stat(srcfile)
     
    if filepath:		
        invID = extractext(srcfile)    
        if invID:
            #size = size + (os.path.getsize(srcfile) / (1024*1024.0))
            #print (os.path.join(new_folder,folder))
            named = os.path.join(new_folder,invID)

            if not path.isdir(named):
                #Folder does not exist
                try:
                    #Create folder
                    os.mkdir(named)
                    log(0,"Successfully created the directory %s " % named)

                except OSError:
                    log(1,"Creation of the directory %s failed" % named)
                
            else:            
                #Folder exist
                log(0,"Folder exist %s " % named)
            
            
            destfile = os.path.join(named, filename)
            destfile			
            if not os.path.exists(destfile):
                shutil.move(srcfile, destfile)
                log(0,"Archived '" + filename + "'.")
                files_success = files_success + 1
                approved = True
                #Connect to db
                db = client.iportalDevDB19
                #Connect to collection
                collection = db.files
                
                file = { 
                        "filename": filename, 
                        "company": company, 
                        "fundID": fundID,
                        "compID": compID,
                        "catID": catID,
                        "invID": invID,
                        "approved": approved
                        }   
                rec_files = collection.insert_one(file)
            
            else:
                shutil.move(srcfile, errorfile)
                log(1,"File Exists '" + filename + "'.")
                files_with_errors = files_with_errors + 1
        else:
            shutil.move(srcfile, errorfile)
            log(1,"Without invID'" + filename + "'.")
            files_with_errors = files_with_errors + 1
except:
    log(1,"file does not exist '" + filename + "'.")

log(0,"Successfully achieved " + str(files_success) + " files, totalling " + str(round(size,2)) + "MB. files with errors " + str(files_with_errors))
end(0)


