#!/usr/bin/env python

"""
Info Program Search and move for file
Example:
python3 searchandmove_file.py serverfolder/source/PDF\ all.pdf dataofdocType dataofcompID dataoffundID dataofcatID dataofapproved dataofpending
python3 searchandmove_file.py fileName.pdf docType compID fundID catID approved pending
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
import PyPDF2
import pymongo
import urllib.parse
import json
import os.path as path
from pymongo import MongoClient
from PyPDF2 import PdfFileWriter, PdfFileReader
from datetime import datetime

# bd
username = urllib.parse.quote_plus('chew')
password = urllib.parse.quote_plus('zaq12Wsx')
client = MongoClient('mongodb://%s:%s@127.0.0.1' % (username, password))

# start editable vars
original_folder = "./serverfolder/source/"    	# folder to move files from
pdf_folder = "./"                               # pdf files from
new_folder = "./serverfolder/destination/"      # folder to move files to
ok_folder = "./serverfolder/processed/"    # folder to move files is ok
error_folder = "./serverfolder/unprocessed/"    # folder to move files with errors
logfile = "./serverfolder/logs/log.log"   		# log file to record what has happened
files_success = 0                               # count files
files_with_errors = 0							# count files with errors
size = 0.0                                      # size
pattern_to_search ='000 (.+?) Avenue'           # pattern to search is invID
dst = None
invID = ''										# invID is empty
date = datetime.today()                         # date
filename = os.path.basename(sys.argv[1])
docType = os.path.basename(sys.argv[2])
compID = os.path.basename(sys.argv[3])
fundID = os.path.basename(sys.argv[4])
catID = os.path.basename(sys.argv[5])
approved = os.path.basename(sys.argv[6])
pending = os.path.basename(sys.argv[7])
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

def safe_copy(file_path, out_dir, dst = None):
    """Safely copy a file to the specified directory. If a file with the same name already
    exists, the copied file name is altered to preserve both.

    :param str file_path: Path to the file to copy.
    :param str out_dir: Directory to copy the file into.
    :param str dst: New name for the copied file. If None, use the name of the original
        file.
    """
    name = dst or os.path.basename(file_path)
    if not os.path.exists(out_dir):
        shutil.move(file_path, out_dir)

    else:
        base, extension = os.path.splitext(name)
        f = 0
        while os.path.exists(os.path.join(out_dir, '{}_{}{}'.format(base, f, extension))):
            f += 1
        shutil.move(file_path, os.path.join(out_dir, '{}_{}{}'.format(base, f, extension)))
        log(0,"File Exists '" + filename + "'.")
        f = 0

# end function definitions

# start process #

logger = logging.getLogger("cuarch")
hdlr = logging.FileHandler(logfile)
hdlr.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s: %(message)s'))
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)
log(0,"Initialising...")
folder=os.path.splitext(filename)[0]

srcfile = os.path.join(original_folder, filename)
okfile = os.path.join(ok_folder, filename)
errorfile = os.path.join(error_folder, filename)

try:
    filepath = os.stat(srcfile)
    filepath
    with open(srcfile, "rb") as f:
        pdf = PdfFileReader(f)
        bookmarks = pdf.getOutlines()
        pdf
        bookmarks
        for b in bookmarks:
            invID = b['/Title']
            if len(invID) > 20 :
                i = pdf.getDestinationPageNumber(b)
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

            #Split pdf
            output = PdfFileWriter()
            output.addPage(pdf.getPage(i))
            with open(filename, "wb") as outputStream:
                output.write(outputStream)

            if invID:
                pdffile = os.path.join(pdf_folder, filename)
                destfile = os.path.join(named, filename)
                renamefile = os.path.join(named, filename)
                safe_copy(pdffile,named)
                files_success = files_success + 1
                approved = True
                #Connect to db
                db = client.iportalDevDB19
                #Connect to collection
                collection = db.files

                file = {
                        "filename": filename,
                        "docType": docType,
                        "compID": compID,
                        "fundID": fundID,
                        "catID": catID,
                        "invID": invID,
                        "approved": approved,
                        "peding": pending,
                        "date": date
                        }
                rec_files = collection.insert_one(file)
                log(0,"Archived '" + filename + "'.")
            else:
                shutil.move(srcfile, errorfile)
                log(1,"Without invID'" + filename + "'.")
                files_with_errors = files_with_errors + 1
    safe_copy(srcfile,ok_folder)

except:
    log(1,"This file could not be processed.'" + filename + "'.")
    shutil.move(srcfile, errorfile)
    files_with_errors = files_with_errors + 1

log(0,"Successfully achieved " + str(files_success) + " files, totalling " + str(round(size,2)) + "MB. files with errors " + str(files_with_errors))
end(0)


