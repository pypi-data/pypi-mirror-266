import glob
import pandas as pd
import os
import numpy as np
import sys
import pickle
import itertools
import seaborn as sns
import multiprocessing
from multiprocessing import set_start_method
import matplotlib.pyplot as plt
from astropy.table import Table
from astropy.io import fits
from . import *

def collect_results(result):

    results.extend(result)

def feh_layden_vector(coeff_a,coeff_b,coeff_c,coeff_d,H,K):
    """
    Finds Fe/H given equivalent widths (in angstroms), from
    K = a + b*H + c*[Fe/H] + d*H*[Fe/H]  (Layden 1994 Eqn. 7)

    Parameters:
        coeff_a (float): coefficient a
        coeff_b (float): coefficient b
        coeff_c (float): coefficient c
        coeff_d (float): coefficient d

    Returns:
        [Fe/H] value
    """

    feh = np.divide(np.subtract(K,np.subtract(coeff_a,np.multiply(coeff_b,H))),
                    np.add(coeff_c,np.multiply(coeff_d,H)))

    return feh

def feh_abcdfghk_vector(coeff_a,coeff_b,coeff_c,coeff_d,coeff_f,coeff_g,coeff_h,coeff_k,H,K):
    """
    Finds Fe/H given equivalent widths (in angstroms), from
    K = a + b*H + c*[Fe/H] + d*H*[Fe/H] + f*(H^2) + g*([Fe/H]^2) + h*(H^2)*[Fe/H] + k*H*([Fe/H]^2)

    Parameters:
        coeff_a (float): coefficient a
        coeff_b (float): coefficient b
        coeff_c (float): coefficient c
        coeff_d (float): coefficient d
        coeff_f (float): coefficient f
        coeff_g (float): coefficient g
        coeff_h(float): coefficient h
        coeff_k (float): coefficient j
    Returns:
        [Fe/H] value
    """

    A_cap = np.add(coeff_g,np.multiply(coeff_k,H))
    B_cap = np.add(coeff_c,np.add(np.multiply(coeff_d,H),np.multiply(coeff_h,np.power(H,2))))
    C_cap = np.add(coeff_a,np.add(np.multiply(coeff_b,H),np.subtract(np.multiply(coeff_f,np.power(H,2)),K)))
    
    # since this involves a quadratic, there are two roots
    F_pos = np.divide(-np.add(
                            B_cap,
                              np.sqrt(
                                            np.subtract(np.power(B_cap,2.),
                                                        4*np.multiply(A_cap,C_cap))
                                           )
                             ),
                      np.multiply(2,A_cap))

    F_neg = np.divide(-np.subtract(
                                B_cap,
                                np.sqrt(
                                            np.subtract(np.power(B_cap,2.),
                                                             4*np.multiply(A_cap,C_cap))
                                            )),
                      np.multiply(2,A_cap))

    return F_pos, F_neg


def apply_one_spec(ew_data_pass, N_MCMC_samples, mcmc_chain, soln_header):

    Balmer_EW = ew_data_pass["EW_Balmer"]
    CaIIK_EW = ew_data_pass["EW_CaIIK"]

    # set the offset (note mu=0; this is a relative offset)
    # (vestigial)
    offset_H = 0 # np.random.normal(loc = 0.0, scale = err_Balmer_EW)
    offset_K = 0 # np.random.normal(loc = 0.0, scale = err_CaIIK_EW)

    # initialize array
    feh_sample_array = np.nan*np.ones((N_MCMC_samples, 1))

    # find one value of Fe/H given those samples in Balmer and CaIIK EWs
    if (len(mcmc_chain.columns)==4):

        try:

            feh_sample = feh_layden_vector(coeff_a = mcmc_chain["a"],
                                coeff_b = mcmc_chain["b"],
                                coeff_c = mcmc_chain["c"],
                                coeff_d = mcmc_chain["d"],
                                H = Balmer_EW,
                                K = CaIIK_EW)

        except:

            logging.info("Convergence failed")
            ew_data_pass["feh_retrieved"] = -999
            ew_data_pass["err_feh_retrieved"] = -999
            ew_data_pass["teff_retrieved"] = -999
            
            return ew_data_pass

    elif (len(mcmc_chain.columns)==8):

        feh_sample = feh_abcdfghk_vector(coeff_a = mcmc_chain["a"],
                            coeff_b = mcmc_chain["b"],
                            coeff_c = mcmc_chain["c"],
                            coeff_d = mcmc_chain["d"],
                            coeff_f = mcmc_chain["f"],
                            coeff_g = mcmc_chain["g"],
                            coeff_h = mcmc_chain["h"],
                            coeff_k = mcmc_chain["k"],
                            H = Balmer_EW,
                            K = CaIIK_EW)

        # just want one of the two roots
        feh_sample = feh_sample[1]

        # check for NaN answers
        x=feh_sample
        x = x[~np.isnan(x)]
        frac_finite = len(x)/len(feh_sample)

        # if less than 0.95 of the metallicities converged for this
        # spectrum, consider it not to have converged
        if (frac_finite < 0.95):

            logging.info("Convergence failed")
            ew_data_pass["feh_retrieved"] = -999
            ew_data_pass["err_feh_retrieved"] = -999
            ew_data_pass["teff_retrieved"] = -999
            
            return ew_data_pass

        logging.info("-----")


    # output the results (note this corresponds to one spectrum)
    logging.info(str(ew_data_pass["orig_spec_file_name"]) + ", median [Fe/H] = " + str(np.round(np.nanmedian(feh_sample),decimals=3)))
    ew_data_pass["feh_retrieved"] = np.nanmedian(feh_sample)
    ew_data_pass["err_feh_retrieved"] = np.std(feh_sample)
    ew_data_pass["teff_retrieved"] = np.add(
                                        np.multiply(ew_data_pass["EW_Balmer"],soln_header["SLOPE_M"]),
                                        soln_header["YINT_B"]
                                        )
    
    return ew_data_pass


