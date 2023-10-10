"""Miscellaneous useful functions."""
import numpy as np
import time
import glob
from PIL import Image
import os

def logprint(string):
    t = time.localtime()
    current_time = time.strftime("%H:%M", t)
    print(f'{current_time}  {str(string)}')
    #time.sleep(1)

def find(pattern):
    ''' find file in current directory with name matching 'pattern' '''
    return sorted(glob.glob(pattern))

def get_resolution(filename):
    img = Image.open(filename)
    x,y = img.size
    return x,y

def delete(files):
    tools.logprint('Deleting files after 30 seconds. Press CTRL+C to cancel.')
    for i in tqdm(range(30)):
        time.sleep(1)

    for file in files:
        try:
            os.remove(file)
        except OSError as error:
            print(error)
            print(f'File {file} cannot be removed.')
    logprint('Done removing files.')

def corruption_check(files):
    for file in files:
        try:
            img = Image.open(file) # open the image file
            img.verify() # verify that it is, in fact an image
        except (IOError, SyntaxError) as e:
            print('Bad file:', file)
            files.remove(file)
    return files

def extract_param(logfile,query,append='',title=None,mode='text'):
    with open (logfile, 'rt') as  file:      #Open log.txt for reading
        for line in file:                    #For each line, read to a string,
            if query in line:
                if 'SetRegion' in line:
                    value = line[ len(query+'.SetRegion(1, ') : -2 ]
                elif ':=' in line:
                    value = line[ len(query) + 4 :-1 ]
                else:
                    value = line[ len(query) + 3 :-1 ]

                if mode == 'text':
                    if title == None:
                        return query + ': ' + value + append
                    else:
                        return title + ': ' + value + append
                if mode == 'value':
                    return value
    return None
