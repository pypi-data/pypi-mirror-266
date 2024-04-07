#!/usr/bin/env python
# coding: utf-8

# This reads in UN-normalized SDSS spectra and masks and
# 1.) Interpolates masked regions which are outside absorption lines (to preserve normalization)
# 2.) Masks regions which are located inside lines completely (to avoid messing with the EWs; note there
#      should not be many such cases--- most spectra with cosmic rays in the lines were discarded)

# Parent notebook created 2021 June 27 by E.S.

import pandas as pd
#from astropy.io import fits
#import multiprocessing
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
import glob
import os

stem = "/Users/bandari/Documents/git.repos/rrlyrae_metallicity/rrlyrae_metallicity/sdss_spectra_cosmic_ray_removal/"

## BEGIN USER INPUTS HERE
# glob in list of unnormalized files to use
unnorm_file_list = glob.glob(stem + "02a_unnormalized_post_mask/" + "*dat")
# glob in list of masks
mask_dir = "02c_masks_2nd_round/"
mask_file_list = glob.glob(stem + mask_dir + "*dat*")
spec_write_dir = "03a_post_2nd_mask_pre_any_normalization/"
plot_write_dir = "03b_plots_post_2nd_mask_unnormalized/"
ray_in_line = "discard" # what to do if a ray is found in a line (discard/interpolate)
## END USER INPUTS

# for each unnormalized spectrum, find the matching mask
dict_files_masks = {"spec_file_name": unnorm_file_list}
df_files_masks = pd.DataFrame.from_dict(dict_files_masks)
df_files_masks["mask_file_name"] = ""
mask_file_array = np.asarray(mask_file_list)

print("Matching masks with spectral files...")

# loop over spectral files to fill in corresponding masks
for file_num in range(0,len(df_files_masks)):

    # if spec name is in mask name
    this_spec = os.path.basename(df_files_masks["spec_file_name"].iloc[file_num])
    mask_exists = np.flatnonzero(np.core.defchararray.find(mask_file_array,this_spec)!=-1)

    if (mask_exists.size > 0):
        df_files_masks["mask_file_name"].iloc[file_num] = os.path.basename(mask_file_array[mask_exists][0])

