'''
Scrape Robospect output and do some processing of the results
'''

import os
import sys
import glob
import logging
import pandas as pd
import numpy as np
import matplotlib
from astropy.io.fits import getdata
#import matplotlib # kernel needs to be restarted to avoid TkAgg error
#matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import matplotlib.pylab as pl
from . import *


def line_order_check(line_centers):
    """
    Sanity check that the absorption lines are listed in order
    N.b. This checks the wavelengths using the given line list
    values (and not the fitted centers)

    Parameters:
        line_centers (array of floats): array of measured line centers

    Returns:
        int of number of apparent bad line centers
    """

    logging.info('Verifying line centers...')
    logging.info(line_centers[0])
    glitch_count = int(0) # boolean for bookeeping
    if ((line_centers[0] < 3933.660-10) or
        (line_centers[0] > 3933.660+10)): # CaIIK
        logging.warning('CaIIK line center does not match!')
        glitch_count = int(1) # boolean for bookeeping
    if ((line_centers[1] < 3970.075-10) or
          (line_centers[1] > 3970.075+10)): # H-epsilon (close to CaIIH)
        logging.warning('H-epsilon center (close to CaIIH) line does not match!')
        glitch_count = int(1) # boolean for bookeeping
    if ((line_centers[2] < 4101.7100-10) or
          (line_centers[2] > 4101.7100+10)): # H-delta
        logging.warning('H-delta line center does not match!')
        glitch_count = int(1) # boolean for bookeeping
    if ((line_centers[3] < 4340.472-10) or
          (line_centers[3] > 4340.472+10)): # H-gamma
        logging.warning('H-gamma line center does not match!')
        glitch_count = int(1) # boolean for bookeeping
    if ((line_centers[4] < 4861.290-10) or
          (line_centers[4] > 4861.290+10)): # H-beta
        logging.warning('H-beta line center does not match!')
        glitch_count = 1 # boolean for bookeeping
    if (glitch_count == int(0)):
        logging.info('CaIIK, H-eps, H-del, H-gam, H-beta line centers are consistent')
    return glitch_count




