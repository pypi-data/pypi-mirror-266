import matplotlib
matplotlib.use('Agg')

import sys, os
from configparser import ConfigParser, ExtendedInterpolation
import pandas as pd
import astropy
from scipy.optimize import least_squares
from astropy.io import fits

current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, target_dir)

# import more things with changed system path
from rrlfe import *
from rrlfe import run_emcee
from conf import *
import numpy as np
import glob

# configuration data for reduction
config_gen = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
# config for reduction to find a, b, c, d
config_gen.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_gen.ini'))

# set some fake constants
coeffs_4_test = np.array([1.5,2.6,3.7,4.8])
coeffs_8_test = np.array([1.2,2.7,3.9,4.7,0.5,0.42,-0.12,-0.04])
Bal_test = 0.55
Feh_test = -0.4
Caiik_test = 1.3
err_Bal_test = 0.33
err_Feh_test = 0.11
err_Caiik_ew_test = 0.27


def test_WriteSolnToFits():

    inst_abcdfghk = run_emcee.WriteSolnToFits(module_name="test2",
                                                file_name_mcmc_posterior_read = config_gen["data_dirs"]["TEST_DIR_SRC"] + config_gen["file_names"]["TEST_MCMC_OUTPUT_ABCDFGHK"],
                                                file_name_teff_data_read = config_gen["data_dirs"]["TEST_DIR_SRC"] + config_gen["file_names"]["TEST_READIN_TREND_TEFF_VS_BALMER"],
                                                soln_write_name = config_gen["data_dirs"]["TEST_DIR_BIN"] + config_gen["file_names"]["CALIB_SOLN"],
                                                model_type_override = "abcdfghk", 
                                                test_flag=True)
    
    test_abcdfghk = inst_abcdfghk.run_step(attribs=config_gen)

    # assert correct type and expected cols exist
    assert isinstance(test_abcdfghk,fits.hdu.table.BinTableHDU)
    assert test_abcdfghk.columns["a"]
    assert test_abcdfghk.columns["k"]


def test_CornerPlot():

    # get a sample of the MCMC posterior data after being read in, and check the column
    # numbers are consisten with the model
    inst_abcdfghk = run_emcee.CornerPlot(module_name="test2",
                                         file_name_mcmc_posterior_read = config_gen["data_dirs"]["TEST_DIR_SRC"] + config_gen["file_names"]["TEST_MCMC_OUTPUT_ABCDFGHK"],
                                         plot_corner_write = config_gen["data_dirs"]["TEST_DIR_BIN"] + "test_abcdfghk_plot.png")

    mcmc_sample_abcdfghk = inst_abcdfghk.run_step(attribs=config_gen)

    # assert column numbers are N_coeff + 1 (1 extra from index column)
    assert len(mcmc_sample_abcdfghk.columns) == 8


def test_lnprob():

    ln_prior_4_likel_good = run_emcee.lnprob(walker_pos_array=coeffs_4_test,
                                            Teff_pass=Teff,
                                            measured_H_pass=Bal_test,
                                            measured_F_pass=Feh_test,
                                            measured_K_pass=Caiik_test,
                                            err_measured_H_pass=err_Bal_test,
                                            err_measured_F_pass=err_Feh_test,
                                            err_measured_K_pass=err_Caiik_ew_test)

    ln_prior_4_likel_bad = run_emcee.lnprob(walker_pos_array=[10.,4.,22.,5.],
                                            Teff_pass=Teff,
                                            measured_H_pass=Bal_test,
                                            measured_F_pass=Feh_test,
                                            measured_K_pass=Caiik_test,
                                            err_measured_H_pass=err_Bal_test,
                                            err_measured_F_pass=err_Feh_test,
                                            err_measured_K_pass=err_Caiik_ew_test)

    ln_prior_8_likel_good = run_emcee.lnprob(walker_pos_array=coeffs_8_test,
                                            Teff_pass=Teff,
                                            measured_H_pass=Bal_test,
                                            measured_F_pass=Feh_test,
                                            measured_K_pass=Caiik_test,
                                            err_measured_H_pass=err_Bal_test,
                                            err_measured_F_pass=err_Feh_test,
                                            err_measured_K_pass=err_Caiik_ew_test)

    ln_prior_8_likel_bad = run_emcee.lnprob(walker_pos_array=[10.,4.,22.,5.,1.,1.,1.,1.],
                                            Teff_pass=Teff,
                                            measured_H_pass=Bal_test,
                                            measured_F_pass=Feh_test,
                                            measured_K_pass=Caiik_test,
                                            err_measured_H_pass=err_Bal_test,
                                            err_measured_F_pass=err_Feh_test,
                                            err_measured_K_pass=err_Caiik_ew_test)

    assert round(ln_prior_4_likel_good, 3) == -11.474
    assert ln_prior_4_likel_bad == -np.inf
    assert round(ln_prior_8_likel_good, 3) == -10.959
    assert ln_prior_8_likel_bad == -np.inf


def test_lnprior():

    # for 4 coefficients
    lnprior_4_test_good = run_emcee.lnprior(theta=[a_layden,b_layden,c_layden,d_layden])
    lnprior_4_test_bad = run_emcee.lnprior(theta=[a_layden,6.,c_layden,d_layden])

    # for 8 coefficients
    lnprior_8_test_good = run_emcee.lnprior(theta=coeffs_8_test)
    lnprior_8_test_bad = run_emcee.lnprior(theta=[a_layden,6.,c_layden,d_layden,1.,1.,1.,1.])

    assert round(lnprior_4_test_good, 3) == 0.000
    assert lnprior_4_test_bad == -np.inf
    assert round(lnprior_8_test_good, 3) == 0.000
    assert lnprior_8_test_bad == -np.inf


