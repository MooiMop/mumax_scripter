from Master import *
import os
import numpy as np

os.chdir('Examples')
path = os.path.abspath(os.getcwd())
custom_mask = 'd1500ratio2_DecoupledContactsV2.png'

animation_example = MumaxScripter(
    project_folder=original_path,
    name='Animation Example',
    h = 50,
    D = 800,
    axes_ratio = 2.0,
    cell_size = 5.0,
    contacts = False,
    stray_fields = False
    )
animation_example.add_static_field([1000,0,0],runtime=0.25)
animation_example.add_static_field([0,100,0],runtime=5.0,remove_afterwards=True)
animation_example.add_static_field([100,0,0],runtime=5.0,remove_afterwards=True)
animation_example.write_out(overwrite=False)
animation_example.run()

sweep_example = MumaxScripter(
    project_folder=original_path,
    name='Two-state switch with smaller cell size',
    h = 50,
    D = 800,
    axes_ratio = 2.0,
    cell_size = 5.0,
    custom_mask = custom_mask,
    stray_fields = True
    )
sweep_example.add_field_sweep('y',start_mag='x',start=0,end=100,step_size=10,sweep_back=True)
sweep_example.add_field_sweep('x',start=0,end=100,step_size=10,sweep_back=True)
sweep_example.write_out(overwrite=False)
sweep_example.run()

new_path = os.path.join(path,animation_example.name+'.out')
data = DataAnalysis(data_folder=new_path,do_all=True)

new_path = os.path.join(path,sweep_example.name+'.out')
data = DataAnalysis(data_folder=new_path,do_all=True)


strayfile = {'Zero Vortex':  'B_demag000000.npy',
             'Two Vortex':   'B_demag000025.npy'}

data.flux(strayfile=strayfile,device_start_x=100,trench_location=220,mask_image=custom_mask)
