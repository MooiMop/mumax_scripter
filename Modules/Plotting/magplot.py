from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import os
from PIL import Image

def magplot(datafile,zslice=0,cell_size=5.0,B_ext=None,geometry=None,filename=None):
    '''
    Goal: Make a plot of magnetic spins in xy plane of device. The plot consists of two parts:
        - a vector field plot of the xy plane magnetization, handled by plt.quiver()
        - a color image of the z component of the magnetization, handled by plt.imshow()
    Inputs:
        - datafile(str): location of m*.npy or m_full*.npy file. Used to calculate how hight the
            device is and which pixels are directly above and which are around device by checking which pixels
            are (non)zero.
        -zslice(int): slice in the z axis of which to plot.
        -cell_size(float): width of one pixel in nm.
        -B_ext(float): Value of externally applied field. Is put in title of image.
        -mask_image(str): location of png image used as device mask in mumax.
        -filename(str): custom filename.
    '''
    cell_size = float(cell_size) #somehow this doesn't always work automatically so just in case
    data = np.load(datafile)[:,:,zslice]
    original_shape = np.shape(data)
    #Create slicing mask for quiver plot later. This is to make the number of arrows managable.
    #The idea is: roughly 30 arrows in each direction.
    skip = int(np.shape(data)[0]/30)
    slicer = (slice(None,None,skip),slice(None,None,skip))

    norm = np.max(data)
    data = data/norm

    #Select relevant vector components
    mx = data[:,:,0]
    my = data[:,:,1]
    mz = data[:,:,2]

    #Create mask to leave out all points where m=0 (points outside device)
    if geometry != None:
        if __name__ == '__main__':
            print('Setting all spins outside device to zero')
        geometry = '../' + geometry
        shape = np.shape(mx)
        im = np.array(Image.open(geometry).resize((shape[0],shape[1])))
        im = np.swapaxes(im,0,1)
        mask = np.where((np.sum(im,axis=2) == 0),True,False)
    else:
        mask = np.where(np.sum(data,axis=2)==0,True,False)

    mx[mask] = np.nan
    my[mask] = np.nan
    mz[mask] = np.nan

    #Vector field part~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #Trim data
    mx = mx[slicer]
    my = my[slicer]

    #Create grid
    shape = np.shape(mx)
    xx,yy = np.mgrid[0:shape[0],0:shape[1]]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.quiver(xx*cell_size*skip,
        yy*cell_size*skip,
        mx,
        my,
        width=0.015,headwidth=3,headlength=3,headaxislength=3,
        pivot='mid',angles='uv',units='inches',scale=9)

    #OOP color part~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    OOP_part = mz
    OOP_part = np.swapaxes(OOP_part,0,1) #Imshow shows x vertical and y horizontal, hence the transpose
    xmin,xmax = -cell_size/2, cell_size * original_shape[0] - cell_size/2
    ymin,ymax = -cell_size/2, cell_size * original_shape[1] - cell_size/2
    ax.imshow(OOP_part,cmap='bwr',extent=[xmin,xmax,ymin,ymax],origin='lower')

    ax.set_ylim([0-ymax*0.05, ymax*1.05])
    ax.set_xlim([0-xmax*0.05, xmax*1.05])

    if np.shape(B_ext) != ():
        fig.suptitle(r'$B_{ext}$ = ' + str(B_ext) + ' (mT)')

    if filename==None: filename = datafile[:-4]+'.pdf'
    else: filename += '.pdf'
    fig.savefig(filename)
    if __name__ == '__main__':
        plt.show()
    plt.close(fig)

if __name__ == '__main__':
    path = '../../Examples/Sweep Example.out'
    os.chdir(path)

    #Data files
    datafile = 'm_full000022.npy'

    magplot(datafile,zslice=0,cell_size=5.0,filename=None)