class Scraper():
    """
    Scrape all the equivalent width info from the Robospect robolines files

    Parameters:
        module_name (str): arbitrary module name
        orig_spec_list (list): original file names of spectra to read in
        robo_output_read (str): directory containing Robospect output
        file_scraped_write (str): file name of csv containing the scraped data

    Returns:
        [csv written to disk; dataframe is returned for testing only]
    """

    def __init__(self,
        module_name,
        input_spec_list_read,
        robo_output_read,
        file_scraped_write):

        self.name = module_name
        self.orig_spec_list = input_spec_list_read
        self.robo_output_read = robo_output_read
        self.file_scraped_info = file_scraped_write

    def run_step(self, attribs = None):

        verbose=False

        # directory containing the *.fits.robolines
        # files with the EW info
        stem = '.' ## ##
        # subdirectory containing the *.c.dat files
        subdir = self.robo_output_read

        # get list of filenames without the path
        # note the string being sought here is specific to RW's synthetic spectra; might change later
        if os.path.isdir(subdir):
            logging.info('Reading in Robolines output from '+str(subdir))
        else:
            logging.warning('Making new directory '+str(subdir)+ ' which will contain Robospect output')
            make_dir(subdir)

        file_list_long = glob.glob(subdir+'/'+'*robolines')
        file_list_unsorted = [os.path.basename(x) for x in file_list_long]
        file_list = sorted(file_list_unsorted)

        # read in original file names (note variable is being renamed here)
        input_list = pd.read_csv(self.orig_spec_list)
        orig_spec_list = input_list["orig_spec_file_name"]

        # EW info will get scraped into this
        write_out_filename = self.file_scraped_info
        # check receiving directory exists in first place
        if os.path.dirname(write_out_filename):
            # check if directory exists
            logging.info('File to contain scraped EW data is '+str(write_out_filename))
        else:
            logging.warning('Making new directory '+str(os.path.dirname(write_out_filename))+ ' which will contain EW output data')
            make_dir(os.path.dirname(write_out_filename))

        # return tables of EW data?
        verbose = verbose

        df_master = pd.DataFrame() # initialize

        # loop over all filenames of realizations of empirical spectra, extract line data
        for t in range(0, len(file_list)):

            # read in Robospect output
            logging.info("--------------------")
            logging.info("Reading in Robospect output from directory")
            logging.info(subdir)

            '''
            The following parses lines from Robospect *robolines output files,
            which look like the following, as of the v0.76 tag of Robospect:

            ## Units
            ##AA      [ AA           AA             None]        [ AA             AA                None]             [ AA           AA          None]       mAA        mAA             None      None     None       None
            ## Headers
            ##wave_0  [ gaussianMu   gaussianSigma  gaussianAmp] [ uncertaintyMu  uncertaintySigma  uncertaintyAmp]   [ priorMu      priorSigma  priorAmp]   EQW        uncertaintyEQW  chiSqr    flags    blendGroup comment
            3933.6600 [ 3933.618556  1.636451       -0.338310]   [ 0.043767       0.045441          0.008054]         [ 3934.427147  1.754001    0.384793]   1.387738   0.127230        0.004045  0x10020  0          CaII-K
            3970.0750 [ 3969.912002  6.497202       -0.626854]   [ 0.245555       0.237816          0.023196]         [ 3971.262223  4.535872    0.781687]   10.208984  1.331932        0.117392  0x10020  0          H-eps
            4101.7100 [ 4101.728498  6.829899       -0.596311]   [ 0.335244       0.327236          0.025288]         [ 4102.885050  4.878668    0.734648]   10.208852  1.637334        0.220112  0x10020  0          H-del
            4340.4720 [ 4340.374387  7.365172       -0.557777]   [ 0.395447       0.378434          0.025443]         [ 4340.943149  4.961159    0.689719]   10.297539  1.773505        0.300238  0x10020  0          H-gam
            4861.2900 [ 4861.316520  7.570797       -0.505060]   [ 0.441626       0.426212          0.025690]         [ 4861.746895  4.898021    0.635582]   9.584604   1.822847        0.377350  0x10020  0          H-beta
            '''

            df = pd.read_csv(subdir+'/'+file_list[t],
                             skiprows=19,
                             delim_whitespace=True,
                             index_col=False,
                             usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],
                             names=  ["wavel_stated_center","[1","wavel_found_center","gaussianSigma","gaussianAmp",
                                        "[2","uncertaintyMu","uncertaintySigma","uncertaintyAmp",
                                        "[3","priorMu","priorSigma","priorAmp","EQW","uncertaintyEQW",
                                        "chiSqr","flags","blendGroup","line_name"])

            # remove dummy columns
            df = df.drop(columns=["[1","[2","[3"])
            # remove Robospect delimiter strings from columns and cast contents as floats
            logging.info("Parsing " + file_list[t])
            try:
                # this will fail if there are infs in the EWs
                df["gaussianAmp"] = df["gaussianAmp"].str.replace("]","", regex=True)
                df["gaussianAmp"] = df["gaussianAmp"].astype(float)
                df["uncertaintyAmp"] = df["uncertaintyAmp"].str.replace("]","", regex=True)
                df["uncertaintyAmp"] = df["uncertaintyAmp"].astype(float)
                df["priorAmp"] = df["priorAmp"].str.replace("]","", regex=True)
                df["priorAmp"] = df["priorAmp"].astype(float)
            except:
                # skip this file
                logging.error("Parsing error! " + file_list[t])
                continue

            # check lines are in the right order
            # if they are not, a warning is printed in the log
            glitches_num = line_order_check(df['wavel_found_center'])

            # add two cols on the left: the filename, and the name of the line
            #s_length = len(df['mean']) # number of lines (should be 5)

            # file names
            df['robolines_file_name'] = pd.Series(file_list[t],
                                        index=df.index)

            # names of empirical spectra realizations (multiple ones
            # correspond to one empirical spectrum)
            # remove .robolines extension
            df['realization_spec_file_name'] = pd.Series(file_list[t].split(".robolines")[0],
                                              index=df.index)

            # names of the absorption lines
            df['line_name'] = ['CaIIK', 'Heps', 'Hdel', 'Hgam', 'Hbet']

            # print progress
            logging.info('Out of '+str(len(file_list))+' files, '+str(t+1)+' scraped...')

            # if this is the first list, start a master copy from it to concatenate stuff to it
            if (t == 0):
                df_master = df.copy()
            else:
                df_master = pd.concat([df_master, df])
                del df # clear variable

        # write to csv, while resetting the indices
        # note THIS TABLE INCLUDES ALL DATA, GOOD AND BAD
        #df_master_reset = df_master.reset_index(drop=True).copy()
        # this is effectively the same, but gets written out
        make_dir(write_out_filename) # check if write directory exists and is empty
        df_master.reset_index(drop=True).to_csv(write_out_filename,index=False)
        logging.info("Table of ALL EW info written to " + str(write_out_filename))
        #if self.verbose:
        #    return df_master_reset, df_master_reset_drop_bad_spectra
        # return for checking
        return df_master


