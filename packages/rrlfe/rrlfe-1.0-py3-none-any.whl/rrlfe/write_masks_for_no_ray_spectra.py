#!/usr/bin/env python
# coding: utf-8

# This tests algorithms to remove cosmic rays from multiepoch spectra (in particular from SDSS stripe 82
# spectra, which are too many for manual removal)

# Created 2021 May 10 by E.S.

'''
Order of operations:

1.) Flag cosmic rays in spectra that have been normalized once; copy unique spectra
    (i.e., those with only 1 per object) to directory X
2.) Mask those pixels, and move spectra with flagged pixels inside absorption lines to directory X
3.) Inspect latter by hand (discard ones with rays inside lines, put others back in with the others)
4.) Normalize the spectra a second time
5.) Flag rays as before, but perhaps with slightly tighter constraints
6.) Mask those pixels, and move spectra to another directory (don't bother checking ones by hand)
7.) Normalize one last time
'''

import pandas as pd
import numpy as np
import glob
import sys
import os
import matplotlib.pyplot as plt
from astropy.stats import sigma_clip

def main():

    # read list of names of no-ray files to write masks for
    stem = "/Users/bandari/Documents/git.repos/rrlyrae_metallicity/rrlyrae_metallicity/"
    list_file_name = "norays_all_cleaned.txt"
    list_file_df = pd.read_csv(stem + list_file_name, names=["file_name"])

    dir_normalized_first = "01a_all_normalized_once/"
    dir_1st_masks = "01f_masks"

    # loop over the files in the list, and write out masks (which are all 'False'
    # since there are no rays in them)
    # loop over each file
    for file_num in range(0,len(list_file_df)):

        # read in the file
        read_in_file_name = stem + "sdss_spectra_cosmic_ray_removal/01a_all_normalized_once/" + \
                                    list_file_df["file_name"].iloc[file_num] + "_000"
        print("Reading in " + read_in_file_name)
        df_spec = pd.read_csv(read_in_file_name, names=["wavel","flux"], delim_whitespace=True)

        flagged_df = pd.DataFrame(df_spec["wavel"].copy())
        flagged_df["flux_flag_1"] = False

        csv_write_name = stem + "sdss_spectra_cosmic_ray_removal/" + dir_1st_masks + "/mask1_" + os.path.basename(read_in_file_name)

        # check if the mask already exists
        # Use this function to search for any files which match your filename
        files_present = glob.glob(csv_write_name)
        # if no matching files, write to csv, if there are matching files, print statement
        if not files_present:
            flagged_df.to_csv(csv_write_name, columns = ["wavel","flux_flag_1"])
            print("Wrote mask of spectrum with apparent ray: " + csv_write_name)
        else:
            print("WARNING: This file already exists!")

        print("-------------------")


if __name__ == "__main__":
    main()
