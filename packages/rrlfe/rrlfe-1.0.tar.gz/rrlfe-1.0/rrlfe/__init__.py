'''
Initialization
'''

import os
import git
import sys
import multiprocessing
import logging
from setuptools import Distribution
from setuptools.command.install import install
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation
import subprocess

# get pipeline hash
# warning: may throw error on cluster
'''
def get_git_hash():
    try:
        git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
        return git_hash
    except:
        return None

# get pipeline hash
sha = get_git_hash()
'''

# set up logging, to print to screen and save to file simultaneously
time_start = datetime.now()
timestring_human = str(time_start)
timestring_start = time_start.strftime("%Y%m%d_%H%M%S")
log_filename = timestring_start + ".log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler(sys.stdout)
    ]
)


# number of cores to use
#ncpu = multiprocessing.cpu_count()
ncpu = 3

# prompt user if files will be overwritten? (turn to false if running on HPC)
prompt_user = False

# configuration data for reduction
config_gen = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
# config for reduction to find a, b, c, d
config_gen.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_gen.ini'))

# set some constants

# vestigial constant in MCMC (this is NOT an astrophysical Teff)
Teff = 0.0586758
# coefficients from first line of Table 8 in Layden+ 1994
# (reddening not included), to serve as MCMC starting point
a_layden = 13.542
b_layden = -1.072
c_layden = 3.971
d_layden = -0.271


# The class OnlyGetScriptPath() and function get_setuptools_script_dir()
# are from the setup.py script in the Apogee repository by jobovy
# https://github.com/jobovy/apogee/blob/master/setup.py

class OnlyGetScriptPath(install):
    def run(self):
        self.distribution.install_scripts = self.install_scripts

def get_setuptools_script_dir():
    '''
    Get the directory setuptools installs scripts to for current python
    '''
    dist = Distribution({'cmdclass': {'install': OnlyGetScriptPath}})
    dist.dry_run = True  # not sure if necessary
    dist.parse_config_files()
    command = dist.get_command_obj('install')
    command.ensure_finalized()
    command.run()
    return dist.install_scripts


class MakeDirsConfig():
    '''
    Make directories listed in the config file for housing files/info if they don't already exist
    '''

    def __init__(self, module_name):

        self.name = module_name

    def run_step(self, attribs = None):

        logging.info("## Making directories ##")

        # make directories for
        # 1. reduction of spectra to find a, b, c, d (objective = "find_calib"), or
        # 2. to apply the solution (objective = "apply_calib"; default)

        # loop over all directory paths we will need
        try: 
            for vals in attribs["data_dirs"]:
                abs_path_name = str(attribs["data_dirs"][vals])
                logging.info("Directory exists: " + abs_path_name)

                # if directory does not exist, create it
                if not os.path.exists(abs_path_name):
                    original_umask = os.umask(0) # original system permission
                    os.makedirs(abs_path_name, 0o777)
                    #os.mkdir(abs_path_name)
                    logging.info("Made directory " + abs_path_name)
                    os.umask(original_umask) # revert to previous permission status

                # if it does exist, check if it is not already empty;
                # if it is non-empty, prompt user (as long as prompt_user
                # flag has been set further above)
                # (this needs to be refined, since some directories are not supposed to be empty)
                if prompt_user and os.path.exists(abs_path_name):
                    with os.scandir(abs_path_name) as list_of_entries1:
                        counter1 = 0
                        for entry1 in list_of_entries1:
                            if entry1.is_file():
                                counter1 += 1
                    if (counter1 != 0):
                        logging.info("------------------------------")
                        logging.info(abs_path_name)
                        print("The above is a non-empty directory. Do you want to proceed? [Yes]")
                        print("(N.b. You will be prompted again when the directory is written to.)")
                        input()
                        logging.info("------------------------------")
            status_success = True
        
        except:
            logging.error("Error in making directories!")
            status_success = False
        
        return status_success


def make_dir(abs_path_name_gen):
    '''
    Make directory listed in the argument if it doesn't already exist
    (similar to class MakeDirsConfig, but for single given pathnames)

    INPUTS:
    abs_path_name_gen: the absolute path; could be file name or directory [string]
    '''

    # if it's a file name, get the parent directory
    abs_path_name = os.path.dirname(abs_path_name_gen)

    # if directory does not exist, create it
    if not os.path.exists(abs_path_name):
        original_umask = os.umask(0) # original system permission
        os.makedirs(abs_path_name, 0o777)
        #os.mkdir(abs_path_name)
        logging.info("Made directory " + abs_path_name)
        os.umask(original_umask) # revert to previous permission status
    else:
        logging.info("Directory exists: " + abs_path_name)

    # if it does exist, check if it is not already empty;
    # if it is non-empty, prompt user (as long as prompt_user
    # flag has been set further above)
    # (this needs to be refined, since some directories are not supposed to be empty)
    '''
    if prompt_user and os.path.exists(abs_path_name):
        with os.scandir(abs_path_name) as list_of_entries1:
            counter1 = 0
            for entry1 in list_of_entries1:
                if entry1.is_file():
                    counter1 += 1
        if (counter1 != 0):
            logging.info("------------------------------")
            logging.info(abs_path_name)
            print("The above is a non-empty directory. Do you want to proceed? [Yes]")
            # handle EOFError in case this is being run in a unit test
            try:
                input()
            except EOFError as e:
                print('')
            logging.info("------------------------------")
    '''
    return

'''
def get_hash():
    # Retrieve git hash

    # warning: may throw error on cluster
    repo = git.Repo(search_parent_directories=True)
    sha = repo.head.object.hexsha

    return sha
'''

class ConfigInit():
    '''
    Print parameters from the config file to log
    '''

    def __init__(self, module_name):

        self.name = module_name

    def run_step(self, attribs = None):

        try: 
            logging.info("## Begin pipeline configuration parameters ##")

            #logging.info("rrlfe git hash: " + sha)
            print(attribs.sections)

            for each_section in attribs.sections():
                logging.info("----")
                logging.info("- " + each_section + " -")
                for (each_key, each_val) in attribs.items(each_section):
                    logging.info(each_key + ": " + each_val)

            logging.info("----")
            logging.info("## End pipeline configuration parameters ##")
            status_success = True
        
        except:
            logging.error("Error in making directories!")
            status_success = False

        return status_success


'''
def phase_regions():
    # Read in the boundary between good and bad phase regions (obsolete)

    # obtain values as floats
    value1 = config_gen.getfloat("phase", "MIN_GOOD")
    value2 = config_gen.getfloat("phase", "MAX_GOOD")

    return value1, value2
'''