class AddSyntheticMetaData():
    """
    For the generation of a calibration, this reads in a file with spectrum file
    names and other info like Fe/H, and adds everything to the table with EWs

    Parameters:
        module_name (str): arbitrary module name
        input_spec_list_read (str): file name of list containing original spectrum names and meta-data
        ew_data_w_net_balmer_read (str): file name of table containing EW data including Balmer lines and their errors
        file_w_meta_data_write (str): file name with everything together to write out

    Returns:
        [csv written to disk; dataframe is returned for testing only]
    """

    def __init__(self,
                module_name,
                input_spec_list_read,
                ew_data_w_net_balmer_read,
                file_w_meta_data_write):

        self.name = module_name
        self.input_spec_list_read = input_spec_list_read
        self.ew_data_w_net_balmer_read = ew_data_w_net_balmer_read
        self.file_w_meta_data_write = file_w_meta_data_write

    def run_step(self, attribs = None):

        input_list = self.input_spec_list_read
        read_in_filename = self.ew_data_w_net_balmer_read
        write_out_filename = self.file_w_meta_data_write

        # read in metadata
        logging.info("Reading in meta-data from file " + str(input_list))
        input_data_arr = pd.read_csv(input_list)

        # read in EW data
        all_data = pd.read_csv(read_in_filename)

        # add rows of meta-data table to EW data table, based on matchings of original spectrum file names
        combined_data = all_data.merge(input_data_arr,how="left",on="orig_spec_file_name")

        # write out
        combined_data.to_csv(write_out_filename,index=False)
        logging.info("Table of EW info with meta-data written to " + str(write_out_filename))

        # return for testing
        return combined_data


