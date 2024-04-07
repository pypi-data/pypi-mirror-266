import subprocess
from subprocess import call
from subprocess import Popen
import shlex
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os, os.path
from os import listdir
from os.path import isfile, join
import pandas as pd
import sys
from pylab import * 
import glob
from IPython.display import clear_output
from astropy.io import fits

class norm_spec:
    # this is a superclass that will be inherited by other classes
    
    def __init__(self, input_file):
        self.smoothing = 22 # smoothing applied by Carrell's normalization code
        self.input_file = input_file
        
    def __call__(self):
        
        # compile Carrell's normalization code
        # (see carrell_readme.txt)

        # Carrell's C code should already be compiled by setup.py. But here are the manual commands for posterity:
        #normzn_compile1 = shlex.split("g++ -o bkgrnd bkgrnd.cc")
        #normzn_compile2 = subprocess.Popen(normzn_compile1) # run
        
        # run the normalization routine on the data
        normzn_run1 = shlex.split("./bkgrnd --smooth "+str(self.smoothing)+" "+self.input_file) # self.input_file can be 'in.data'
        normzn_run2 = subprocess.Popen(normzn_run1, stdout=subprocess.PIPE, stderr=subprocess.PIPE) # run and capture output
                                  
        # make list of all output files put out by Robospect
        dir_name = "test_robo_output/"
        list_output_files = [name for name in os.listdir(dir_name) if os.path.isfile(os.path.join(dir_name, name))]
                                  
        # divide the second column of the output files (empirical) with the third (normalization) 
        header = ['WAVELENGTH', 'FLUX'] # headers of output file that Robospect will use (see Robospect user manual)
        for filenum in range(0,len(list_output_files)):
            df = pd.read_csv(dir_name + str(list_output_files[filenum]), delim_whitespace=True, header=None)
            df['WAVELENGTH'] = df[0]
            df['FLUX'] = np.divide(df[1],df[2]) # normalize
            df.to_csv('test_output_data/output.csv', columns = header, index = False, sep = ' ') # write out file 
            del df