def test_function_K():

    k_4_test = run_emcee.function_K(coeffs_pass=coeffs_4_test,
                                Bal_pass=Bal_test,
                                F_pass=Feh_test)

    k_8_test = run_emcee.function_K(coeffs_pass=coeffs_8_test,
                                Bal_pass=Bal_test,
                                F_pass=Feh_test)

    assert round(k_4_test, 3) == 0.394
    assert round(k_8_test, 3) == 0.320


def test_LM_fit():
    # tests the Levenberg-Marquardt fitting functionality

    # these are arrays of fake data (as opposed to single values), to make
    # sure the residuals are in array form, and to fit functions in the first place

    # set arbitrary Balmer, FeH arrays
    test_balmer_ew_array = np.array([4.7, 6.2, 7.8, 9.1, 10.3, 11.2, 14.6, 15.05, 17.2])
    test_feh_array = np.array([-1.5, -1.1, -0.9, -0.4, 0.1, 0.25, 0.3, 0.35, 0.4])

    # generate theoretical values with chosen coefficients and fake EW and FeH data
    test_caiik_ew_array_4 = run_emcee.function_K(coeffs_pass=coeffs_4_test,
                                        Bal_pass=test_balmer_ew_array,
                                        F_pass=test_feh_array)
    test_caiik_ew_array_8 = run_emcee.function_K(coeffs_pass=coeffs_8_test,
                                        Bal_pass=test_balmer_ew_array,
                                        F_pass=test_feh_array)

    # add some noise
    test_caiik_ew_array_4 = np.add(test_caiik_ew_array_4,np.random.normal(loc=0.0, scale=0.001, size=len(test_balmer_ew_array)))
    test_caiik_ew_array_8 = np.add(test_caiik_ew_array_8,np.random.normal(loc=0.0, scale=0.001, size=len(test_balmer_ew_array)))

    # do the fitting
    coeffs_4_test_fitted = least_squares(run_emcee.K_residual, x0=[1,1,1,1],
                                        args=(test_balmer_ew_array, test_feh_array, test_caiik_ew_array_4),
                                        method="lm")
    coeffs_8_test_fitted = least_squares(run_emcee.K_residual, x0=[1,1,1,1,1,1,1,1],
                                        args=(test_balmer_ew_array, test_feh_array, test_caiik_ew_array_8),
                                        method="lm")

    # assert that the fitted coefficients are effectively the same as the ones
    # which were chosen for generating the test data
    assert np.allclose(
                        np.round(coeffs_4_test_fitted.x, decimals=1),
                        np.round(coeffs_4_test, decimals=1),
                        atol=0.2
                        )
    assert np.allclose(
                        np.round(coeffs_8_test_fitted.x, decimals=1),
                        np.round(coeffs_8_test, decimals=1),
                        atol=0.2
                        )



def test_sigma_Km_sqd():

    # case of 4 coefficients
    sigma_Km_4_sqd = run_emcee.sigma_Km_sqd(
                                        coeffs_pass=np.array([2.4,5.3,4.5,4.9]),
                                        Bal_pass=6.3,
                                        err_Bal_pass=0.33,
                                        Feh_pass=-0.14,
                                        err_Feh_pass=0.11
                                        )

    # case of 8 coefficients
    sigma_Km_8_sqd = run_emcee.sigma_Km_sqd(
                                        coeffs_pass=np.array([2.4,5.3,4.5,4.9,0.5,0.32,-0.12,-0.03]),
                                        Bal_pass=6.3,
                                        err_Bal_pass=0.33,
                                        Feh_pass=-0.14,
                                        err_Feh_pass=0.11
                                        )

    assert round(sigma_Km_4_sqd, 3) == 17.456
    assert round(sigma_Km_8_sqd, 3) == 24.786


def test_chi_sqd_fcn():

    # find chi-squared for 4 and 8 coeff models

    chi_sq_4_test_i = run_emcee.chi_sqd_fcn(Bal_pass=Bal_test,
                            Feh_pass=Feh_test,
                            Caiik_pass=Caiik_test,
                            sig_Bal_pass=err_Bal_test,
                            sig_Feh_pass=err_Feh_test,
                            sig_Caiik_pass=err_Caiik_ew_test,
                            coeffs_pass=coeffs_4_test)

    chi_sq_8_test_i = run_emcee.chi_sqd_fcn(Bal_pass=Bal_test,
                            Feh_pass=Feh_test,
                            Caiik_pass=Caiik_test,
                            sig_Bal_pass=err_Bal_test,
                            sig_Feh_pass=err_Feh_test,
                            sig_Caiik_pass=err_Caiik_ew_test,
                            coeffs_pass=coeffs_8_test)

    assert round(chi_sq_4_test_i, 3) == 1.346
    assert round(chi_sq_8_test_i, 3) == 1.286


def test_RunEmcee():

    emcee_instance_test = run_emcee.RunEmcee(module_name="test1",
                                             file_name_scraped_ews_good_only_read=config_gen["data_dirs"]["TEST_DIR_SRC"]  + "test_restacked_ew_info_good_only.csv",
                                             file_name_write_mcmc_text_write=config_gen["data_dirs"]["TEST_DIR_BIN"] + "test_write_mcmc_output.csv")

    # instantiation works
    assert emcee_instance_test
