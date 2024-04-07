import numpy as np
import pandas as pd
import logging
import matplotlib.pyplot as plt
from astropy.io import fits
import os
from sys import exit


class FindCorrxn:
    """
    Generates a correction to a raw FITS calibration, based on comparison of the retrievals
    with high-res spectroscopy

    Parameters:
        module_name (str): module name
        file_name_basis_raw_retrieved_fehs (str): file name of retrieved Fe/Hs (these need to
            have high-res counterparts)
        file_name_basis_lit_fehs (str): file name of literature values based on high-res specs
        soln_write_name (str): file name containing empirical [Fe/H] values for stars
        
    Returns:
        writes correction to FITS file solution
    """

    def __init__(self, 
                module_name, 
                file_name_basis_raw_retrieved_fehs, 
                file_name_basis_lit_fehs,
                soln_write_name):

        self.name = module_name
        self.file_name_basis_raw_retrieved_fehs = file_name_basis_raw_retrieved_fehs
        self.file_name_basis_lit_fehs = file_name_basis_lit_fehs
        self.soln_write_name = soln_write_name

    def run_step(self, attribs = None):
        '''
        Finds residual between rrlfe and SSPP values
        
        INPUTS:
        file_name_basis_raw_retrieved_fehs (csv): file name of retrieved McDonald [Fe/H] values, as retrieved using raw rrlfe calibration
        file_name_basis_lit_fehs (str): file name with literature [Fe/H] values based on high-res spectroscopy
        soln_write_name (str): pre-existing FITS file in which to write the offset correction in the header
        
        RETURNS:
        (residuals to 1-to-1 line for testing only)
        '''

        # raw [Fe/H] values retrieved with rrlfe
        logging.info('Reading in raw [Fe/H] values of basis set stars from '+str(self.file_name_basis_raw_retrieved_fehs))
        df_raw_retrieved = pd.read_csv(self.file_name_basis_raw_retrieved_fehs)
        # [Fe/H] based on high-res spectroscopy from the literature; this should include both
        # raw (average) literature values, and the values after remapping onto a common basis set
        logging.info('Reading in [Fe/H] values of basis set stars from high-res spectroscopy literature from '+str(self.file_name_basis_lit_fehs))
        df_basis = pd.read_csv(self.file_name_basis_lit_fehs)
        # average the high-res values for each 

        ## make matching and merger
        df_raw_retrieved['name_match'] = df_raw_retrieved['orig_spec_file_name'].str[:6].str.rstrip('_')

        df_raw_retrieved['name_match'].loc[df_raw_retrieved['name_match'] == 'V445_O'] = 'V445_Oph' # to make the name matching for this star to work right

        # make lower-case in case of case error
        df_basis['name_match'] = df_basis['name_match'].str.lower()
        df_raw_retrieved['name_match'] = df_raw_retrieved['name_match'].str.lower()
        df_merged = df_raw_retrieved[['name_match','feh_retrieved']].merge(df_basis[['name_match','feh_high_res_mapped']], on='name_match', how='inner')

        # the literature [Fe/H] after remapping them onto a common basis
        vals_basis = df_merged['feh_high_res_mapped'].values
        # _r for raw
        vals_rrlfe_r = df_merged['feh_retrieved'].values

        # initial best fit between rrlfe vs. basis
        m_b, b_b = np.polyfit(vals_basis,vals_rrlfe_r,1) # _b: best-fit
        
        # find residual best-fit line
        resids = (m_b-1)*vals_basis + b_b

        # generate corrected Fe/H values
        vals_rrlfe_c = vals_rrlfe_r - resids
        
        # find best-fit of vals_rrlfe_c (corrected) vs. vals_rrlfe_r (raw)
        m_c, b_c = np.polyfit(vals_rrlfe_r,vals_rrlfe_c,1) # _c: corrected

        # read in raw FITS calibration
        hdul = fits.open(self.soln_write_name)
        hdul[1].header["CO_SLP_M"] = (m_c, "Slope of rrlfe_c vs. rrlfe_r")
        hdul[1].header["CO_YIN_B"] = (b_c, "Y-intercept of rrlfe_c vs. rrlfe_r")
        hdul.writeto(self.soln_write_name, overwrite=True)

        logging.info("Appended final calibration correction to " + self.soln_write_name)

        '''
        plt.scatter(vals_sspp,vals_rrlfe)
        plt.plot([-2.8,0.3],[-2.8,0.3],linestyle=":")
        plt.plot(vals_sspp, m_b*vals_sspp + b_b,linestyle="--")
        plt.scatter(vals_sspp, rrlfe_corrected(vals_sspp, vals_rrlfe),linestyle="--", color="red")
        plt.show()
        '''
        
        # returns resids to 1-to-1 line for testing only; the important part above is just to append params
        # of line of best fit to a FITS file
        return vals_rrlfe_r - resids
    

