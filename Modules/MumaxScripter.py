import numpy as np
import Modules.tools as tools
import os
import time
import platform
import subprocess
import webbrowser

#Physical constants
nm = 1e-9

class MumaxScripter:
    #Useful variables
    source_folder = os.path.dirname(os.path.abspath(__file__)) #Directory of this file
    main_folder = os.path.abspath(os.path.join(source_folder,os.pardir))
    backup_folder = os.path.join(main_folder,'Output')

    def __init__(self,project_folder=None,**kwargs):
        '''
        This function initializes the class by creating variables with all parameters needed to run a
        simulation.
        Parameters that are not given as kwargs but are needed have default values which are for cobalt
        elliptical cylinder of dimensions 800x400x65 nm.
        If 'contacts' is set to True but no mask file has been given through 'custom_mask', then a default
        mask is applied (Masks\Co(h60,d800,cx).png).
        '''
        tools.logprint('\n\nStarting new simulation.\n\n')
        #Set project folder~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if project_folder == None:
            tools.logprint('No project folder defined. Using backup output folder.')
            project_folder = self.backup_folder

        elif not os.path.exists(project_folder):
            tools.logprint('Project folder does not exist. If you are on Windows, make sure to use double backslashes. This is what you gave as input: \n\n' + project_folder+'\n')
            tools.logprint('Using backup output folder.')
            project_folder = self.backup_folder

        try:
            os.chdir(project_folder)
            tools.logprint('Working directory changed to: ' + os.getcwd())
        except OSError:
            tools.logprint("Can't change the current working directory for some reason. Changing to backup folder.")
            project_folder = self.backup_folder
            try:
                os.chdir(project_folder)
                tools.logprint('Working directory changed to: ' + os.getcwd())
            except OSError:
                tools.logprint("Still can't change working directory. Exiting program. Better investigate what's going on!")
                tools.logprint('Exiting.')
                exit()

        #Load simulation parameters~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        default_parameters = {
            'alpha' : 0.5,         #LL-damping
            'exchange_length' : 5, #nm
            'Msat' : 1440e3,       #saturasation magnetisation
            'Aex' : 31e-12,        #exchange stiffness
            'h' : 50,              #Height
            'D' : 1000,            #Diameter of long axis
            'axes_ratio' : 2.0,    #Ratio between long and short axes
            'cell_size' : 5.0,     #"Resolution" of the simulation
            'contacts': False,     #Whether or not to run with contacts
            'stray_fields': False   #Whether to save B_demag files or not. Significantly changes simulation script!
            }

        #Update the parameters by what the user has set as parameter values
        default_parameters.update(kwargs)
        #Convert parameter dictionarty to variables
        for key in default_parameters: self.__setattr__(key, default_parameters[key])

        #Check if this simulation has a name and if not give it default name
        if not hasattr(self, 'name'):
            self.custom_name = False
            self.name = f'Co(h{self.h},d{self.D},contacts,ratio{self.axes_ratio})'
        else: self.custom_name = True
        tools.logprint('Simulation name: ' + self.name)

        #Load contacts~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #Set contacts to true if custom mask is provided
        if hasattr(self, 'custom_mask'): self.contacts = True

        #The purpose of this if-statement is to get the physical size in x and y of the device in nm
        if self.contacts:
            if hasattr(self, 'custom_mask'):
                self.name_maskfile = kwargs['custom_mask']
                x,y = tools.get_resolution(self.name_maskfile)
                tools.logprint('Loaded custom mask file: ' + self.name_maskfile)

            else:
                tools.logprint('No mask file given. Using default mask file.')
                self.name_maskfile = os.path.join(self.main_folder,'Masks','Co(h60,d800,cx).png')

                #Scale standard mask to current parameters
                x,y = tools.get_resolution(self.name_maskfile)
                x = x * self.D / 800
                y = y * self.D / 800 * (2/self.axes_ratio)

            if '\\\\' not in self.name_maskfile:
                self.name_maskfile = self.name_maskfile.replace('\\','\\\\')
        else:
            x,y = self.D,self.D/self.axes_ratio

        #Convert physical sizes to pixels.
        self.Nx = int(round(x / self.cell_size))
        self.Ny = int(round(y / self.cell_size))
        self.Nz = int(round(self.h / self.cell_size))

        tools.logprint('Chosen parameters: \n')
        print('\n'.join("%s: %s" % item for item in default_parameters.items())+'\n')

        if self.Nx*self.Ny*self.Nz > 1e6:
            tools.logprint(f'WARNING: The simulation contains more than a million pixels ({str(self.Nx*self.Ny*self.Nz)}). This will take a while.')


        self.new_config()

    def new_config(self):
        '''
        This function creates a string variable self.mumaxscript, which will contain the entire text for the
        .mx3 file. This is done by appending new lines to the variable. Make sure to only append to this
        variable and not reset it! The only way to reset self.mumaxscript is to call this function.
        '''
        self.mumaxscript = '\n'.join((
        '\n/* Simulation setup */',
        'TableAdd(E_total)',
        'TableAdd(E_exch)',
        'Tableadd(E_demag)',
        'Tableadd(E_zeeman)',
        'TableAdd(maxTorque)',
        'TableAdd(LastErr)',
        'TableAdd(PeakErr)',
        'TableAdd(B_ext)',
        'FixDt = 5e-13',
        'OutputFormat = OVF2_BINARY',
        'EdgeSmooth = 0',
        '\n/* Device properties */',
        f'Height := {self.h}',
        f'Diameter := {self.D}',
        f'Axes_ratio := {self.axes_ratio}',
        f'Nx := {self.Nx}',
        f'Ny := {self.Ny}',
        f'Nz := {self.Nz + int(50/self.cell_size)} //add 100nm of empty space above device' * self.stray_fields,
        f'Nz := {self.Nz}' * (not self.stray_fields),
        'SetGridsize(Nx,Ny,Nz)',
        f'cell_size := {self.cell_size}',
        'nm := 1e-9',
        'SetCellsize(cell_size*nm,cell_size*nm,cell_size*nm)\n'
        '\n/* Geometry */'
        ))
        if self.contacts:
            self.mumaxscript += f'\ngeometry := ImageShape("{self.name_maskfile}")\n'
        else:
            self.mumaxscript += f'\ngeometry := Ellipse({self.D}*nm,{int(self.D/self.axes_ratio)}*nm)\n'

        if self.stray_fields:
            self.mumaxscript += '\n'.join((
            'DefRegion(1,geometry)',
            f'DefRegion(2,Layers({self.Nz+1},{self.Nz + int(50/self.cell_size) + 1})) //empty space',
            '\n/* Physical properties of material */',
            f'Msat.SetRegion(1, {self.Msat}) // saturasation magnetisation',
            f'Aex.SetRegion(1, {self.Aex}) // exchange stiffness',
            f'alpha.SetRegion(1,{self.alpha})',
            '\n/* Starting Condition */',
            'm.setRegion(1,RandomMag()) ',
            'B := 0.0\n'
            ))
        else:
            self.mumaxscript += '\n'.join((
            'SetGeom(geometry)'
            '\n/* Physical properties of material */',
            f'Msat = {self.Msat}// saturasation magnetisation',
            f'Aex = {self.Aex} // exchange stiffness',
            f'alpha = {self.alpha}',
            '\n/* Starting Condition */',
            'm = RandomMag()',
            'B := 0.0\n'
            ))

    def add_static_field(self,field,relax=False,runtime=2.0,autosave=0.05,remove_afterwards=True,snapshots=True):
        '''
        Goal: set a static field until device has relaxed and optionally remove it afterwards.
        Inputs:
            - field[int,int,int]: external field vector with components in mT
            - relax(bool): if true, relax after field is applied. If false, run for time runtime
            - runtime(float): runtime in nanoseconds
            - remove_afterwards(bool): whether to set the field back to [0,0,0] and relax.
            - autosave(float): how often to save data in nanoseconds. 0 means off. disabled if relax==True
            - snapshots(bool): save snapshots of magnetization after every step
        '''

        if len(field) != 3:
            tools.logprint(f'field {field} is not a valid vector.')
            return

        #If you use the relax function in mumax, no time information is saved, making autosave functions
        #useless.
        if autosave != 0.0 and not relax:
            if 'auto_save :=' not in self.mumaxscript:
                self.mumaxscript += '\n'.join((
                f'auto_save := {autosave}e-9',
                'TableAutoSave(auto_save)',
                'AutoSnapshot(m,auto_save)'
                ))

        self.mumaxscript += '\n'.join((
        '\n\n/*Static field */',
        f'B_ext = vector({field[0]}/1000,{field[1]}/1000,{field[2]}/1000)'
        ))

        if relax:
            self.mumaxscript += '\n'.join((
            '\nrelax()',
            'snapshot(m)' * snapshots,
            'save(m_full)',
            'save(B_demag)' * self.stray_fields,
            'tablesave()\n'
            ))
        else:
            self.mumaxscript += '\n'.join((
            f'\nrun({runtime}e-9)',
            'snapshot(m)' * snapshots,
            'save(m_full)',
            'save(B_demag)\n' * self.stray_fields
            ))

        if remove_afterwards:
            self.mumaxscript += '\nB_ext = vector(0,0,0)'

            if relax:
                self.mumaxscript += '\n'.join((
                '\nrelax()',
                'snapshot(m)' * snapshots,
                'save(m_full)',
                'save(B_demag)' * self.stray_fields,
                'tablesave()\n'
                ))
            else:
                self.mumaxscript += '\n'.join((
                f'\nrun({runtime}e-9)',
                'snapshot(m)' * snapshots,
                'save(m_full)',
                'save(B_demag)\n' * self.stray_fields
                ))

    def add_field_sweep(self,sweep_dir,start_mag=None,start=0,end=50,step_size=5,snapshots=True,sweep_back=True,relax_zero=False):
        '''
        Goal: set field sweep from B_ext = start -> B_ext = end
        Inputs:
            - sweep_dir('x','y','z'): direction of external field vector
            - start_mag(None,'x','y','z'): starting magnetization before field sweep. Simulation will set all
                spins in this direction, then relax, then start field sweep
            - start,end,step_size(int,int,int): magnitudes of start & end & field steps in mT
            - snapshots(bool): save snapshots of magnetization after every step
            - sweep_back(bool): whether to sweep back from end to start
            - relax_zero(bool): if true, simulation will 'start over' after every field value. Example: with
                (start,end,step_size)=(0,20,5): B_ext = 5 -> B_ext = 0 -> system reset with start_mag ->
                B_ext = 10 ->  B_ext = 0 -> reset -> etc
              if relax_zero == True, sweep_back is set to False
        '''
        #Set initial magnetization~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        if start_mag != None:
            self.mumaxscript += f'\n/*starting condition: fully magnetized in {start_mag}-direction */\n'
            if start_mag == 'x':
                self.mumaxscript += f'm.SetRegion(1, uniform(1,0,0))\n'
            elif start_mag == 'y':
                self.mumaxscript += f'm.SetRegion(1, uniform(0,1,0))\n'
            elif start_mag == 'z':
                self.mumaxscript += f'm.SetRegion(1, uniform(0,0,1))\n'
            elif start_mag == '-x':
                self.mumaxscript += f'm.SetRegion(1, uniform(-1,0,0))\n'
            elif start_mag == '-y':
                self.mumaxscript += f'm.SetRegion(1, uniform(0,-1,0))\n'
            elif start_mag == '-z':
                self.mumaxscript += f'm.SetRegion(1, uniform(0,0,-1))\n'

            self.mumaxscript += '\n'.join((
            'relax()',
            'snapshot(m)' * snapshots,
            'save(m_full)',
            'save(B_demag)' * self.stray_fields,
            'tablesave()\n'))

        #Set field sweep~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        self.mumaxscript += f'\n/* Field Sweep in {sweep_dir}-direction */\n'

        if end > start:
            sweep_direction = 1
            self.mumaxscript += 'for B='+str(start)+'e-3; B<='+str(end)+'e-3; B+='+str(step_size)+'e-3{'
        elif start > end:
            sweep_direction = -1
            self.mumaxscript += 'for B='+str(start)+'e-3; B>='+str(end)+'e-3; B-='+str(step_size)+'e-3{'

        if sweep_dir == 'x':
            self.mumaxscript += '\n    B_ext = vector(B,0,0)\n'
        elif sweep_dir == 'y':
            self.mumaxscript += '\n    B_ext = vector(0,B,0)\n'
        elif sweep_dir == 'z':
            self.mumaxscript += '\n    B_ext = vector(0,0,B)\n'

        self.mumaxscript += '\n'.join((
        '    relax()',
        '    snapshot(m)'* snapshots,
        '    save(m_full)',
        '    save(B_demag)' * self.stray_fields,
        '    tablesave()\n'
        ))

        if relax_zero:
            self.mumaxscript += '\n'.join((
            '    B_ext = vector(0,0,0)',
            '    relax()',
            '    snapshot(m)'* snapshots,
            '    save(m_full)',
            '    save(B_demag)' * self.stray_fields,
            '    tablesave()',
            '    m = uniform(1,0,0)',
            '    relax()',
            '    snapshot(m)'* snapshots,
            '    save(m_full)',
            '    save(B_demag)' * self.stray_fields,
            '    tablesave()\n'))

        self.mumaxscript += '\n}\n'

        if sweep_back and not relax_zero:
            if end > start:
                sweep_direction = 1
                self.mumaxscript += '\nfor B='+str(step_size)+'e-3; B<='+str(end-start)+'e-3; B+='+str(step_size)+'e-3{'
            elif start > end:
                sweep_direction = -1
                self.mumaxscript += '\nfor B='+str(step_size)+'e-3; B>='+str(end-start)+'e-3; B-='+str(step_size)+'e-3{'

            if sweep_dir == 'x':
                self.mumaxscript += f'\n    B_ext = vector({end}e-3-B,0,0)\n'
            elif sweep_dir == 'y':
                self.mumaxscript += f'\n    B_ext = vector(0,{end}e-3-B,0)\n'
            elif sweep_dir == 'z':
                self.mumaxscript += f'\n    B_ext = vector(0,0,{end}e-3-B)\n'

            self.mumaxscript += '\n'.join((
            '    relax()',
            '    snapshot(m)'* snapshots,
            '    save(m_full)',
            '    save(B_demag)' * self.stray_fields,
            '    tablesave()',
            '}\n'
            ))

    def write_out(self, overwrite=False):
        self.name_mumaxscript = self.name+'.mx3'
        #If the name of this simulation already exists, add number to name so we don't overwrite anything
        if not overwrite and os.path.exists(self.name_mumaxscript):
            i = 2
            while os.path.exists(self.name + str(i) + '.mx3'):
                i+=1
            self.name = self.name + str(i)
            self.name_mumaxscript = self.name+'.mx3'

        mumaxfile = open(self.name_mumaxscript,'w+')
        mumaxfile.write(self.mumaxscript)
        mumaxfile.close()
        tools.logprint(f'File \'{self.name_mumaxscript}\' generated.')

    def run(self,filename=None):
        if filename == None:
            try:
                filename = self.name_mumaxscript
            except AttributeError:
                tools.logprint('No script to run! Exiting.')
                return False

        if platform.system() != 'Windows':
            tools.logprint('This is not Windows! How am I supposed to run this!?')
            return False
        else:
            tools.logprint(f'Starting mumax3 simulation of {self.name_mumaxscript}.')

        start_time = time.time()
        webbrowser.open('http://127.0.0.1:35367', new=0, autoraise=True)
        simulation = subprocess.run(['mumax3',self.name_mumaxscript], capture_output=True, text=True)
        elapsed_time = time.time() - start_time

        if elapsed_time < 30:
            tools.logprint('Simulation took less than 30 seconds. Something probably went wrong. Here is the simulation output.')
            print('Non-error output:\n' + simulation.stdout)
            print('Error output:\n' + simulation.stderr)
            return False
        else:
            tools.logprint('Simulation run succesfully.')
            tools.logprint(f'The simulation took {np.int(np.floor(elapsed_time/3600))} hours, {np.int(np.floor(elapsed_time%3600/60))} minutes, and {np.int(np.floor(elapsed_time%3600%60))} seconds.')
            return True
