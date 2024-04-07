'''
Consolidates all the data to make it ready for the MCMC
'''

import glob
import sys
import pickle
import numpy as np
import pandas as pd
from pylab import *
from . import *


def graft_feh(pickle_source_dir,
              stars_and_offsets_info_file,
              hk_source_dir,
              synthetic=False):
    """
    Read in the EW and phase data, and attach Fe/H values

    Parameters:
        pickle_source_dir (str): source directory of pickled mapped Fe/H data
        stars_and_offsets_info_file (str): file name of star subtypes and their offsets
        hk_source_dir (str): source directory for HK info
        synthetic (bool):
            =False: the Fe/H will be derived from the basis
            =True: the Fe/H will be extracted from the file name

    Returns:
        [text file of EW and Fe/H values for each star written to disk]
    """

    if not synthetic:
        # read in star names first
        # N.b. this is just the RRabs with RRab offsets for now
        real_data_1 = pickle.load( open(pickle_source_dir  +
                                    stars_and_offsets_info_file, "rb" ) )

        # arrange the data in a way we can use
        # N.b. This is NOT fake data; I'm just appropriating the old variable name
        # Note the placeholder Layden errors for now
        data_1 = { "star_name": real_data_1[0]["name_star"],
                "feh_lit": real_data_1[0]["feh_highres"],
                "feh_layden": real_data_1[0]["feh_basis"],
                "err_feh_lit": np.zeros(len(real_data_1[0]["feh_basis"])),
                "err_feh_layden": 0.07*np.ones(len(real_data_1[0]["feh_basis"]))}

        # loop over each star to read in the calculated metallicities
        final_star_feh = pd.DataFrame(columns=["star_name",
                                           "final_feh_center",
                                           "final_feh_lower",
                                           "final_feh_upper"])
        for t in range(0, len(data_1["star_name"])):
            this_star = data_1["star_name"][t]

            # replace space with underscore
            name_star_underscore = str(this_star).replace(" ", "_")

            # read the mapped Fe/H values
            pickle_read_name = (pickle_source_dir + "plot_info_" +
                            name_star_underscore + ".pkl")
            with open(pickle_read_name, 'rb') as f:
                name_star,feh_mapped_array,x_vals,y_vals,xvals_interp,cdf_gauss_info,\
                  idx,idx_1sig_low,idx_1sig_high,shortest_xrange_lower,\
                  shortest_xrange_upper,shortest_xrange_halfway = pickle.load(f)
            this_feh_center = shortest_xrange_halfway
            this_feh_lower = shortest_xrange_lower
            this_feh_upper = shortest_xrange_upper

            final_star_feh = final_star_feh.append({"star_name_underscore": name_star_underscore,
                                               "final_feh_center": this_feh_center,
                                               "final_feh_lower": this_feh_lower,
                                               "final_feh_upper": this_feh_upper},
                                               ignore_index=True)

    # read in the EW and phase info
    hk_ews = pd.read_csv(hk_source_dir + config_choice["file_names"]["MORE_REALISTIC"])

    # paste the feh values onto the HK table
    # loop over each row of the HK table and assign an FeH based
    # on string in empirical spectrum name
    hk_ews["final_feh_center"] = np.nan
    hk_ews["final_feh_lower"] = np.nan
    hk_ews["final_feh_upper"] = np.nan
    hk_ews["Teff"] = np.nan
    hk_ews["logg"] = np.nan

    # loop over each star name (of which our program stars are a subset)
    # and paste the FeH values to the HK table rows corresponding to the
    # empirical spectra for that star
    if not synthetic:
        logging.info("Filling in Fe/H values for empirical spectra")
        for star_num in range(0, len(final_star_feh["star_name_underscore"])):
            this_star = final_star_feh["star_name_underscore"][star_num]
            logging.info("Retrieving calculated Fe/H value for " + this_star)
            feh_center_this_star = final_star_feh["final_feh_center"][star_num]
            feh_lower_this_star = final_star_feh["final_feh_lower"][star_num]
            feh_upper_this_star = final_star_feh["final_feh_upper"][star_num]

            # loop over each of our program stars; i.e., empirical spectra
            for em_spec_num in range(0, len(hk_ews["original_spec_file_name"])):

                # if the star assigned to an FeH value appears in the empirical spectrum name
                if (this_star in hk_ews["original_spec_file_name"][em_spec_num]):
                    hk_ews["final_feh_center"].iloc[em_spec_num] = feh_center_this_star
                    hk_ews["final_feh_lower"].iloc[em_spec_num] = feh_lower_this_star
                    hk_ews["final_feh_upper"].iloc[em_spec_num] = feh_upper_this_star

    # if these are synthetic spectra
    elif synthetic:
        logging.info("Filling in Fe/H values for synthetic spectra")

        # read in FeH values
        feh_info = pd.read_csv(hk_source_dir + config_choice["file_names"]["LIST_SPEC_PHASE"],
                    delim_whitespace=True)

        for synth_spec_num in range(0, len(hk_ews["original_spec_file_name"])):
            logging.info("Num " + str(synth_spec_num) + " out of " + str(len(hk_ews["original_spec_file_name"])))
            this_synth_spectrum_name = hk_ews["original_spec_file_name"][synth_spec_num]

            # find where spectrum name in feh_info matches, and grab the FeH from there
            row_of_interest = feh_info.where(feh_info["Original_spectrum_file_name"] == this_synth_spectrum_name).dropna()
            # take FeH of zeroth location (there could be repeats)
            feh_center_this_star = row_of_interest["final_FeH"].values[0]
            err_feh_center_this_star = row_of_interest["final_err_FeH"].values[0]
            feh_lower_this_star = np.subtract(feh_center_this_star,err_feh_center_this_star)
            feh_upper_this_star = np.add(feh_center_this_star,err_feh_center_this_star)

            # also obtain logg and Teff
            Teff_this_star = row_of_interest["Teff"].values[0]
            logg_this_star = row_of_interest["logg"].values[0]

            hk_ews["final_feh_center"].iloc[synth_spec_num] = feh_center_this_star
            hk_ews["final_feh_lower"].iloc[synth_spec_num] = feh_lower_this_star
            hk_ews["final_feh_upper"].iloc[synth_spec_num] = feh_upper_this_star
            hk_ews["Teff"].iloc[synth_spec_num] = Teff_this_star
            hk_ews["logg"].iloc[synth_spec_num] = logg_this_star

        # now remove the synthetic spectra with Teff<6000, Teff>7500, logg=2
        # ... this functionality should be moved
        hk_ews = hk_ews[hk_ews.Teff >= 6000]
        hk_ews = hk_ews[hk_ews.Teff <= 7500]
        hk_ews = hk_ews[hk_ews.logg > 2]
        hk_ews = hk_ews.reset_index()

    # fyi
    hk_ews.to_csv('junk.csv')

    # pickle the table of H,K,phases,Fe/H
    pickle_write_name = pickle_source_dir + config_choice["file_names"]["KH_FINAL_PKL"]
    with open(pickle_write_name, "wb") as f:
        pickle.dump(hk_ews, f)
    logging.info("-----------------------------")
    logging.info("Wrote HK data with Fe/H values to ")
    logging.info(pickle_write_name)

    return


