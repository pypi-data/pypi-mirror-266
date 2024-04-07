#!/usr/bin/python

# -----------------------------
# Standard library dependencies
# -----------------------------
import argparse
import os
import glob
from subprocess import Popen, PIPE
# -------------------
# Third-party imports
# -------------------
from astropy.io import fits
from astropy.table import Table
import sys
import numpy as np
import pandas as pd
from pathlib import *

current_dir = os.path.dirname(__file__)

from . import *

# --------------------
# Function Definitions
# --------------------
def create_norm_spec(name_list,
                     normdir,
                     finaldir):
    """
    Create final normalized spectra, using the output from the bkgrnd routine (which
    puts out wavelength, flux, and continuum flux, but not the actual normalized flux)

    Parameters:
        name_list (list): list of realization file names (no path info); should have 3 cols
        normdir (str): directory where files in name_list are located
        finaldir (str): final directory for files which have completed the full
            normalization process; these will have 3 cols too
    Returns:
       list of final file names
    """

    logging.info("Creating normalized spectra")

    new_name_list = list()

    for spec in name_list: # loop through spectrum realizations

        # spectrum realization file name (as output by bkgrnd), with relative path info
        spec_name = os.path.join(normdir, spec)

        # astropy table containing a spectrum's 1.) wavelength, 2.) flux, 3.) background flux
        spec_tab = read_bkgrnd_spec(spec_name)
        # output file name of final, normalized spectrum, with relative path info
        new_name = os.path.join(finaldir, spec) # vestigial, from adding .smo to help Robospect pick it out
        # add to list
        new_name_list.append(new_name)

        try:
            # open file to write normalized spectrum to
            outfile = open(new_name, 'w')
        except IOError:  # pragma: no cover
            logging.info("File {} could not be opened!".format(new_name))
        for j in range(len(spec_tab['wavelength'])):
            # do the division to normalize and write out
            outfile.write("{} {:.4f}\n".format(spec_tab['wavelength'][j],
                                               spec_tab['flux'][j]/spec_tab['bckgrnd_flux'][j]))

        outfile.close()

    return(new_name_list)

def calc_noise(noise_level, spectrum_df):
    """
    Generate noise spectrum

    Parameters:
        noise_level (str/float): define noise level \n
            "file": from file \n
            "None": no noise \n
            (float): level of relative noise to use
        spectrum_df (pandas dataframe): spectrum file; if noise is being read in from file, or is 
            being calculated from the flux, those must be in this file, in cols as follows: \n
            [0]: wavelength [angstr] \n
            [1]: flux \n
            [2]: background flux \n

    Returns:
        Numpy array of noise spectrum
    """

    if (noise_level == "file"):
        # add Gaussian error to the empirical flux, taking sigma to be the
        # 'error' column in an input file; note this is an ABSOLUTE error
        noise_to_add = np.random.standard_normal(len(spectrum_df))*spectrum_df["error"]
        logging.info("Injecting Gaussian noise based on error column in file.")
    elif (noise_level == "None"):
        # don't inject noise at all (note this doesn't make sense if multiple spectra are being realized)
        noise_to_add = 0
        logging.info("Injecting no noise at all")
    else:
        # noise is a set value, representing a Gaussian sigma; this is normalized,
        # so a '0.01' means 'Gaussian-distributed random number with sigma=0.01*flux_input';
        # note this 0.01 is a RELATIVE error
        noise_to_add = np.random.standard_normal(len(spectrum_df))*noise_level*spectrum_df["flux"]
        logging.info("Injecting "+str(noise_level)+" of Gaussian noise.")

    return noise_to_add