class ApplyCorrxn:
    """
    Applies a correction to Fe/H retrievals, based on the info in the FITS headers

    Parameters:
        module_name (str): module name
        file_name_basis_raw_retrieved_fehs (str): file name of raw retrieved Fe/Hs
        soln_fits_name (str): file name containing the raw calibration as a binary table,
            and the correction in the header
        file_name_corrected_retrieved_fehs_write (str): file name of the Fe/Hs with col
            of corrected Fe/Hs
        
    Returns:
        writes out table with corrected values
    """

    def __init__(self, 
                module_name, 
                file_name_basis_raw_retrieved_fehs, 
                soln_fits_name, 
                file_name_corrected_retrieved_fehs_write):

        self.name = module_name
        self.file_name_basis_raw_retrieved_fehs = file_name_basis_raw_retrieved_fehs
        self.soln_fits_name = soln_fits_name
        self.file_name_corrected_retrieved_fehs_write = file_name_corrected_retrieved_fehs_write

    def run_step(self, attribs = None):
        '''
        Writes out corrected Fe/H values
        
        INPUTS:
        file_name_basis_raw_retrieved_fehs (str): file name of csv of the retrieved values
        soln_fits_name (str): file name of the FITS file of the calibration
        file_name_corrected_retrieved_fehs_write (str): file name of the csv to write with corrected Fe/H values
        
        RETURNS:
        Corrected Fe/H values (for testing only)
        '''

        if os.path.exists(self.file_name_basis_raw_retrieved_fehs):
            # check if file exists
            logging.info('Reading in raw [Fe/H] values from '+str(self.file_name_basis_raw_retrieved_fehs))
        else:
            logging.error('File '+str(self.file_name_basis_raw_retrieved_fehs)+ ' which is supposed to contain raw [Fe/H] values does not exist! ')
            exit()
        df_raw_retrieved = pd.read_csv(self.file_name_basis_raw_retrieved_fehs) # raw values retrieved with rrlfe

        # read in raw FITS calibration
        if os.path.exists(self.soln_fits_name):
            logging.info('Reading in calibration file '+str(self.soln_fits_name))
        else:
            logging.error('Calibration file '+str(self.soln_fits_name)+ ' does not exist! ')
            exit()
        hdul = fits.open(self.soln_fits_name)
        m_slope = float(hdul[1].header["CO_SLP_M"]) # slope of rrlfe_c vs. rrlfe_r
        b_yint = float(hdul[1].header["CO_YIN_B"]) # Y-intercept of rrlfe_c vs. rrlfe_r

        # residuals to 1-to-1 line in rrlfe vs. high-res spectroscopy space
        #resids = (m_slope-1)*vals_basis + b_yint

        # add column with corrected Fe/H values
        feh_c = np.add(b_yint,np.multiply(m_slope,df_raw_retrieved['feh_retrieved'])) # _c: corrected
        df_raw_retrieved['feh_corrected'] = feh_c

        # write out
        df_raw_retrieved.to_csv(self.file_name_corrected_retrieved_fehs_write, index=False)
        logging.info("Corrected Fe/Hs written to " + self.file_name_corrected_retrieved_fehs_write)

        '''
        plt.scatter(vals_sspp,vals_rrlfe)
        plt.plot([-2.8,0.3],[-2.8,0.3],linestyle=":")
        plt.plot(vals_sspp, m_b*vals_sspp + b_b,linestyle="--")
        plt.scatter(vals_sspp, rrlfe_corrected(vals_sspp, vals_rrlfe),linestyle="--", color="red")
        plt.show()
        '''
        
        # return corrected values for testing
        return feh_c
