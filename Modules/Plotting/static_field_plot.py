import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

color_dict = {'x': 'blue', 'y': 'orange', 'z': 'green',
              '-x': 'blue','-y': 'orange', '-z': 'green'}

def region_mask(len,start,end):
    x = np.arange(len)
    return (x>=start) & (x<=end)

def static_field_plot(data,filename=None):
    '''
    Goal: Create a plot with magnetization and energy as function of simulation time.
    The plot consists of three parts:
        - a line subplot of the total magnetization in x,y,z.
        - a line subplot of the system energy.
        - shaded regions (region_mask) to show where fields were applied.
    Inputs:
        -data: location of datafile from mumax simulation.
        -filename(str): custom filename.
    '''
    df = pd.read_csv(data,sep='	')
    data_keys = df.keys()

    #Plot setup
    fig = plt.figure(figsize=(15,10))
    fig.suptitle('Total magnetization and system energy as function of time.')
    mplot = plt.subplot(211)
    Eplot = plt.subplot(212)
    time = df[data_keys[0]]

    if np.sum(time) > 0: #check if simulation saved time information.
        time = time * 1e9 #from s to ns
        xlabel = 'Time (ns)'
    else:
        print('WARNING: Data file does not contain time information! Plot will look ugly.')
        time = np.arange(1,len(time)+1)
        xlabel = 'Simulation steps'

    #magnetization plots
    for key in data_keys[1:3+1]:
        mplot.plot(time,df[key],label=key)

    #Energy plots
    E_total = np.sum(np.abs([df['E_exch (J)'],df['E_demag (J)'],df['E_Zeeman (J)']]),axis=0)
    for key in data_keys[5:7+1]:
        Eplot.plot(time,np.abs(df[key]),label=key)
    Eplot.plot(time,E_total,label=data_keys[4])

    #Add shaded regions that show where external fields were applied
    Bx,By,Bz = df['B_extx (T)'].to_numpy(), df['B_exty (T)'].to_numpy(), df['B_extz (T)'].to_numpy()
    B = np.transpose (np.array((Bx,By,Bz)))
    B_mask = np.sum(B,axis=1) != 0
    max = np.max(B)

    #finding regions where fields are applied and saving the direction
    dirs = ['x','y','z']
    mplot2 = mplot.twinx()
    Eplot2 = Eplot.twinx()
    for i in range(3):
        fill = B[:,i] * 1000 #Go from T to mT
        mask = fill != 0
        for plot in [mplot2,Eplot2]:
            plot.fill_between(time, 0, fill, where=mask,
                    facecolor=color_dict[dirs[i]], alpha=0.2)
            plot.set_ylabel('(Shaded) External field strength (mT)')

    '''#Text box with simulation parameters
    boxtext = '\n'.join((
            self.extract_param('Height','nm'),
            self.extract_param('Diameter','nm'),
            self.extract_param('cell_size','Cell Size','nm'),
            self.extract_param('alpha','Damping (alpha)')
            ))
    try:
        boxtext.append('Number of pixels = ' + str( int(self.extract_param('Nx','')) * int(self.extract_param('Ny','')) * int(self.extract_param('Nz',''))))
    except: None

    boxparams = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    fig.text(0.01, 0.03, boxtext, fontsize=12,bbox=boxparams)'''


    #Align the zero-points of the y-axes of the magnetization plot.
    ax1_ylims = mplot.axes.get_ylim()           # Find y-axis limits set by the plotter
    ax1_yratio = ax1_ylims[0] / ax1_ylims[1]  # Calculate ratio of lowest limit to highest limit

    ax2_ylims = mplot2.axes.get_ylim()           # Find y-axis limits set by the plotter
    ax2_yratio = ax2_ylims[0] / ax2_ylims[1]  # Calculate ratio of lowest limit to highest limit


    # If the plot limits ratio of plot 1 is smaller than plot 2, the first data set has
    # a wider range range than the second data set. Calculate a new low limit for the
    # second data set to obtain a similar ratio to the first data set.
    # Else, do it the other way around

    if ax1_yratio < ax2_yratio:
        mplot2.set_ylim(bottom = ax2_ylims[1]*ax1_yratio)
    else:
        mplot.set_ylim(bottom = ax1_ylims[1]*ax2_yratio)

    Eplot.set_ylim([1e-16,1e-13])
    mplot.set_title('Magnetization')
    Eplot.set_title('Energy')
    mplot.legend(loc=1)
    Eplot.legend(loc=1)

    mplot.set_ylabel('Normalised Magnetization')
    mplot.set_xlabel(xlabel)
    Eplot.set_xlabel(xlabel)
    Eplot.set_ylabel('Energy (J)')
    Eplot.set_yscale('log')

    if filename==None: filename = 'static_field_plot.pdf'
    else: filename += '.pdf'
    fig.savefig(filename)
    print(f'Figure saved as \'{filename}\'.')
    if __name__ == '__main__':
        plt.show()
    plt.close(fig)

if __name__ == '__main__':
    path = '../../Testing/Animation_Example'
    os.chdir(path)

    datafile = 'table.txt'
    static_field_plot(datafile)
