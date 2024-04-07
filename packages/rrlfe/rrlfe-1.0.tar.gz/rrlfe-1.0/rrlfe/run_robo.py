import os
import glob
import multiprocessing
from multiprocessing import get_context
import logging
from . import *


class RunRobo:
    """
    Enables multiprocessing

    Parameters:
        write_dir (str): directory to write to
        robo_dir (str): directory in which robospect.py lives
    """

    def __init__(self, write_dir, robo_dir):

        self.norm_spec_deposit_dir = write_dir
        self.robo_dir = robo_dir

    def __call__(self, file_name):

        """
        Parameters:
            file_name: the absolute file name of one file to run Robospect on

        Returns:
            (writes files to disk)
        """

        # for applying to synthetic spectra
        logging.info("Running Robospect on "+ file_name + " \n")

        # define string for output base names
        # the below is specific to *smo* files
        file_specific_string = file_name.split("/")[-1]

        # example rSpect command:
        ## python rSpect.py -i 4       ['Run four iterations of the full fitting loop,
        ##                               with noise/continuum/detection/initial line
        ##                               fits/non-linear least squares line fits all
        ##                               happening on each iteration.' --C. Waters]
        ## ./tmp/input_spectrum.dat    [run Robospect on this input spectrum]
        ## -P ./tmp/czw.20190823       [deposit results here, with this file stem]
        ## --line_list /tmp/ll         [use this line list]
        ## -C name null                [consider the continuum fixed at 1]
        ## -D name null                ['Do not detect lines not listed in the line
        ##                               list.' --C. Waters]
        ## -N name boxcar              ['Generate noise estimate from boxcar smoothing.'
        ##                               --C. Waters]
        ## -I range 10.0               ['Set initial line estimate range to +/- 10AA
        ##                               when estimating FWHM value.' --C. Waters]
        ## -F chi_window 20.0          ['Fit chi^2 calculation using windows of
        ##                               +/- 20AA from the line center.' --C. Waters]
        ## -vvvv                       ['Enable all debug messages for all components.'
        ##                               --C. Waters]

        logging.info("Robospect cmd:")
        cmd_string = "python "+ self.robo_dir + "bin/rSpect.py -i 4 " + str(file_name) + \
            " -P " + self.norm_spec_deposit_dir + file_specific_string + \
            " --line_list " + self.robo_dir + "tmp/ll" +" -C name null" + \
            " -D name null" + " -N name boxcar" + " -I range 10.0" + \
            " -F chi_window 20.0 " + "-vvvv"
        logging.info(cmd_string)
        try:
            os.system(cmd_string)
            logging.info("Robospect output files written to " + \
                self.norm_spec_deposit_dir + file_specific_string + "*")
        except:
            logging.error("Failed to carry out cmd " + cmd_string)


class Robo():
    """
    Runs the Robospect EW measurement

    Parameters:
        module_name (str): name of module
        robo_dir_read (str): directory Robospect reads spectra from
        normzed_spec_dir_read (str): directory of normalized spectra
        robo_output_write (str): directory Robospect writes EW info to

    Returns:
        [EW data written to text file]
    """

    def __init__(self,
        module_name,
        robo_dir_read,
        normzed_spec_dir_read,
        robo_output_write):

        self.name = module_name
        self.robo_dir_read = robo_dir_read
        self.normzed_spec_source_dir = normzed_spec_dir_read
        self.robo_output_write = robo_output_write

    def run_step(self, attribs = None):

        # check if write directories exist and are empty
        #make_dir(self.robo_output_write)

        # explicit syntax necessary for Macbook M1
        pool = get_context("fork").Pool(ncpu)

        # note the below file name list collects ALL files in that directory,
        # not just the ones listed in the initial .list file
        file_name_list = glob.glob(self.normzed_spec_source_dir+"*")
        
        # check Robospect input directory exists
        if os.path.isdir(self.normzed_spec_source_dir):
            # check if directory exists
            logging.info('Reading in spectra from '+str(self.normzed_spec_source_dir))
        else:
            logging.warning('Making new directory '+str(self.normzed_spec_source_dir)+ ' which will contain normalized input spectra for Robospec')
            make_dir(self.normzed_spec_source_dir)
        # check Robospect output directory exists
        if os.path.isdir(self.robo_output_write):
            # check if directory exists
            logging.info('Reading in spectra from '+str(self.robo_output_write))
        else:
            logging.warning('Making new directory '+str(self.robo_output_write)+ ' which will contain Robospec output')
            make_dir(self.robo_output_write)

        # Check to see if it is empty (if not, there is data from a previous
        # run that will inadvertently be used later)
        preexisting_file_list = glob.glob(self.robo_output_write + "/*", recursive=False)

        if (len(preexisting_file_list) > 0):
            logging.info("------------------------------")
            logging.info("Directory to receive Robospect output not empty!! Pre-existing files will also be used later")
            logging.info(self.robo_output_write)
            logging.info("------------------------------")

        # run Robospect on normalized spectra in parallel
        # (N.b. Setting the config files allows Robospect to dump files in the right places)

        # check if Robospect binary dir exists
        if os.path.isdir(self.robo_dir_read):
            # check if directory exists
            logging.info('Reading in background binary from '+str(self.robo_dir_read))
        else:
            logging.error('Robospect input directory '+str(self.robo_dir_read)+ ' does not exist! ')
            exit()
       
        run_robospect_instance = RunRobo(write_dir = self.robo_output_write, robo_dir = self.robo_dir_read)
        #if (configuration == "config"):
        #    run_robospect_instance = RunRobo(config_data=configuration)
        #elif (configuration == "config_apply"):
        #    run_robospect_instance = RunRobo(config_data=config_apply)

        # in parallel
        pool.map(run_robospect_instance, file_name_list)

        # serial (testing only)
        #run_robospect_instance(file_name_list[0])

        logging.info("Done with Robospect")
        logging.info("-------------------")
