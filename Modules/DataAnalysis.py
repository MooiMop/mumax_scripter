import numpy as np
import Modules.tools as tools
import os
import time
import platform
import subprocess
import webbrowser
import glob
import pandas as pd
import matplotlib.pyplot as plt
import imageio
import ffmpy
import Modules.decodeOVF as decodeOVF
from tqdm import tqdm

#import different plots
import Modules.convert_ovf_to_npy as cotn
import Modules.Plotting.static_field_plot as sfp
import Modules.Plotting.sweepplot as sp
import Modules.Plotting.makemovie as mm
import Modules.Plotting.magplot as mp
import Modules.Plotting.flux as flx

class DataAnalysis:
    #Useful variables
    source_folder = os.path.dirname(os.path.realpath(__file__)) #Directory of this file
    main_folder = os.path.join(source_folder,os.pardir)
    backup_folder = os.path.join(main_folder,'Output')

    def __init__(self,data_folder,do_all=True,**kwargs):
        #Set project folder~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        try:
            os.chdir(data_folder)
            tools.logprint('Working directory changed to: ' + os.getcwd())
        except OSError:
            tools.logprint("Can't change working directory to project folder. Exiting program. Better investigate what's going on!")
            tools.logprint('Exiting.')
            exit()

        #Load files
        self.table = os.path.join(data_folder,'table.txt')
        self.log = os.path.join(data_folder,'log.txt')

        self.update_availability()
        if self.params: self.get_params()

        self.print_available_actions()
        #Perform all data analysis steps
        if do_all:
            if self.table_plots:
                try: self.static_field_plot()
                except() as e: print(e)
                try: self.sweepplot()
                except() as e: print(e)
            if self.snapshots:
                try: self.makemovie()
                except() as e: print(e)
            if self.ovf:
                try: self.convert_ovf_to_npy()
                except() as e: print(e)
                self.update_availability()
            if self.mag:
                try: self.magplot()
                except() as e: print(e)

    def print_available_actions(self):
        print('\n'.join((
        '',
        'Able to read simulation parameters:    ' +  (not self.params) * 'un' + 'available',
        'convert_ovf_to_npy:                    ' +  (not self.ovf) * 'un' + 'available',
        'static_field_plot:                     ' +  (not self.table_plots) * 'un' + 'available',
        'sweepplot:                             ' +  (not self.table_plots) * 'un' + 'available',
        'magplot:                               ' +  (not self.mag) * 'un' + 'available',
        'snapshot_animation:                    ' +  (not self.snapshots) * 'un' + 'available',
        'fluxplot:                              ' +  (not self.demag) * 'un' + 'available, but needs to be called manually. Please see the documentation.',
        ''
        )))

    def update_availability(self):
        #Make list of available files and thus available functions.
        if os.path.exists(self.log):
            self.params  = True
        else:
            self.params = False

        if os.path.exists(self.table):
            self.table_plots  = True
        else:
            self.table_plots = False

        if len(tools.find('m*jpg')) > 20:
            self.snapshots = True
        else: self.snapshots = False

        if len(tools.find('*ovf')) > 0:
            self.ovf = True
        else:
            self.ovf = False

        if len(tools.find('m*npy')) > 0:
            self.mag = True
            self.ovf = False
        else:
            self.mag = False

        if len(tools.find('B_demag*npy')) > 0:
            self.demag = True
        else:
            self.demag = False

    def get_params(self):
        tools.logprint('Trying to read parameters from log file.')

        interesting_params = [
            ['Height','value'],
            ['Diameter','value'],
            ['Axes_ratio','value'],
            ['cell_size','value'],
            ['alpha','value'],
            ['geometry','text']
        ]

        parameters = {}
        for i in range(len(interesting_params)):
            parameters[interesting_params[i][0]] = self.extract_param(
                interesting_params[i][0],
                mode = interesting_params[i][1])

        tools.logprint('Found the following paramter values:\n'+str(parameters))

        #Convert parameter dictionarty to variables
        for key in parameters:
            if parameters[key] != None:
                self.__setattr__(key, parameters[key])

    def extract_param(self,query,append='',title=None,mode='value'):
        with open (self.log, 'rt') as  file:      #Open log.txt for reading
            for line in file:                     #For each line, read to a string,
                if query in line:
                    if 'SetRegion' in line:
                        value = line[ len(query+'.SetRegion(1, ') : -2 ]
                    elif '(' in line:
                        value = line[ line.find( '(' ) + 2 : line.find( ')' ) -1 ]
                    elif ':=' in line:
                        value = line[ len(query) + 4 :-1 ]
                    else:
                        value = line[ len(query) + 3 :-1 ]

                    if mode == 'text':
                        '''if title == None:
                            return query + ': ' + value + append
                        else:
                            return title + ': ' + value + append'''
                        return str(value)
                    if mode == 'value':
                        return float(value)
        if mode == 'text':
            return ''
        if mode == 'value':
            return None

    def convert_ovf_to_npy(self,**kwargs):
        tools.logprint('Finding .ovf files to convert.')
        files = tools.find('*.ovf')
        if files == []:
            tools.logprint(f'No .ovf files found.')
        else:
            tools.logprint(f'{len(files)} .ovf files found.')
            cotn.convert_ovf_to_npy(files,**kwargs)
            self.mag=True

    def static_field_plot(self,**kwargs):
        tools.logprint('Making static field plot.....')
        sfp.static_field_plot(self.table,**kwargs)

    def sweepplot(self,**kwargs):
        tools.logprint('Plotting magnetization and energy figures.')
        sp.sweepplot(self.table,**kwargs)

    def magplot(self, **kwargs):
        tools.logprint('Plotting magnetic spins for all files in folder.')

        #Get list of magnetic-spin data files
        datafiles = tools.find('m_full*.npy')

        if datafiles == []:
            datafiles = tools.find('m*.npy')

        if datafiles == []:
            tools.logprint(f'No data files found.')
        else:
            tools.logprint(f'{len(datafiles)} files found. Starting image creation.')

            if self.table:#Get list of external field values
                df = pd.read_csv(self.table,sep='	')
                B = np.array([df['B_extx (T)'].to_numpy(), df['B_exty (T)'].to_numpy(), df['B_extz (T)'].to_numpy()])
                B = np.rint( np.transpose(B * 1000) ).astype('int')

            try:
                self.zslice = int(self.Height/self.cell_size/2)
            except:
                None

            for i in tqdm(range(len(datafiles))):
                #Collect variables needed for magplot function
                relevant_variables = {'zslice','cell_size','B_ext','geometry','filename'}
                input = {}
                if self.table:
                    input['B_ext'] = B[i]
                input.update((k, v) for k, v in self.__dict__.items() if k in relevant_variables)
                input.update((k, v) for k, v in kwargs.items() if k in relevant_variables)

                mp.magplot(datafiles[i], **input)


    def makemovie(self,query='m*.jpg',**kwargs):
        tools.logprint('Finding images for movie.')
        images = tools.find(query)

        if images == []:
            tools.logprint(f'No images found with query \'{query}\'')
        else:
            tools.logprint(f'{len(images)} images found. Starting movie creation.')
            mm.makemovie(images,**kwargs)

    def flux(self,**kwargs):
        reference_file = tools.find('m_full*.npy')[1]
        tools.logprint('Plotting stray fields.')
        if hasattr(self, 'cell_size'):
            flx.flux(magfile=reference_file,cell_size=self.cell_size,**kwargs)
        else:
            flx.flux(magfile=reference_file,**kwargs)
