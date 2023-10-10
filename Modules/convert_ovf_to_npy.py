import Modules.decodeOVF as decodeOVF
import Modules.tools as tools
from tqdm import tqdm
import numpy as np

def convert_ovf_to_npy(files,delete=False):
    '''
    Goal: Convert .ovf files from mumax3 to .npy data files.
    Inputs:
        -files([str]): list of filenames.
        -delete(bool): whether to delete files after making the animation.
    Warning: sometimes this method gets stuck on a specific .ovf file. I could not find a way for the code
    to auto-detect which files would work and which ones to skip. So the only workaround is to delete/move
    ovf files that can't be converted.
    '''
    tools.logprint('Converting ovf files to npy files.'+' Will delete files after.'*delete)

    for i in tqdm(range(len(files))):
        #load data
        file = files[i]

        data,params = decodeOVF.unpackFile(file)

        data[0,0,0,0] = 0 #Mumax saves the value of the first pixel as 1234567, which has to manually be set to 0

        data[:,:,:,[0,1]] = data[:,:,:,[1,0]] #mumax puts mag vectors in order z,x,y
        data[:,:,:,[1,2]] = data[:,:,:,[2,1]] #These two lines re-order the vectors to x,y,z
        #The order of the data arrays is [x,y,z,mvector] = [Nx,Ny,Nz,3]

        np.save(file[:-4],data) # Save np tensor with the same filename as the ovf file.

    if delete: tools.delete(files)