class QualityCheck():
    """
    Reads in all the scraped EW data in raw form, removes spectra that have fits
    which are bad based on multiple criteria, and writes out another data_table

    Parameters:
        module_name (str): arbitrary module name
        file_scraped_all_read: file name of the table with ALL scraped data from Robospect
        file_scraped_good_write: file name of the table with spectra with any bad line fits removed

    Returns:
        [csv written to disk; dataframe is returned for testing only]
    """

    def __init__(self,
                module_name,
                file_scraped_all_read,
                file_scraped_good_write):

        self.name = module_name
        self.file_scraped_all_read = file_scraped_all_read
        self.file_scraped_good_write = file_scraped_good_write

    def run_step(self, attribs = None):

        read_in_filename = self.file_scraped_all_read
        write_out_filename = self.file_scraped_good_write

        # read in data
        if os.path.exists(read_in_filename):
            # check if directory exists
            logging.info("Reading in for quality check: " + str(read_in_filename))
        else:
            logging.error('File '+str(read_in_filename)+ ' which is supposed to contain scraped EW data does not exist! ')
            exit()
        
        all_data = pd.read_csv(read_in_filename)

        # make new column for 'good' (G) or 'bad' (B) based on the below criteria
        # (initialize all as 'G')
        all_data["quality"] = "G"

        # impose criteria for pruning of data

        # Criterion 1. Remove all rows with a Robospect flag ending with something other than zero
        # (i.e., Robospect found the fit to be bad)
        # make an array consisting of the last character in each spectrum's flag
        red_flag_array = ([u[-1] for u in all_data["flags"]])
        # consider bad flags to be of any flag with a nonzero last character
        # and remove rows if the bad flag corresponds to CaIIK, Hgam, or Hdel
        where_red_flag = np.where(np.logical_and(
                                                np.array(red_flag_array) != '0',
                                                np.logical_or(all_data["line_name"] == "CaIIK",
                                                    np.logical_or(all_data["line_name"] == "Hgam",all_data["line_name"] == "Hdel")
                                                    )
                                                )
                                )
        # identify the synthetic spectrum names which have at least one line with a bad fit
        bad_robo_spectra = all_data["realization_spec_file_name"][np.squeeze(where_red_flag)]

        # remove duplicate names
        try:
            # case of >1 bad spectrum
            bad_robo_spectra_uniq = bad_robo_spectra.drop_duplicates()
        except:
            bad_robo_spectra_uniq = bad_robo_spectra_uniq
        # flag as bad the spectra with those names
        all_data.loc[all_data["realization_spec_file_name"].isin(bad_robo_spectra_uniq),"quality"] = "B"

        # Criterion 2. Remove rows where the line centers are not right, using steps similar to above
        # (specifically, if measured line center is more than 10 A away from perfect center)
        where_bad_line_center = np.where(np.abs(np.subtract(all_data["wavel_found_center"],all_data["wavel_stated_center"]) > 10))
        bad_line_center_spectra = all_data["realization_spec_file_name"][np.squeeze(where_bad_line_center,axis=0)] # squeeze necessary to preserve finite size
        bad_line_center_spectra_uniq = bad_line_center_spectra.drop_duplicates()
        all_data.loc[all_data["realization_spec_file_name"].isin(bad_line_center_spectra_uniq),"quality"] = "B"

        # Criterion 3. Remove rows with EWs which are clearly unrealistically large which slipped through other checks
        # (this is particularly an issue with the CaIIK line, which is close to CaIIH)
        # set cutoff at 18 A, based on inspection of >200 Robospect plots of fits to
        # synthetic spectra; all those with CaIIK EW > 18 are clearly not fit right,
        # and all those with EW < 18 look acceptable -E.S.
        '''
        where_bad_CaIIK = np.where(np.logical_and(all_data["line_name"] == "CaIIK", all_data["EQW"] > 18))
        bad_CaIIK_spectra = all_data["realization_spec_file_name"][np.squeeze(where_bad_CaIIK)]
        bad_CaIIK_spectra_uniq = bad_CaIIK_spectra.drop_duplicates()
        all_data.loc[all_data["realization_spec_file_name"].isin(bad_CaIIK_spectra_uniq),"quality"] = "B"
        '''

        # Criterion 4. Remove bad phases (for empirical data)
        '''
        min_good, max_good = phase_regions()
        #[...]
        #good_indices = np.intersect1d(good_phase, good_metal)
        #[...]
        '''

        # Last step: Write only the rows with a good ("G") flag to file
        # (note that if AT LEAST one absorption line was found to be bad, ALL the
        # data corresponding to that spectrum is removed)
        pruned_data = all_data[all_data.quality == "G"]#.reset_index()
        pruned_data.to_csv(write_out_filename,index=False)

        logging.info("--------------------------")
        logging.info('Scraped Robospect output written to')
        logging.info(write_out_filename)

        return pruned_data