def generate_realizations(spec_name, 
                          outdir, 
                          spec_file_format, 
                          num, 
                          noise_level):
    '''
    Calculates a number of realizations of a given spectrum using Gaussian error bars

    Parameters:
        spec_name (str): the spectrum filename
        outdir (str): the working directory
        spec_file_format (str): the format of the input spectra ["fits", "ascii.no_header"]
        num (int): number of realizations to generate
        noise (str/float): 'None': add no noise; 'file': take Gaussian samples of error with spread based on the error column in file
    Returns:
       list of filenames for the realization spectra.
    '''

    logging.info("Generating spectrum realizations of " + spec_name)

    # astropy table containing an empirical spectrum's 1.) wavelength, 2.) flux, 3.) error
    # and the header of the source FITS file
    spec_tab, hdr = read_spec(spec_name, format=spec_file_format)

    basename = os.path.basename(spec_name) # shave off path stem

    # check if directory to write to exists
    if os.path.isdir(outdir):
        logging.info('Writing realizations of input spectra to '+str(outdir))
    else:
        logging.warning('Making new directory '+str(outdir)+ ' which is supposed to contain written out spectrum realizations')
        make_dir(outdir)

    # generate realizations
    new_basename_list = list()

    for i in range(num):

        # make file names

        # basename of spectrum realization, ascii
        new_prefix_ascii = "{}_{:03d}".format(basename.split(".")[-2], i)
        suffix_ascii = basename.split(".")[-1] # could be .dat, .csv, .txt, etc.
        new_basename_ascii = new_prefix_ascii + "." + suffix_ascii
        # if we want to change to FITS intermediary files:
        new_basename_fits = "{}_{:03d}".format(basename.split(".fits")[0], i) + ".fits"
        # don't need path info in spec_name list; add ascii name here
        new_basename_list.append(new_basename_ascii)

        # name of spectrum realization, with path
        new_name_ascii = os.path.join(outdir, new_basename_ascii)
        new_name_fits = os.path.join(outdir, new_basename_fits)

        noise_to_add = calc_noise(noise_level=noise_level, spectrum_df=spec_tab)

        # add the noise
        new_flux = noise_to_add + spec_tab['flux']

        try:
            outfile = open(new_name_ascii, 'w')
        except IOError: # pragma: no cover
            logging.info("File {} could not be opened!".format(new_name_ascii))

        # write out new realization of file in ascii, so bkgrnd can read it in
        logging.info("Writing out ascii realization file " + new_name_ascii + \
            " with noise level stdev " + str(np.std(noise_to_add)))
        for j in range(len(new_flux)):
            outfile.write("{} {:.2f}\n".format(spec_tab['wavelength'][j], new_flux[j]))
        outfile.close()

    return(new_basename_list)

def read_bkgrnd_spec(spec_name):
    """
    Reads in ascii spectra created by bckgrnd and returns numpy arrays of wavelength, flux, bckgrnd_flux

    Arguments:
        spec_name (str): The spectrum filename. If ascii file, should have 3 columns: \n
            [0]: wavelength [angstr] \n
            [1]: flux \n
            [2]: background flux \n
    Returns:
       numpy table with three columns: wavelength, flux, background flux
    """

    logging.info("Reading ascii spectrum realization and background in " + spec_name)
    
    spec_tab = Table.read(spec_name, format='ascii.no_header',
                          names=['wavelength', 'flux', 'bckgrnd_flux'])

    return(spec_tab)


def read_list(input_list):
    """
    Read in list of spectrum names and returns a table of filenamse

    Arguments:
        input_list (str): file name of a csv file with columns \n
            [0]: filename \n
            [1]: subtype (RRab, RRc) \n
            [2]: phase (0. to 1., -9999 for NaN) \n
            [3]: metallicity (if producing the calibration) \n
            [4]: error in metallicity (if producing the calibration)
    Returns:
       numpy array of filenames
    """

    if os.path.exists(input_list):
        logging.info("Reading in list of spectrum names " + input_list)
    else:
        logging.info("List of spectrum names does not exist! " + input_list)

    # expects header reading
    # spectrum,subtype,phase,feh,err_feh
    input_data_arr = pd.read_csv(input_list)

    # col 0 contains the file names
    filenames_arr = input_data_arr["orig_spec_file_name"].values

    return(filenames_arr)


def read_spec(spec_name, format):
    """
    Read in ascii empirical spectrum and return
    wavelength, flux, and error.

    Parameters:
        spec_name (str): The spectrum filename. If ascii file (no headers), should have
           3 columns \n
           [0]: wavelength \n
           [1] flux \n
           [2] error \n
        format (str): format of the spectrum file ("ascii.no_header" is the only option for now)
    Returns:
       spec_tab: A numpy Table with three columns: wavelength, flux, error
       hdr: FITS header of the input spectrum
    """

    logging.info("Reading spectrum " + spec_name)

    if (format == "ascii.no_header"):

        try:
            spec_tab = Table.read(spec_name, format='ascii.no_header',
                          names=['wavelength', 'flux', 'error'])
            hdr = np.nan

        except IOError:    # pragma: no cover
            # this error should be redundant, since upstream the input file list
            # should be checked with what is in the input directory
            logging.info("File {} not found!".format(spec_name))

    else: # pragma: no cover
        logging.info("File format unknown!!!")

    return(spec_tab, hdr)


