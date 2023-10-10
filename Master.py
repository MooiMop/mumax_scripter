'''
Master.py version 1.0
Author: Naor Scheinowitz
Last edit: april 7, 2021
~~~
The purpose of this script is twofold: (1) easily schedule simulations in mumax3 and (2) analyse the outputted
data. This script combines a number of different scripts that can be found in the 'Scripts' subfolder. The
reason this is so split out is so that other people can more easily add or change individual parts of this
collection of tools.
'''

from Modules import tools
from Modules.MumaxScripter import MumaxScripter
from Modules.DataAnalysis import DataAnalysis

print('\n\
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n\
Hi there! Welcome to mumax scripter. \n\n\n\
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')


if __name__ == '__main__':
    tools.logprint('Running test simulation.')
    test_simulation = MumaxScripter(
        project_folder='Testing',
        name='testsim'
        )
    test_simulation.add_static_field([0,0,1000])
    test_simulation.add_field_sweep('x')
    test_simulation.write_out(overwrite=True)
    succes = test_simulation.run()
    if succes:
        tools.logprint('Yay the simulation works!')