class GenerateNetBalmer():
    """
    Takes stacked spectra data and adds a column representing a net Balmer line,
    and populates another column for the error (based on propagation of the Robo
    errors of constituent lines, and then some error propagation)

    Parameters:
        module_name (str): arbitrary module name
        file_restacked_read: name of the file with stacked EW data from Robospect, and
            only including 'good' data
        file_ew_net_balmer_write: name of the file to be written out; identical to the file read in,
            except that additional columns contain info on a net Balmer line

    Returns:
        writes out csv with net Balmer line EWs, and the following for testing: [m, err_m, b, err_b], [m_1to1, err_m_1to1, b_1to1, err_b_1to1], df_poststack
    """

    def __init__(self,
                module_name,
                file_restacked_read,
                file_ew_net_balmer_write):

        self.name = module_name
        self.file_restacked_read = file_restacked_read
        self.file_ew_net_balmer_write = file_ew_net_balmer_write

    def run_step(self, attribs = None):

        read_in_filename = self.file_restacked_read
        write_out_filename = self.file_ew_net_balmer_write

        # read in
        if os.path.exists(read_in_filename):
            # check if directory exists
            logging.info('Reading in restacked EW data from '+str(read_in_filename))
        else:
            logging.error('File '+str(read_in_filename)+ ' which is supposed to contain restacked EW data does not exist! ')
            exit()
        df_poststack = pd.read_csv(read_in_filename)

        # to generate a net Balmer line, make a rescaling of Hgamma
        # based on Hdelta
        logging.info("Making a net Balmer line")

        # get rid of *really* bad points, and make sure they're simultaneously finite
        # (otherwise a skipped 'nan' may cause a phase shift between the two series)

        idx_cond = np.logical_and(
                                np.logical_and(df_poststack["EW_Hdelta"] > 0.5, df_poststack["EW_Hdelta"] < 20.),
                                np.logical_and(df_poststack["EW_Hgamma"] > 0.5, df_poststack["EW_Hgamma"] < 20.)
                                )

        EW_Hgamma_good = df_poststack["EW_Hgamma"].where(idx_cond).dropna()
        EW_Hdelta_good = df_poststack["EW_Hdelta"].where(idx_cond).dropna()

        # vestigial from when we were trying to scale the lines instead of simply averaging them
        [m, err_m, b, err_b] = [0,0,0,0]

        # Propagate the error by simply doing
        #
        # err_W_B = sqrt ( err_W_delta^2 + err_W_gamma^2 )

        # add column of net Balmer line
        cols = ["EW_Hgamma","EW_Hdelta"]
        df_poststack["EW_Balmer"] = df_poststack[cols].mean(axis=1) # simple average; note these are all of the spectra


        df_poststack["err_EW_Balmer_from_robo"] = 0.5*np.sqrt(
                                                            np.add( np.power(df_poststack["err_EW_Hdelta_from_robo"],2.),
                                                                    np.power(df_poststack["err_EW_Hgamma_from_robo"],2.)
                                                                    )
                                                            ) # sigma_B

        # write out
        if os.path.exists(os.path.dirname(write_out_filename)):
            # check if directory exists
            logging.info("Table with net Balmer line EWs being written to " + str(write_out_filename))
        else:
            logging.warning('Making new directory '+str(os.path.dirname(write_out_filename))+ ' which will contain Balmer line EW file')
            make_dir(os.path.dirname(write_out_filename))
        df_poststack.to_csv(write_out_filename,index=False)
        

        # returns parameters of line fit, and DataFrame with net Balmer info
        return [m, err_m, b, err_b], df_poststack


