import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import os
from PIL import Image

def flux(magfile,strayfile,device_height=None,device_start_x=0,cell_size=5.0,trench_width=15,
    penetration_depth=150,mask_image=None,trench_location=None,filename=None):
    '''
    Goal: Make a plot of out-of-plane stray field magnitude directly above ferromagnetic device.
    Inputs:
        - magfile(str): location of m*.npy or m_full*.npy (better) file. Used to calculate how hight the
            device is and which pixels are directly above and which are around device by checking which pixels
            are (non)zero.
            if you only have normalized data files (m*.npy), make sure to set mask_image and and device_height
            manually, as mumax sets nonzero spin values for pixels outside your magnetic device :(
            If you do have a m_full*.npy file, you can set device_height and mask_image to None without
            impacting the result.
        -strayfile(str:str): library of B_demag*.npy files that you want in your plot. Format is a library
            with "state":"filename". State strings will be used as labels in the plot.
        -device_height(int): number of pixels that the device occupies.
        -device_start_x(int): number of pixels from the left that are not really part of the device, but of
        contacts.
        -cell_size(float): width of one pixel in nm.
        -trench_width(float): physical width of the trench in nm.
        -penetration_depth(float): penetration depth of material in nm.
        -mask_image(str): location of png image used as device mask in mumax.
        -trench_location(float): highlighted trench position in nm.
        -filename(str): custom filename.
    '''

    if ('m_full' not in magfile) and mask_image==None:
        print("*******WARNING********\nUsing normalized magnetic spins without mask_image. \nBecause of mumax3 fuckery, this means I can\'t calculate over which pixels to integrate the stray field. Either use mask_image=[file.png] or a m_full*.npy file.")
        return

    colors = {'Zero Vortex':  'orangered',
              'Two Vortex':   'royalblue'}

    total_trench_width = trench_width + 2 * penetration_depth

    #Infer proportions of device of reference mag file.
    mag = np.load(magfile)
    shape = np.shape(mag)

    plot_start = - 20 * cell_size
    plot_end = (shape[0] - 2 * device_start_x + 20)  * cell_size

    if ('m_full' not in magfile) and device_height==None:
        print("*******WARNING********\nUsing normalized magnetic spins. \nBecause of mumax3 fuckery, this means I can\'t calculate how high the magnetic device is. Either use a m_full*.npy file or set device_height=[int] (pixels) manually.")
        return
    elif device_height!=None:
        interface = device_height + 1
    else:
        #Go to the middle in xy and check where is de first occurence in de z-direction of the spin becoming
        #zero. This is the first pixel-row above the device (i.e. where you want to know the B_demag field.)
        interface = np.argmin( np.abs( mag[ int(shape[0]/2), int(shape[1]/2), :, 2] ) )#in pixels

    #Create mask to leave out all points where m=0 (points outside device in xy plane)
    if mask_image != None:
        mask_image = '../' + mask_image
        im = np.array(Image.open(mask_image).resize((shape[0],shape[1])))
        im = np.swapaxes(im,0,1)
        mask = np.where((np.sum(im,axis=2) != 0),True,False)
    else:
        mask = np.where(np.sum(mag[:,:,interface-1],axis=2)!=0,True,False)

    #Calculation and plotting ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    extraticks = []
    max = 0
    for state in strayfile.keys():
        stray = np.load(strayfile[state])[:,:,interface,2]

        field = [] #List of Demag_field in trenches
        domain = [] #List of centers of trenches

        for x in range(shape[0]): #integrate along x
            #Convert physical units to pixels
            trench_begin = x - int(np.ceil(total_trench_width/2/cell_size))
            trench_end = x + int(np.ceil(total_trench_width/2/cell_size)) + 1

            if trench_begin < 0:
                continue
            if trench_end > shape[0]:
                break

            #Select slice of data that is exactly in the junction area.
            slice = stray[trench_begin:trench_end,:] [mask[trench_begin:trench_end]]

            flux = np.sum(slice)
            field_area = np.sum(mask[trench_begin:trench_end])

            field.append(flux/field_area*1000) #*1000 to go from Tesla to mT
            domain.append((x-device_start_x) * cell_size)

        max = np.max([max, np.max(field)])
        plt.plot(domain,field,label=state,c=colors[state])

        #if trench_location != None:
            #trench_loc = np.argmin( np.abs( np.array(domain) - trench_location ) )
            #print(f'Field shift at trench location in the {state} state: {field[trench_loc]} mT.')
            #extraticks.append( int( field[trench_loc] ) )
            #plt.plot([plot_start,domain[trench_loc]],[field[trench_loc],field[trench_loc]], color=colors[state], ls='--')


    if trench_location != None:
        plt.axvline(trench_location,color='black',ls='--',label = 'Approx. Trench Location')

    plt.xlim(plot_start, plot_end) #Cut off fields from contacts
    plt.ylim(-max*1.1, max*1.1)
    plt.xlabel('Trench position on device (nm)')
    plt.ylabel('Change in magnetic field (mT)')
    plt.legend()

    #ticks = [-200,-100,100,200]+ extraticks
    #plt.yticks(ticks)

    #plt.gca().get_yticklabels()[4].set_color("orangered")
    #plt.gca().get_yticklabels()[5].set_color("royalblue")


    plt.title('Demagnetizing field in junction area')

    if filename==None: filename = 'flux.pdf'
    else: filename += '.pdf'
    plt.savefig(filename)
    if __name__ == '__main__':
        plt.show()
    plt.clf()

if __name__ == '__main__':
    path = '../../Examples/Sweep Example.out'
    os.chdir(path)

    #Data files
    magfile = 'm_full000002.npy'
    strayfile = {'Zero Vortex':  'B_demag000001.npy',
                 'Two Vortex':   'B_demag000025.npy'}

    #mask_image = '../d1500ratio2_DecoupledContactsV2.png'
    mask_image = None

    flux(magfile,strayfile,
        device_start_x=100,
        cell_size=5.0,
        trench_width=15,
        #penetration_depth=150,
        penetration_depth=0,
        mask_image=mask_image,
        trench_location=220,
        filename=None)