def winnow(pickle_source_dir=config_choice["data_dirs"]["DIR_PICKLE"],
                         hk_winnowed_write_dir=config_choice["data_dirs"]["DIR_BIN"]):
    """
    Removes the program star spectra based on criteria such as \n
    1. phase (0 to 1) \n
    2. star subtype (ab, c)

    Parameters:
        pickle_source_dir (str): directory containing
        hk_winnowed_write_dir (str): directory to which csv info on H, K is written
        remove_rrl_subtype (str): RR Lyrae subtype to remove from analysis ("ab", "c", or none)

    Returns:
        [csv written to disk]
    """

    # read in phase boundaries
    min_good, max_good = phase_regions()

    # restore pickle file with all the H,K data
    hk_data = pickle.load( open( pickle_source_dir +
                                 config_choice["file_names"]["KH_FINAL_PKL"], "rb" ) )

    hk_data_winnowed = hk_data.where(np.logical_and(hk_data["phase"] > min_good,
                                                    hk_data["phase"] < max_good)).dropna().reset_index()

    winnowed_file_name = hk_winnowed_write_dir + config_choice["file_names"]["KH_WINNOWED"]
    hk_data_winnowed.to_csv(winnowed_file_name)
    logging.info("--------------------------")
    logging.info("Wrote winnowed EW data for MCMC to ")
    logging.info(winnowed_file_name)

    # future possibility to winnow by star type, too

    return
