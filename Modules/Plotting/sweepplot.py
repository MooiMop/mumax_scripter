import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

def sweepplot(data,filename=None,subplots=False):
    '''
    Goal: Create a plot of total energy vs applied magnetic field.
    Comment: the difficult part is to detect when a sweep ends and the next one begins.
    Inputs:
        -data: location of datafile from mumax simulation.
        -filename(str): custom filename.
        -subplots(bool): whether to plot every sweep in a different subplot
    '''
    #Load data
    df = pd.read_csv(data,sep='	')
    data_keys = df.keys()
    Bx,By,Bz = df['B_extx (T)'].to_numpy(), df['B_exty (T)'].to_numpy(), df['B_extz (T)'].to_numpy()
    mx,my,mz = df['mx ()'].to_numpy(), df['my ()'].to_numpy(), df['mz ()'].to_numpy()

    #Calculate total energy and fields
    #You might be thinking "why not use the total energy from the table? Why are you calculating it here
    #again?" The reason is: Mumax takes the zeeman energy to be negative, which causes the total energy to be
    #lower than it should be.
    total_field = np.sum([Bx,By,Bz],axis = 0) * 1e3 #convert T to mT
    E_total = np.sum(np.abs([df['E_exch (J)'],df['E_demag (J)'],df['E_Zeeman (J)']]),axis=0)*1e15

    #divide into different sweeps
    print(f'Slicing data into different sweeps...')

    sweeplist = [] #Coordinate list where each new sweep starts. i.e. where does a new sweep start?
    sweepdirections = [''] #In which direction is the new sweep? Empty value added so that [-1] does not return error

    for i in np.arange(1,len(Bx)):
        #Check if two consecutive steps have zero applied field. This happens just when one sweep ended
        #and the next begins.
        new_sweep = np.round(mx[i]+my[i]+mz[i],3) == np.round(mx[i-1]+my[i-1]+mz[i-1],3)
        if new_sweep and total_field[i] == 0:
            i = i + 1
            sweeplist.append(i-1)
            if Bx[i] != 0:
              sweepdirections.append('x')
              print("New x sweep detected at i="+str(i))
            elif By[i] != 0:
              sweepdirections.append('y')
              print("New y sweep detected at i="+str(i))
            elif Bz[i] != 0:
              sweepdirections.append('z')
              print("New z sweep detected at i="+str(i))

        #The following lines check if the direction of the applied field has changed between this step and the
        #previous step
        elif Bx[i] != 0 and sweepdirections[-1] != 'x':
          print("New x sweep detected at i="+str(i))
          sweepdirections.append('x')
          sweeplist.append(i-1)
        elif By[i] != 0 and sweepdirections[-1] != 'y':
          print("New y sweep detected at i="+str(i))
          sweepdirections.append('y')
          sweeplist.append(i-1)
        elif Bz[i] != 0 and sweepdirections[-1] != 'z':
          print("New z sweep detected at i="+str(i))
          sweepdirections.append('z')
          sweeplist.append(i-1)


    sweepdirections = sweepdirections[1:] #Remove first empty entry
    sweeplist.append(len(Bx)-1) #Add index of last element. Makes plotting easier.

    #Plot magnetisation(x-axis) vs total energy (y-axis)
    print(f'Plotting...')

    fig, ax = plt.subplots()
    xwidth = np.min([0.2 * np.sqrt( (len(Bx) / 20) ), 0.5])

    axin1 = ax.inset_axes([0.15, 0.7, xwidth , 0.2])
    for i in range(len(sweepdirections)):
        #Magnetization - Energy plot
        start = sweeplist[i]
        stop = sweeplist[i+1]+1
        ls = (0, (1, 1))
        ax.plot(total_field[start:stop], E_total[start:stop],label=f'{sweepdirections[i]} sweep',alpha=0.6,marker='.')

        #Plot of total magnetization vs simulation steps
        x = np.arange(start,stop,1)
        axin1.plot(x,total_field[start:stop],marker='.')

    #Plot arrows to show path of sweep
    number_of_arrows = int(len(sweepdirections) * 1.5)
    selection = np.linspace(3, len(total_field)-3, number_of_arrows)
    selection = selection.astype(int)

    x = total_field[selection]
    y = E_total[selection]
    dx = total_field[selection + 1] - x
    dy = E_total[selection + 1] - y
    norm = np.sqrt(np.array(dx)**2 + np.array(dy)**2)

    ax.quiver(x,y,dx/norm,dy/norm,angles='xy',headwidth=2)

    #Plot styling
    ax.legend(loc=4)
    ax.set_title('Field sweep energy')
    ax.set_ylabel('Energy (fJ)')
    ax.set_xlabel(r'$B_{ext}$ (mT)')
    axin1.set_ylabel(r'$B_{ext}$ (mT)')
    axin1.set_xlabel('Simulation steps')


    if filename==None: filename = 'sweepplot.pdf'
    else: filename += '.pdf'
    fig.savefig(filename)
    print(f'Figure saved as \'{filename}\'.')
    if __name__ == '__main__':
        plt.show()
    plt.close(fig)

if __name__ == '__main__':
    path = '../../Examples/Sweep Example.out/'
    os.chdir(path)

    datafile = 'table.txt'
    sweepplot(datafile)