class FehRetrieval():
    """
    Find a Fe/H value for a combination of coefficients
    from the MCMC chain, and sample from the Balmer and
    CaIIK EWs, given their errors

    Parameters:
        write_out_filename (str): the file name of everything, incl. retrieved Teff and Fe/H

    Returns:
        final_table (DataFrame): dataframe equivalent of the written csv file, for unit testing
        [csv is also written to disk]
    """

    def __init__(self,
                module_name,
                file_good_ew_read,
                file_calib_read,
                dir_retrievals_write,
                file_retrievals_write):

        self.name = module_name
        self.file_good_ew_read = file_good_ew_read
        self.file_calib_read = file_calib_read
        self.dir_retrievals_write = dir_retrievals_write
        self.file_retrievals_write = file_retrievals_write


    def run_step(self, attribs = None):

        calib_read_file = self.file_calib_read
        calib_file = calib_read_file ## ## vestigial?
        mcmc_chain = Table.read(calib_file, hdu=1)
        write_pickle_dir = self.dir_retrievals_write
        good_ew_info_file = self.file_good_ew_read
        write_out_filename = self.file_retrievals_write
        ew_file = good_ew_info_file

        if os.path.exists(ew_file):
            logging.info('Reading in EW file from '+str(ew_file))
        else:
            logging.error('EW file '+str(ew_file)+ ' does not exist! ')
            exit()
        ew_data = pd.read_csv(ew_file).copy(deep=True)

        if os.path.exists(calib_file):
            logging.info('Reading in calibration file '+str(calib_file))
        else:
            logging.error('Calibration file '+str(calib_file)+ ' does not exist! ')
            exit()
        hdul = fits.open(calib_file)
        soln_header = hdul[1].header

        # loop over samples in the MCMC chain ## for serial process
        N_MCMC_samples = len(mcmc_chain)

        if os.path.isdir(write_pickle_dir):
            # check if directory exists
            logging.info('Will write [Fe/H] retrievals to '+str(write_pickle_dir))
        else:
            logging.warning('Making new directory '+str(write_pickle_dir)+ ' which will contain [Fe/H] retrievals')
            make_dir(write_pickle_dir)

        # check if there is already something else in pickle directory
        preexisting_file_list = glob.glob(write_pickle_dir + "/*.{*}")
        if (len(preexisting_file_list) != 0):
            logging.info("------------------------------")
            logging.info("Directory to pickle Fe/H retrievals to is not empty!!")
            logging.info(write_pickle_dir)
            logging.info("------------------------------")
            if prompt_user:
                input("Do what you want with those files, then hit [Enter]")

        # add columns to data table to include retrieved Fe/H values
        ew_data["feh_retrieved"] = np.nan
        ew_data["err_feh_retrieved"] = np.nan
        ew_data["teff_retrieved"] = np.nan

        try:
            set_start_method('fork') # necessary to spawn children
        except RuntimeError:
            pass
        pool = multiprocessing.Pool(ncpu)

        # split big dataframe into separate ones, one dataframe per row
        #results = [v for k, v in ew_data.groupby('orig_spec_file_name')]
        ew_data_split = ew_data.to_dict('records')

        # zip things for multiprocessing
        n_elem = len(ew_data_split)
        all_zipped = zip(ew_data_split, list(itertools.repeat(N_MCMC_samples, n_elem)), list(itertools.repeat(mcmc_chain, n_elem)), list(itertools.repeat(soln_header, n_elem)))
        test_results = pool.starmap(apply_one_spec, all_zipped)

        final_table = pd.DataFrame(test_results)

        final_table.to_csv(write_out_filename, index=False)
        logging.info("Wrote out retrieved [Fe/H] and Teff to " + write_out_filename)

        return final_table
