'''
This is the high-level script which runs all the pieces of the pipeline to
obtain updated Layden coefficients [a, b, c, d]
'''

import os
import sys
import collections
from collections import OrderedDict
from configparser import ConfigParser, ExtendedInterpolation

# enable searching of one dir higher
sys.path.append("..")

from rrlfe.conf import *
from rrlfe import *

from rrlfe import (compile_normalization,
                      create_spec_realizations,
                      run_robo,
                      scrape_ew_and_errew,
                      teff_retrieval,
                      find_feh, 
                      final_corrxn,
                      run_emcee)


class GenerateCalib():
    '''
    This actually runs the reduction that generates a calibration
    '''
    def __init__(self):

        # dictionary to contain pipeline steps
        self._dict_steps = collections.OrderedDict()

        # read in choice of configuration data file for reduction;
        # set contents as attributes for sections to follow
        config_choice = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
        # config for reduction
        config_choice.read(os.path.join(os.path.dirname(__file__), 'conf', 'config_gen.ini'))

        self._attribs = config_choice


    def add_step(self, module):
        '''
        Adds module to the list of things to do
        '''

        self._dict_steps.update({module.name:module})


    def run(self):
        '''
        Loop over steps and run, letting each step inherit the attributes
        from the config file
        '''

        for exec_id in self._dict_steps.values():
            exec_id.run_step(attribs = self._attribs)
