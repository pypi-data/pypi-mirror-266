'''
Reads in config file and sets some values accordingly
'''

import os
from configparser import ConfigParser, ExtendedInterpolation

# configuration data for reduction
global config_choice
config_choice = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
# config for reduction to find a, b, c, d
config_choice.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_red.ini'))

# config for applying a calibration
'''
config_apply = ConfigParser(interpolation=ExtendedInterpolation())

config_apply.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_apply.ini'))
'''

# set pathnames for important files that are used by different modules
cc_bkgrnd_file_path_abs = str(config_choice["data_dirs"]["DIR_SRC"] + "/bkgrnd.cc")
compiled_bkgrnd_file_path_abs = str(config_choice["data_dirs"]["DIR_BIN"] + "/bkgrnd")


class configInit():
    '''
    Print parameters from the config file to log
    '''

    def __init__(self, module_name):

        self.name = module_name
        #self.objective = "apply_calib"

    def run_step(self):

        logging.info("## Begin pipeline configuration parameters ##")

        logging.info("rrlfe git hash: " + sha)

        '''
        if (objective == "apply_calib"):
            config_choice = config_apply
        elif (objective == "find_calib"):
            config_choice = config_red
        '''

        for each_section in config_choice.sections():
            logging.info("----")
            logging.info("- " + each_section + " -")
            for (each_key, each_val) in config_choice.items(each_section):
                logging.info(each_key + ": " + each_val)

        logging.info("----")
        logging.info("## End pipeline configuration parameters ##")


class makeDirs():
    '''
    Make directories for housing files/info if they don't already exist
    '''

    def __init__(self, module_name):

        self.name = module_name

    def run_step(self):

        logging.info("## Making directories ##")

        # loop over all directory paths we will need
        for vals in config_choice["data_dirs"]:
            abs_path_name = str(config_choice["data_dirs"][vals])
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
