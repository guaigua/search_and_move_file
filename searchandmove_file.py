    #!/usr/bin/env python

"""
Info Program Search and move for file
Example:
python3 searchandmove_file.py PDF\ all.pdf dataofdocType dataofcompID dataoffundID dataofcatID dataofapproved dataofpending
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
client = MongoClient(os.environ['dev_dbConnection'])
# start editable vars
original_folder = "./serverfolder/source/"    	# folder to move files from
pdf_folder = "./"                               # pdf files from
new_folder = "./serverfolder/destination/"      # folder to move files to

if not path.isdir(original_folder):
    #Folder does not exist
    try:
        #Create folder
        os.mkdir(original_folder)

    except OSError:
        print ('Error Create Folder')

if not path.isdir(new_folder):
    #Folder does not exist
    try:
        #Create folder
        os.mkdir(new_folder)

    except OSError:
        print ('Error Create Folder')


files_success = 0                               # count files
files_with_errors = 0							# count files with errors
size = 0.0                                      # size
pattern_to_search ='000 (.+?) Avenue'           # pattern to search is invID
dst = None
invID = ''										# invID is empty
date = datetime.today()                         # date
upload = False                                  # Upload set False
error = 0
filename = os.path.basename(sys.argv[1])
docType = os.path.basename(sys.argv[2])
compID = os.path.basename(sys.argv[3])
fundID = os.path.basename(sys.argv[4])
catID = os.path.basename(sys.argv[5])
approved = os.path.basename(sys.argv[6])
pending = os.path.basename(sys.argv[7])
# end editable vars

# start function definitions

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
    #shutil.copy(file_path, out_dir)

    name = dst or os.path.basename(file_path)

    file_path2 = os.path.join(out_dir, file_path)
    if os.path.isfile(file_path2):
        base, extension = os.path.splitext(name)
        f = 1
        while os.path.exists(os.path.join(out_dir, '{}_{}{}'.format(base, f, extension))):
            f += 1
        shutil.move(file_path, os.path.join(out_dir, '{}_{}{}'.format(base, f, extension)))
        f = 1
    else:
        shutil.move(file_path, out_dir)


def error_log(filename, upload, errormsg):
    #Write log
    #Connect to db
    db = client.iportalDevDB19
    #Connect to collection
    collection = db.uploadlog
    error = {
                        "filename": filename,
                        "upload": upload,
                        "error": errormsg,
                        "date": date
    }
    collection.insert_one(error)
    # end function definitions

# start process #

folder=os.path.splitext(filename)[0]
# joins
srcfile = os.path.join(original_folder, filename)

# Try file existe?
try:
    filepath = os.stat(srcfile)
except:
    upload=False
    errormsg= "file does not exist"
    error_log(filename,upload,errormsg)
    sys.exit()

with open(srcfile, "rb") as f:
    pdf = PdfFileReader(f)
    #Try bookmarks without child
    try:
        bookmarks = pdf.getOutlines()
    except:
        upload=False
        errormsg= "this file contains bookmarks with child"
        error_log(filename,upload,errormsg)
        sys.exit()
    #Read Bookmarks
    if bookmarks:
        for b in bookmarks:
            invID = b['/Title']
            if len(invID) < 22 and re.match('\w',invID):
                i = pdf.getDestinationPageNumber(b)
                #Search InvID in database
                #Connect to db
                db = client.iportalDevDB19
                #Connect to collection
                collection = db.investors
                rinvID = ''
                for x in collection.find({ "invID":  invID }):
                    rinvID=  str(x['_id'])
                if rinvID:
                    named = os.path.join(new_folder,rinvID)
                    if not path.isdir(named):
                        #Folder does not exist
                        try:
                            #Create folder
                            os.mkdir(named)

                        except OSError:
                            error = error + 1
                            upload=False
                            errormsg= "Creation of the directory %s failed" % named
                            error_log(filename,upload,errormsg)
                    else:
                        #Folder exist
                        print ("Folder exist %s " % named)
                else:
                    error=error + 1
            else:
                error=error + 1
                errormsg= "bookmark is higher 21 or it's not alphanumeric"
            #Split pdf
            output = PdfFileWriter()
            output.addPage(pdf.getPage(i))
            with open(filename, "wb") as outputStream:
                output.write(outputStream)

            if rinvID:
                pdffile = os.path.join(pdf_folder, filename)
                destfile = os.path.join(named, filename)
                renamefile = os.path.join(named, filename)
                safe_copy(pdffile,named)
                #Connect to collection
                collection = db.files
                file = {
                        "filename": filename,
                        "docType": docType,
                        "compID": compID,
                        "fundID": fundID,
                        "catID": catID,
                        "invID": rinvID,
                        "approved": approved,
                        "peding": pending,
                        "date": date
                        }
                rec_files = collection.insert_one(file)
                errormsg= "None"
                upload=True
                error_log(filename,upload,errormsg)
            else:
                error = error + 1
                upload=False
                errormsg= "invID = "+ invID +" do not exist in database"
                error_log(filename,upload,errormsg)
        if error > 0:
            sys.exit()
    else:
        upload=False
        errormsg= "Bookmarks do not exist"
        error_log(filename,upload,errormsg)
        sys.exit()