class GenerateAddlEwErrors():
    """
    Calculates errors in EW using the method of finding the stdev of EWs across
    a set of spectra that are realizations of the same single, original spectrum.
    This is an alternative to the errors produced directly by Robospect.

    Parameters:
        module_name (str): arbitrary module name
        ew_data_restacked_read (str): file name of restacked EW data to read
        ew_data_w_net_balmer_read (str): file name of restacked EW data to read
        groupby_parent (bool): if True, collapse noise-churned spectra into 1 after calculating the EW errors;
            else write out a giant table containing data for all noise-churned spectra,
            which is useful if calibration is being applied, and Fe/H will be retrieved
            across all churnings and that will give Fe/H error
    """

    def __init__(self,
                module_name,
                ew_data_restacked_read,
                ew_data_w_net_balmer_read,
                groupby_parent=True):

        self.name = module_name
        self.ew_data_restacked_read = ew_data_restacked_read
        self.ew_data_w_net_balmer_read = ew_data_w_net_balmer_read
        self.groupby_parent = groupby_parent

    def run_step(self, attribs = None):

        read_in_filename = self.ew_data_restacked_read
        write_out_filename = self.ew_data_w_net_balmer_read
        groupby_parent = self.groupby_parent

        df_postbalmer = pd.read_csv(read_in_filename)

        # calculate errors from noise churning (may get added later)
        '''
        orig_specs_nonrepeating = df_postbalmer["orig_spec_file_name"].drop_duplicates().values
        df_postbalmer["err_EW_Balmer_based_noise_churning"] = np.nan # initialize
        df_postbalmer["err_EW_Hbeta_based_noise_churning"] = np.nan # initialize
        df_postbalmer["err_EW_Hdelta_based_noise_churning"] = np.nan # initialize
        df_postbalmer["err_EW_Hgamma_based_noise_churning"] = np.nan # initialize
        df_postbalmer["err_EW_Heps_based_noise_churning"] = np.nan # initialize
        df_postbalmer["err_EW_CaIIK_based_noise_churning"] = np.nan # initialize

        for orig_spec in orig_specs_nonrepeating:
            # loop over the parent spectra, and get stdev of EWs from each set
            # of spectra with the same parent

            # net Balmer
            stdev_this_set_balmer = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_Balmer"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_Balmer_based_noise_churning"] = stdev_this_set_balmer

            # Hbeta
            stdev_this_set_Hbeta = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_Hbeta"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_Hbeta_based_noise_churning"] = stdev_this_set_Hbeta

            # Hdelta
            stdev_this_set_Hdelta = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_Hdelta"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_Hdelta_based_noise_churning"] = stdev_this_set_Hdelta

            # Hgamma
            stdev_this_set_Hgamma = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_Hgamma"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_Hgamma_based_noise_churning"] = stdev_this_set_Hgamma

            # Hepsilon
            stdev_this_set_Heps = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_Heps"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_Heps_based_noise_churning"] = stdev_this_set_Heps

            # CaIIK
            stdev_this_set_CaIIK = np.nanstd(df_postbalmer.where(df_postbalmer["orig_spec_file_name"] == orig_spec)["EW_CaIIK"])
            df_postbalmer.loc[(df_postbalmer["orig_spec_file_name"] == orig_spec),"err_EW_CaIIK_based_noise_churning"] = stdev_this_set_CaIIK


        logging.info("Added column of EW errors based on stdev across noise-churned spectra")

        if groupby_parent:
            # collapse the noise-churned data such that there is only one row for each parent spectrum
            df_postbalmer_grouped = df_postbalmer.groupby("orig_spec_file_name", as_index=False).median()
            df_postbalmer_errors = df_postbalmer_grouped.to_csv(write_out_filename, index=False)
            logging.info("Grouped spectra by parent, and collapsed by taking median down the columns.")

        else:
            df_postbalmer_errors = df_postbalmer.to_csv(write_out_filename, index=False)
            logging.info("Did not group spectra by parent; table with all noise churnings will be written out.")
        '''


        # calculate EW errors based on linear fit to 
        # std of EW returned by Robo (y) vs err of EW returned by Robo (x)
        def scale_robo_err_to_err(robo_err):
        
            poly_fit_stdvsRobo = np.array([0.04154731,0.44331584]) # fit coeffs

            err = np.multiply(poly_fit_stdvsRobo[0],robo_err) + poly_fit_stdvsRobo[1]

            return err

        df_postbalmer['err_EW_Balmer_scaled'] = scale_robo_err_to_err(df_postbalmer['err_EW_Balmer_from_robo'])
        df_postbalmer['err_EW_CaIIK_scaled'] = scale_robo_err_to_err(df_postbalmer['err_EW_CaIIK_from_robo'])

        df_postbalmer.to_csv(write_out_filename, index=False)
        logging.info("Wrote table out to " + str(write_out_filename))

        '''
        logging.info("------------------------------")
        #logging.info("Data will be written out to file " + write_out_filename)
        #input("Hit [Enter] to continue")
        logging.info("Writing out re-casting of Robospect EWs and rescaled Balmer line to " + write_out_filename)
        df_poststack.to_csv(write_out_filename)
        '''

        # FYI plot: how do Balmer lines scale with each other?
        '''
        plt.clf()
        plt.title("Scaling of lines with Hdelta")
        plt.scatter(df_poststack["EW_Hdelta"],df_poststack["EW_Hbeta"], s=3, label="Hbeta")
        plt.scatter(df_poststack["EW_Hdelta"],np.add(df_poststack["EW_Hgamma"],4), s=3, label="Hgamma+4")
        plt.scatter(df_poststack["EW_Hdelta"],np.add(df_poststack["EW_Heps"],8), s=3, label="Heps+8")
        #plt.ylim([0,15])
        plt.xlabel("EW, Hdelta (Angstr)")
        plt.ylabel("EW, non-Hdelta (Angstr)")
        plt.legend()
        plt.savefig("junk_balmer_rescalings.pdf")

        # FYI plot: KH plot
        plt.clf()
        plt.title("KH plot")
        plt.errorbar(df_poststack["EW_resc_Hgamma"],df_poststack["EW_CaIIK"],
                     yerr=df_poststack["err_EW_CaIIK_from_Robo"],
                     marker="o", markersize=2, mfc="k", mec="k", ecolor="gray", linestyle="")
        plt.ylim([0,30])
        plt.xlabel("EW, net Balmer (Angstr)")
        plt.ylabel("EW, CaIIK (Angstr)")
        plt.savefig("junk_KH_plot.pdf")
        '''

        # return dataframe for test function
        return df_postbalmer