def write_bckgrnd_input(name_list, indir, normdir):
    """
    Create input file for the bckgrnd program

    Parameters:
        name_list (list): List of Realization file names (no path info)
        indir (str): The working directory with files to be fed into bkgrnd routine
        normdir (str): The output directory for normalized files
    Returns:
      background input filename string; the filename itself (which
       has been written to disk) lists the input and output directories, and a
       list of the FITS files which are the spectrum realizations in the input
       directory
    """

    logging.info("Creating input file list of spectrum realization filenames")

    # check if directory exists
    if os.path.isdir(indir):
        logging.info('Spectrum realizations being read in from '+str(indir))
    else:
        logging.warning('Making new directory '+str(indir)+ ' which will contain spectrum realizations')
        make_dir(indir)

    #Check to see if inputfile is already there
    bckgrnd_input = os.path.join(indir, "bckgrnd_input.txt")
    if os.path.isfile(bckgrnd_input) is True:
        logging.warning('Removing pre-existing file bckgrnd_input.txt')
        os.remove(bckgrnd_input)
    try:
        outfile = open(bckgrnd_input, 'w')
    except IOError:   # pragma: no cover
            logging.info("File {} could not be opened!".format(bckgrnd_input))


    #Write the text file header (in_dir out_dir)
    outfile.write("{} {}\n".format(indir, normdir))
    for j in range(len(name_list)):
        outfile.write("{}\n".format(name_list[j]))
    outfile.close()

    return(bckgrnd_input)

