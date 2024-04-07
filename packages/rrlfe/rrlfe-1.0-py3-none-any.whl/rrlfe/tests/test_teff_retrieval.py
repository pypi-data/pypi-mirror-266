#!/usr/bin/env python
# coding: utf-8

# This makes plots showing the effective temperature retrievals based on synthetic spectra
# produced by R.W.

# Created from parent restacking_scraped_data.ipynb 2021 March 17 by E.S.

import pandas as pd
import os, sys
from astropy.io.fits import getdata
from configparser import ConfigParser, ExtendedInterpolation
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

current_dir = os.path.dirname(__file__)
target_dir = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, target_dir)

from . import *
from rrlfe import teff_retrieval
from conf import *

# configuration data for reduction
config_gen = ConfigParser(interpolation=ExtendedInterpolation()) # for parsing values in .init file
# config for reduction to find a, b, c, d
config_gen.read(os.path.join(os.path.dirname(__file__), '../conf', 'config_gen.ini'))

def test_TempVsBalmer(test_df_poststack_file_name_read = config_gen["data_dirs"]["TEST_DIR_SRC"]+config_gen["file_names"]["TEST_RESTACKED_EW_DATA_W_METADATA_STANDALONE"],
                        test_df_poststack_file_name_write = config_gen["data_dirs"]["TEST_DIR_SRC"]+config_gen["file_names"]["TEST_RESTACKED_EW_DATA_GOOD_ONLY_TEFFFIT"],
                        test_teff_data_write = config_gen["data_dirs"]["TEST_DIR_BIN"] + config_gen["file_names"]["TEST_TREND_TEFF_VS_BALMER"]):


    inst = teff_retrieval.TempVsBalmer(module_name = "test1",
                                       file_ew_poststack_read = test_df_poststack_file_name_read,
                                            file_ew_tefffit_write = test_teff_data_write,
                                            plot_tefffit_write = "dummy.png",
                                            data_tefffit_write = test_df_poststack_file_name_write,
                                            plot=False,
                                            test_flag=True)
    
    df_test = inst.run_step(attribs = config_gen)

    # check that returned filetype is a pandas dataframe, and that new column 'teff_bestfit' exists
    assert isinstance(df_test, pd.DataFrame)
    assert 'teff_bestfit' in df_test.keys()


# needs fake data
def test_line_fit_temp_range(test_df_poststack_file_name_read = config_gen["data_dirs"]["TEST_DIR_SRC"]+config_gen["file_names"]["TEST_RESTACKED_EW_DATA_W_METADATA_STANDALONE"]):

    # read in data
    df_poststack = pd.read_csv(test_df_poststack_file_name_read)

    # find linear trend of net Balmer EW with Teff
    teff_test = df_poststack["teff"].values.astype(float)
    # fit a straight line: net Balmer
    ews_Balmer_test = df_poststack["EW_Balmer"].values.astype(float)

    m_test, err_m_test, b_test, err_b_test = teff_retrieval.line_fit_temp_range(x_data_pass=ews_Balmer_test, y_data_pass=teff_test, t_min=5900, t_max=7350)

    # check line is being fit correctly
    assert round(m_test, 2) == 192.76
    assert round(b_test, 2) == 5433.73