class StackSpectra():
    """
    Takes output of quality_check() and transposes and stacks data so that the data has *rows* of spectra and *cols* of absorption lines

    Parameters:
        module_name (str): arbitrary module name
        input_spec_list_read (str): list of spectrum file names to read
        file_ew_data_read (str): file name of file with EW data
        file_restacked_write (str): file name of restacked data

    Returns:
        [writes out csv with stacked data, and returns it for testing only]
    """

    def __init__(self,
                module_name,
                input_spec_list_read,
                file_ew_data_read,
                file_restacked_write):

        self.name = module_name
        self.input_list_read = input_spec_list_read
        self.file_ew_data_read = file_ew_data_read
        self.file_restacked_write = file_restacked_write

    def run_step(self, attribs = None):

        read_in_filename = self.file_ew_data_read
        write_out_filename = self.file_restacked_write
        input_list = self.input_list_read

        # read in EW data
        if os.path.exists(read_in_filename):
            logging.info('Reading in file with good EW data from '+str(read_in_filename))
        else:
            logging.error('File '+str(read_in_filename)+ ' which is supposed to contain background good EW data does not exist! ')
            exit()
        df_prestack = pd.read_csv(read_in_filename)

        print('--------')
        #print(read_in_filename)
        print(df_prestack)
        print('--------')
        #print('Reading in original input spectrum file list from '+str(input_list))

        # read in the list of original file names
        if os.path.exists(input_list):
            logging.info('Reading in original input spectrum file list from '+str(input_list))
        else:
            logging.error('File '+str(input_list)+ ' which is supposed to contain original spectrum file names does not exist! ')
            exit()
        original_names = pd.read_csv(input_list)

        logging.info("--------------")
        logging.info("Reading in spectra as listed in " + input_list)

        # make list of individual spectra for which we have EW data, and
        # initialize DataFrame to hold the re-cast data

        list_indiv_spectra = list(df_prestack["realization_spec_file_name"].drop_duplicates())

        print(df_prestack["realization_spec_file_name"])
        print(list_indiv_spectra)

        num_indiv_spectra = len(list_indiv_spectra)

        df_poststack = pd.DataFrame(columns=["realization_spec_file_name",
                                             "orig_spec_file_name",
                                             "EW_Hbeta", "err_EW_Hbeta_from_robo",
                                             "EW_Hdelta", "err_EW_Hdelta_from_robo",
                                             "EW_Hgamma", "err_EW_Hgamma_from_robo",
                                             "EW_Heps", "err_EW_Heps_from_robo",
                                             "EW_CaIIK", "err_EW_CaIIK_from_robo"], index=range(num_indiv_spectra))

        for t in range(0,num_indiv_spectra):
            # loop over all spectra realizations we have measured EWs from to populate the dataframe

            this_realization_spectrum = list_indiv_spectra[t]
            logging.info("Extracting EW data corresponding to " + this_realization_spectrum)

            # extract original file name (the one from which realizations are made)
            # loop over all the original spectrum names; which contains a string that
            # appears in the name of the noise-churned spectrum name?
            condition_array = []

            for this_parent_spectrum in original_names["orig_spec_file_name"]:
                # based on naming convention where noise-churned spec is given a 'ver' name
                # ex. (original, realization) = (700030p00.smo, 700030p00_noise_ver_009.smo)
                trunc_name_parent_spectrum = this_parent_spectrum.split(".")[0]
                condition_array.append(trunc_name_parent_spectrum in this_realization_spectrum)

            try:
                orig_name = original_names[condition_array]["orig_spec_file_name"].values[0]
            except: # pragma: no cover
                # sanity check: if strings are not shared, skip and move to next spectrum
                logging.warning("Spectrum file strings don't match!! Skipping " + this_realization_spectrum)

            # select data from table relevant to this spectrum realization
            data_this_spectrum = df_prestack.where(df_prestack["realization_spec_file_name"] == this_realization_spectrum).dropna().reset_index()

            try:
                # extract Balmer lines from the table of data for this specific spectrum realization
                Hbeta = data_this_spectrum["EQW"].where(data_this_spectrum["line_name"] == "Hbet").dropna().values[0]
                err_Hbeta = data_this_spectrum["uncertaintyEQW"].where(data_this_spectrum["line_name"] == "Hbet").dropna().values[0]

                Hgamma = data_this_spectrum["EQW"].where(data_this_spectrum["line_name"] == "Hgam").dropna().values[0]
                err_Hgamma = data_this_spectrum["uncertaintyEQW"].where(data_this_spectrum["line_name"] == "Hgam").dropna().values[0]

                Hdelta = data_this_spectrum["EQW"].where(data_this_spectrum["line_name"] == "Hdel").dropna().values[0]
                err_Hdelta = data_this_spectrum["uncertaintyEQW"].where(data_this_spectrum["line_name"] == "Hdel").dropna().values[0]

                Heps = data_this_spectrum["EQW"].where(data_this_spectrum["line_name"] == "Heps").dropna().values[0]
                err_Heps = data_this_spectrum["uncertaintyEQW"].where(data_this_spectrum["line_name"] == "Heps").dropna().values[0]

                CaIIK = data_this_spectrum["EQW"].where(data_this_spectrum["line_name"] == "CaIIK").dropna().values[0]
                err_CaIIK = data_this_spectrum["uncertaintyEQW"].where(data_this_spectrum["line_name"] == "CaIIK").dropna().values[0]

                # fill in that row in the dataframe
                df_poststack.iloc[t]["realization_spec_file_name"] = this_realization_spectrum
                df_poststack.iloc[t]["orig_spec_file_name"] = orig_name
                df_poststack.iloc[t]["EW_Hbeta"] = Hbeta
                df_poststack.iloc[t]["err_EW_Hbeta_from_robo"] = err_Hbeta
                df_poststack.iloc[t]["EW_Hdelta"] = Hdelta
                df_poststack.iloc[t]["err_EW_Hdelta_from_robo"] = err_Hdelta
                df_poststack.iloc[t]["EW_Hgamma"] = Hgamma
                df_poststack.iloc[t]["err_EW_Hgamma_from_robo"] = err_Hgamma
                df_poststack.iloc[t]["EW_Heps"] = Heps
                df_poststack.iloc[t]["err_EW_Heps_from_robo"] = err_Heps
                df_poststack.iloc[t]["EW_CaIIK"] = CaIIK
                df_poststack.iloc[t]["err_EW_CaIIK_from_robo"] = err_CaIIK

            except: # pragma: no cover
                logging.error("Data stacking error in data for " + this_realization_spectrum)
                logging.error("Data anomaly; skipping " + this_realization_spectrum)

        # save intermediary table of data, before adding rescaled Balmer line
        logging.info("Writing out intermediary file of stacked Robospect EWs and rescaled Balmer lines to " + write_out_filename)
        df_poststack.to_csv(write_out_filename,index=False)

        return df_poststack
