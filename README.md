# Search and move file in Python with pattern specific
Python script (Cron). Its funtion to review folder, review pdf files, look for the pattern and move files to the corresponding folder.
Python script (file). Its funtion to review file (arg), review pdf files, look for the pattern and move files to the corresponding folder. 

## Dependencies

pip3 install textract
pip3 install PyPDF2

> Also, check the requirements.txt file for additional requirements.

### Deploy 
The files to transform must be in the folder: /serverfolder/source/

The pattern to search is found in the Line 30 of both files

Example
> 30 pattern_to_search ='Fecha:(.+?) Hora:'          # pattern to search search data between date: and time : .


1) Clone or download the git repository.

2) Add pdf files in the source folder

3) run

python3 searchandmove_cron.py

or

python3 searchandmove_file.py  ./serverfolder/source/XXXXXX.pdf 


```