# -------------
# Main Function
# -------------
class CreateSpecRealizationsMain():
    """

    Generate multiple realizations of the same empirical spectrum based on a noise level.

    Parameters:
        module_name (str): name of module (arbitrary)
        cc_bkgrnd_dir (str): absolute path of the directory containing the compiled binary for spectrum backround normalization
        input_spec_list_read (str): absolute path of the file containing the list of spectrum file names (basenames only)
        unnorm_spectra_dir_read (str): absolute path of the directory containing the spectra
        unnorm_noise_churned_spectra_dir_read (str): absolute path of the directory to contain the output spectra with noise added at the level given by user (which may be zero noise)
        bkgrnd_output_dir_write (str): absolute path of the directory to contain spectra after normalization (reads in from dir set by unnorm_noise_churned_spectra_dir_read/)
        final_spec_dir_write (str): absolute path of the directory to contain spectra after normalization, with two-column formatting (reads in from dir set by bkgrnd_output_dir_write/)
        noise_level (str or float): (file name) of file containing noise levels, "None", or float value to set level of noise being injected into spectra (if the calibration is being applied to the spectra, you almost certainly want this to be zero)
        spec_file_type (str): defines the input file type (only option is "ascii.no_header" for now)
        number_specs (int): number of spectrum realizations to make, per empirical spectrum (if the calibration is being applied, this almost certainly should be 1)
        verb (bool): verbose option

    Returns:
        [text files of spectra written to disk]
    """

    def __init__(self,
                module_name,
                cc_bkgrnd_dir,
                input_spec_list_read,
                unnorm_spectra_dir_read,
                unnorm_noise_churned_spectra_dir_read,
                bkgrnd_output_dir_write,
                final_spec_dir_write,
                noise_level,
                spec_file_type,
                number_specs,
                verb=False):

        self.name = module_name
        self.cc_bkgrnd_dir = cc_bkgrnd_dir
        self.input_spec_list_read = input_spec_list_read
        self.unnorm_spectra_dir_read = unnorm_spectra_dir_read
        self.unnorm_noise_churned_spectra_dir_read = unnorm_noise_churned_spectra_dir_read
        self.bkgrnd_output_dir_write = bkgrnd_output_dir_write
        self.final_spec_dir_write = final_spec_dir_write
        self.noise_level = noise_level
        self.spec_file_type = spec_file_type
        self.number_specs = number_specs
        self.verb = verb

    def run_step(self, attribs = None):

        #input_list = self.input_spec_list_read

        # check if write directories exist and are empty
        make_dir(self.bkgrnd_output_dir_write)
        make_dir(self.final_spec_dir_write)

        logging.info("--------------------------")
        logging.info("Making "+str(self.number_specs)+" realizations of each input spectrum")

        if (self.number_specs > 1) and (self.noise_level == "None"):
            logging.warning("Realizing multiple spectra but noise level is zero")
            input("Hit [Enter] to continue")

        # Read list of input spectra
        # input_list ALREADY SET IN DEFAULTS ## input_list = input_spec_list_read_dir + config_red["file_names"]["LIST_SPEC_PHASE"]
        list_arr = read_list(self.input_spec_list_read)

        if os.path.isdir(self.cc_bkgrnd_dir):
            # check if directory exists
            logging.info("Reading in unnormalized spectra from dir " + self.unnorm_spectra_dir_read)
        else:
            logging.warning('Making new directory '+str(self.unnorm_spectra_dir_read)+ ' which will contain contain unnormalized spectra')
            make_dir(self.cc_bkgrnd_dir)


        # Check to make sure the files in the list are actually in the input directory;
        # if not, just remove those from the list and set a warning
        list_actually_there = glob.glob(self.unnorm_spectra_dir_read + "*.*")
        list_actually_basenames = np.array([os.path.basename(t) for t in list_actually_there])

        num_sought = len(list_arr) # number of wanted files
        num_existing = np.sum(np.in1d(list_arr, list_actually_basenames)) # number of wanted files found
        bool_present = np.in1d(list_arr, list_actually_basenames, invert=False)
        bool_missing = np.in1d(list_arr, list_actually_basenames, invert=True)
        files_missing = list_arr[bool_missing] # files in input list, but not found
        files_present = list_arr[bool_present] # files in input list, and found
        num_extra = np.sum(np.in1d(list_actually_basenames, list_arr, invert=True)) # number of extra files found in the input directory

        # did we find all the spectra we wanted?
        if (num_existing < num_sought):
            logging.warning("Found only "+str(num_existing)+" of "+str(num_sought)+" spectra in input list")
            logging.warning("Files missing from input directory:")
            logging.warning(files_missing)
        else:
            logging.info("All spectra in input list found in input directory")

        # did any other spectra appear in the directory, which may or may not be a good thing?
        if (num_extra > 1):
            logging.warning("Found "+str(num_extra)+" files in directory which do not appear in input list")
        else:
            logging.info("No spectra found in input directory which do not appear in input list.")

        # if there are files missing from the directory, just remove those from the input list
        list_arr = files_present

        # create noise-churned realizations for each spectrum
        name_list = list() # initialize

        for i in range(len(list_arr)): # make spectrum realizations and list of their filenames
            name_list.extend(generate_realizations(spec_name=self.unnorm_spectra_dir_read+"/"+list_arr[i],
                                                   outdir=self.unnorm_noise_churned_spectra_dir_read,
                                                   spec_file_format=self.spec_file_type,
                                                   num=self.number_specs,
                                                   noise_level=self.noise_level))

        # next we need to normalize the spectra; begin by creating input list of
        # spectrum realizations written in the previous step
        bkg_input_file = write_bckgrnd_input(name_list, self.unnorm_noise_churned_spectra_dir_read, self.bkgrnd_output_dir_write)
        logging.info("-------------------------------------------")
        logging.info('The file containing the list of spectra which will be fed ' + \
                    'into the normalization routine is ' + bkg_input_file)

        # normalize each spectrum realization (smoothing parameter is set in __init__)
        if os.path.isdir(self.cc_bkgrnd_dir):
            # check if directory exists
            logging.info('Reading in background binary from '+str(self.cc_bkgrnd_dir))
        else:
            logging.warning('Making new directory '+str(self.normzed_spec_source_dir)+ ' which will contain background binary')
            make_dir(self.cc_bkgrnd_dir)

        bkgrnd = Popen([str(self.cc_bkgrnd_dir) + "bkgrnd", "--smooth "+str(attribs["reduc_params"]["SMOOTH"]),
                        "--sismoo 1", "--no-plot", "{}".format(bkg_input_file)], stdout=PIPE, stderr=PIPE)
        (out, err) = bkgrnd.communicate() # returns tuple (stdout, stderr)

        if self.verb == True: # decode messages
            logging.info(out.decode("utf-8"))
            logging.info(err.decode("utf-8"))

        # read in input files, normalize them, write out, and return list of those filenames
        final_list = create_norm_spec(name_list, self.bkgrnd_output_dir_write, self.final_spec_dir_write)

        logging.info("-------------------------------------------")
        logging.info("Wrote realizations of original spectra to directory")
        logging.info(self.unnorm_noise_churned_spectra_dir_read)
        logging.info("-------------------------------------------")
        logging.info("Wrote raw normalization output to directory")
        logging.info(self.bkgrnd_output_dir_write)
        logging.info("-------------------------------------------")
        logging.info("Wrote final normalized spectra to directory")
        logging.info(self.final_spec_dir_write)

        return final_list