# loop over all spectra
for spec_num in range(0,len(df_files_masks)):

    print("Doing spec num " + str(spec_num) + " of " + str(len(df_files_masks)))
    print(df_files_masks["spec_file_name"][spec_num])

    cond_count = 0 # FYI; initialize to count the two types of artifacts: 2= inside and outside absorption lines

    # read in the spectrum and the mask
    this_spectrum = pd.read_csv(df_files_masks["spec_file_name"][spec_num], delim_whitespace = True,
                                names=["wavel","unnorm_flux","noise"])

    # if mask exists (if not, the spectrum was discarded entirely)
    try:
        this_mask = pd.read_csv(stem + mask_dir + df_files_masks["mask_file_name"][spec_num])
    except:
        continue

    # where masked pixels are INSIDE absorption lines, remove wavelength, flux, and noise values from the
    # data entirely

    # delineate where the absorption lines are
    '''
    Recall
    3933.66-30 # CaII-K
    3970.075 # H-eps
    4101.71 # H-del
    4340.472 # H-gam
    4861.29 # H-beta
    '''
    caii_K_line = np.logical_and(this_spectrum["wavel"] >= 3933.66-30,this_spectrum["wavel"] <= 3933.66+30)
    h_eps_line = np.logical_and(this_spectrum["wavel"] >= 3970.075-30,this_spectrum["wavel"] <= 3970.075+30)
    h_del_line = np.logical_and(this_spectrum["wavel"] >= 4101.71-30,this_spectrum["wavel"] <= 4101.71+30)
    h_gam_line = np.logical_and(this_spectrum["wavel"] >= 4340.472-30,this_spectrum["wavel"] <= 4340.472+30)
    h_beta_line = np.logical_and(this_spectrum["wavel"] >= 4861.29-30,this_spectrum["wavel"] <= 4861.29+30)

    # sum across the arrays
    sum_array = np.sum([np.array(caii_K_line),
                        np.array(h_eps_line),
                        np.array(h_del_line),
                        np.array(h_gam_line),
                        np.array(h_beta_line)],axis=0)
    # convert to boolean (True = 'there is an absorption line here')
    line_bool_array = np.array(sum_array, dtype=bool)
    # inversion to denote regions OUTSIDE lines
    outside_line_bool_array = ~line_bool_array

    #matches_inside_line =
    #print(np.where(matches_inside_line == True))

    # indices of cosmic ray artifacts inside absorption lines...
    idx_2_drop_pre = this_mask.index[np.logical_and(this_mask["flux_flag_1"],line_bool_array)].tolist()

    # add adjacent indices
    idx_2_drop_add_1 = list(map(lambda x : x + 1, idx_2_drop_pre))
    idx_2_drop_subt_1 = list(map(lambda x : x - 1, idx_2_drop_pre))
    idx_2_drop_expanded = idx_2_drop_add_1 + idx_2_drop_pre + idx_2_drop_subt_1
    idx_2_drop = list(set(idx_2_drop_expanded)) # remove duplicates
    # remove any appearance of index -1 or 786 (which go off the ends of the axis)
    idx_2_drop = [x for x in idx_2_drop if np.logical_and(x > -1,x < 786)]

    # ... and outside absorption lines
    idx_2_interp_pre = this_mask.index[np.logical_and(this_mask["flux_flag_1"],outside_line_bool_array)].tolist()
    # add adjacent indices
    idx_2_interp_add_1 = list(map(lambda x : x + 1, idx_2_interp_pre))
    idx_2_interp_subt_1 = list(map(lambda x : x - 1, idx_2_interp_pre))
    idx_2_interp_expanded = idx_2_interp_add_1 + idx_2_interp_pre + idx_2_interp_subt_1
    idx_2_interp = list(set(idx_2_interp_expanded)) # remove duplicates

    # remove any appearance of index -1 or 786 (which go off the ends of the axis)
    idx_2_interp = [x for x in idx_2_interp if np.logical_and(x > -1,x < 786)]

    if np.logical_and(len(idx_2_drop_pre)>0,ray_in_line == "discard"):
        print("Rays in lines; skipping spectrum " + str(df_files_masks["spec_file_name"][spec_num]))
        continue # skip this spectrum

    # if there are cosmic ray artifacts in an absorption line, remove these rows from the spectrum
    if idx_2_drop:
        this_spectrum_dropped = this_spectrum.drop(axis=0, index=idx_2_drop)
        #print("Artifacts found INside absorption lines.")
        cond_count+=1

    else:
        # note that nothing has actually been dropped in this case
        this_spectrum_dropped = this_spectrum.copy(deep=True)
        #print("No artifacts found inside absorption lines.")

    # if there are cosmic ray artifacts outside the absorption lines, interpolate over these
    if idx_2_interp:
        # first, drop the rows corresponding to the artifact
        idx_2_interp_nonunion = list(np.setdiff1d(idx_2_interp,idx_2_drop)) # non-union of indices to drop and interpolate
        this_spectrum_dropped = this_spectrum_dropped.drop(axis=0, index=idx_2_interp_nonunion)
        # then do the interpolation, of the flux and the noise
        wavel_interp = this_mask["wavel"].loc[idx_2_interp_nonunion]
        flux_interp = np.interp(x=wavel_interp,
                                xp=this_spectrum_dropped["wavel"],
                                fp=this_spectrum_dropped["unnorm_flux"])
        noise_interp = np.interp(x=wavel_interp,
                        xp=this_spectrum_dropped["wavel"],
                        fp=this_spectrum_dropped["noise"])

        # append the interpolated points
        dict_2_append = {"wavel":wavel_interp,"unnorm_flux":flux_interp,"noise":noise_interp}
        df_2_append = pd.DataFrame.from_dict(dict_2_append)
        this_spectrum_final = this_spectrum_dropped.append(df_2_append, ignore_index=True, verify_integrity=True)
        #print("Artifacts found OUTside absorption lines.")

        # sort, in case the normalization routine or Robospect are picky
        this_spectrum_final = this_spectrum_final.sort_values(by=["wavel"])
        cond_count+=1

    else:
        this_spectrum_final = this_spectrum_dropped.copy(deep=True)
        #print("No artifacts found outside absorption lines.")

    write_plot_name = stem + plot_write_dir + os.path.basename(df_files_masks["spec_file_name"][spec_num]) + ".png"
    plt.clf()
    plt.rcParams["figure.figsize"] = (20,3)
    plt.plot(this_mask["wavel"],100*this_mask["flux_flag_1"])
    plt.plot(this_spectrum_dropped["wavel"],np.add(20.,this_spectrum_dropped["unnorm_flux"]),label="dropped")
    plt.plot(this_spectrum["wavel"],np.add(10.,this_spectrum["unnorm_flux"]),marker="o",markersize=2,label="input")
    plt.plot(this_spectrum_final["wavel"],this_spectrum_final["unnorm_flux"],marker="o",markersize=2,label="output")
    plt.title(os.path.basename(df_files_masks["spec_file_name"][spec_num]))
    plt.legend()
    plt.savefig(write_plot_name, dpi=300)

    # write out final spectrum, and save plot
    this_spectrum_final["unnorm_flux"] = this_spectrum_final["unnorm_flux"].map(lambda x: '%.3f' % x) # clean up decimals
    this_spectrum_final["noise"] = this_spectrum_final["noise"].map(lambda x: '%.5f' % x) # clean up decimals
    write_data_name = stem + spec_write_dir + os.path.basename(df_files_masks["spec_file_name"][spec_num])
    this_spectrum_final.to_csv(write_data_name, sep=" ", header=False, index=False)
    print("Wrote out processed unnormzed spectrum file to " + write_data_name)
    print("... and FYI plot to " + write_plot_name)
    print("-----------------")
