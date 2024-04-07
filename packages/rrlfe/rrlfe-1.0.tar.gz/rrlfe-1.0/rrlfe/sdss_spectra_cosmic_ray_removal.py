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


# compile the C spectral normalization script
#compile_normalization.compile_bkgrnd()


def fyi_plot(flagged_empirical_pass, df_mean_pass, matching_pass, saved_pathname):

    fig = plt.figure(figsize=(24,10))
    plt.plot(flagged_empirical_pass["wavel"],np.subtract(flagged_empirical_pass["flux_flag_1"],1),color="gray",alpha=1)
    #.axvline(x=0, ymin=0, ymax=1
    plt.plot(flagged_empirical_pass["wavel"],flagged_empirical_pass["diff"],label="diff")
    plt.plot(df_mean_pass["wavel"],np.add(df_mean_pass["avg_flux"],0.2),label="mean")
    plt.plot(flagged_empirical_pass["wavel"],flagged_empirical_pass["flux"],label="empirical")
    #plt.plot(df_single_p["wavel"].where(test["flux_flag_1"] == True),
    #             df_single_p["flux"].where(test["flux_flag_1"] == True),
    #         label="flagged",color="k",linewidth=4)
    plt.plot([3900,5000],[limit,limit],linestyle="--")
    plt.title(str(os.path.basename(matching_pass[p])))
    plt.legend(loc="lower right")
    plt.savefig(str(os.path.basename(matching_pass[p])).split(".")[-2] + ".png",
                facecolor="white", edgecolor='white')
    plt.clf()


def flag_from_avg(df_empir_pass,df_avg_pass,df_median_pass,sigma_choice=1):
    '''
    Average two spectra and flag points based on their deviation from the average spectrum

    INPUTS:
    df_empir_pass: dataframe of empirical spectrum
    df_avg_pass: dataframe of average spectrum
    df_median_pass: dataframe of median spectrum
    sigma_choice: threshold for clipping
    '''

    # initialize DataFrame to return
    masked_spec = df_empir_pass.copy(deep=True)
    #masked_spec["flux_masked_1"] = masked_spec["flux"]

    # take difference between empirical spectrum and the AVERAGE of the AVERAGE AND MEDIAN spectrum
    # (note this preserves sign information, and (if only 2 spectra are being compared) protects against
    # misidentification of a cosmic ray in 1 spectrum when the ray is actually in the other)
    #initialize DataFrame for taking an average of some kind
    standin_df = df_avg_pass.copy(deep=True)
    standin_df["median_flux"] = df_median_pass["median_flux"]
    # remove column of wavelengths
    #print(standin_df.keys())
    standin_df = standin_df.drop(labels=["wavel"],axis=1)
    # find the mean of a mean and a median
    standin_df["mean_of_stuff"] = standin_df.mean(axis=1) # average of the columns

    #avg_flux = np.expand_dims(df_avg_pass["avg_flux"].values,axis=1)
    #median_flux = np.expand_dims(df_median_pass["median_flux"].values,axis=1)
    #print(np.expand_dims(avg_flux,axis=0).shape)
    #print(median_flux.shape)
    #mean_median_combo = np.mean(avg_flux,median_flux)
    masked_spec["diff"] = np.subtract(df_empir_pass["flux"],standin_df["mean_of_stuff"])

    # mask deviant points
    # logic: is difference in the array beyond error bounds?
    error_bound = sigma_choice*np.nanstd(masked_spec["diff"])
    logic_1 = np.greater(masked_spec["diff"],error_bound)
    masked_spec["flux_flag_1"] = logic_1 # flag these points as suspect

    return masked_spec, error_bound


def main():

    # top-level directory for SDSS spectra cosmic ray removal, and sub-directories
    stem_s82_norm = "/Users/bandari/Documents/git.repos/rrlyrae_metallicity/rrlyrae_metallicity/" + \
                    "sdss_spectra_cosmic_ray_removal/"
    dir_before_any_normalization = "00_originals_pre_any_normalization/"

    dir_normalized_first = "01a_all_normalized_once/"
    dir_1st_inspect_manually = "01b_plots_to_inspect_manually/"
    dir_1st_masks = "01f_masks"

    dir_normalized_w_1st_masks_new_list = "02a_normalized_w_1st_masks_new_list"
    dir_2nd_inspect_manually = "02b_plots_to_inspect_manually"
    dir_2nd_masks = "02f_masks"

    dir_normalized_w_2nd_masks = "03_normalized_w_2nd_masks"

    # find individual file names of spectra for which continuum has been calculated
    file_list = glob.glob(stem_s82_norm + dir_normalized_first + "/*")
    # find all parent names (i.e., one name for each target, whether or not multiepoch observations were made)
    parent_list = list(set([i.split("g00")[0] for i in file_list]))
    #import ipdb; ipdb.set_trace()

    # find the file names of spectra corresponding to each parent; if there is only 1, ignore;
    # if >= 2, do median comparison to flag it for cosmic rays
    counter1 = 0 # to check for thoroughness
    counter2 = 0
    counter3 = 0
    counter4 = 0
    for t in range(0,len(parent_list)):

        matching = list(filter(lambda x: parent_list[t] in x, file_list))

        print("-------------------------")

        if (len(matching) == 1):
            #import ipdb; ipdb.set_trace()

            df_dummy = pd.read_csv(matching[0], names=["wavel","flux","noise"], delim_whitespace=True)
            fig_file_name = stem_s82_norm + dir_1st_inspect_manually + \
                        str(os.path.basename(matching[0])).split(".")[-2] + ".png"

            # simply write out FYI image to the dir to inspect by hand
            fig = plt.figure(figsize=(24,10))
            plt.plot(df_dummy["wavel"],df_dummy["flux"])
            plt.title("One spec only, " + str(os.path.basename(matching[0])))
            plt.savefig(fig_file_name,
                        facecolor="white", edgecolor='white')
            plt.clf()
            print("Figure written out as " + fig_file_name)

            counter1 += 1

            '''

            df_dummy.to_csv(stem_s82_norm + dir_inspect_manually + os.path.basename(matching[0]))
            print("Only one match found; writing directly to csv:")
            print(stem_s82_norm + dir_inspect_manually + os.path.basename(matching[0]))
            '''


        elif (len(matching) >= 2):

            print(str(len(matching)) + " matches found:")
            print(matching)

            # dictionary to hold dataframes
            d = {}

            # intialize array to contain all fluxes
            df_dummy = pd.read_csv(matching[0], names=["wavel","flux","noise"], delim_whitespace=True)
            aggregate_flux_array = np.nan*np.ones((len(df_dummy),len(matching)))

            # collect spectra in single dictionary
            for p in range(0,len(matching)):

                df_single_p = pd.read_csv(matching[p], names=["wavel","flux","noise"], delim_whitespace=True)

                # delineate where the absorption lines are
                '''
                Recall
                3933.66-30 # CaII-K
                3970.075 # H-eps
                4101.71 # H-del
                4340.472 # H-gam
                4861.29 # H-beta
                '''
                caii_K_line = np.logical_and(df_single_p["wavel"] >= 3933.66-30,df_single_p["wavel"] <= 3933.66+30)
                h_eps_line = np.logical_and(df_single_p["wavel"] >= 3970.075-30,df_single_p["wavel"] <= 3970.075+30)
                h_del_line = np.logical_and(df_single_p["wavel"] >= 4101.71-30,df_single_p["wavel"] <= 4101.71+30)
                h_gam_line = np.logical_and(df_single_p["wavel"] >= 4340.472-30,df_single_p["wavel"] <= 4340.472+30)
                h_beta_line = np.logical_and(df_single_p["wavel"] >= 4861.29-30,df_single_p["wavel"] <= 4861.29+30)
                # sum across the arrays
                sum_array = np.sum([np.array(caii_K_line),
                                    np.array(h_eps_line),
                                    np.array(h_del_line),
                                    np.array(h_gam_line),
                                    np.array(h_beta_line)],axis=0)
                # convert to boolean (True = 'there is an absorption line here')
                line_bool_array = np.array(sum_array, dtype=bool)

                # sanity check that wavelength abcissa are the same
                if p==0:
                    # for checking wavel abcissa is same
                    wavel_initial = df_single_p["wavel"].values
                else:
                    if len(np.setdiff1d(df_single_p["wavel"].values,wavel_initial) >= 1):
                        print("Hey, the wavelength abcissas are not the same!")
                        sys.exit()

                # put fluxes into array
                aggregate_flux_array[:,p] = df_single_p["flux"].values

            # take mean flux of all the spectra
            mean_flux_array = np.mean(aggregate_flux_array,axis=1)

            # cast mean spectrum data as DataFrame
            df_mean = pd.DataFrame(mean_flux_array,columns=["avg_flux"])
            df_mean["wavel"] = df_single_p["wavel"] # uses last spectrum read in
            # include median flux too (important for identifying cosmic rays when only 2 spectra are compared)
            median_flux_array = np.median(aggregate_flux_array,axis=1)
            #print(median_flux_array)
            df_median = pd.DataFrame(median_flux_array,columns=["median_flux"])
            df_median["wavel"] = df_single_p["wavel"] # uses last spectrum read in
            #mean_flux_array["median_flux"] = pd.Series(median_flux_array.tolist())

            for p in range(0,len(matching)):
                # test each empirical spectrum against the mean, and flag points
                df_single_p = pd.read_csv(matching[p], names=["wavel","flux","noise"], delim_whitespace=True)
                flagged_empirical, limit = flag_from_avg(
                                                        df_empir_pass = df_single_p,
                                                        df_avg_pass = df_mean,
                                                        df_median_pass = df_median,
                                                        sigma_choice=5
                                                        )


                if np.any(np.where(flagged_empirical["flux_flag_1"])):
                    # if there are cosmic ray candidates (i.e., if the list of them
                    # is not empty)
                    print(len(np.where(flagged_empirical["flux_flag_1"])))
                    #import ipdb; ipdb.set_trace()

                    if (np.logical_and(flagged_empirical["flux_flag_1"],line_bool_array)).any():
                        # if the cosmic ray appears to be in an absorption line, write image
                        # for manually checking
                        #import ipdb; ipdb.set_trace()
                        #csv_write_name = stem_s82_norm + dir_1st_inspect_manually + os.path.basename(matching[p])
                        fig_write_name = stem_s82_norm + dir_1st_inspect_manually + os.path.basename(matching[p].split(".")[-2]) + ".png"

                        # simply write out FYI image to the dir to inspect by hand
                        fig = plt.figure(figsize=(24,10))
                        plt.plot(df_single_p["wavel"],df_single_p["flux"])
                        plt.plot(flagged_empirical["wavel"],line_bool_array)
                        plt.plot([3900,5000],[limit,limit],linestyle="--")
                        plt.title("Possible ray in line, " + str(os.path.basename(matching[p])))
                        plt.savefig(fig_write_name,
                                    facecolor="white", edgecolor='white')
                        plt.clf()
                        print("Flagged pixels appear in absorption line; figure written out as " + fig_write_name)

                        counter2 += 1

                        '''
                        df_dummy.to_csv(csv_write_name)
                        print("Flagged pixels appear in absorption line; writing directly to csv:")
                        print(csv_write_name)
                        fyi_plot(flagged_empirical_pass=flagged_empirical,
                                df_mean_pass=df_mean,
                                matching_pass=matching,
                                saved_pathname=fig_write_name)
                        '''


                    else:
                        # there is >=1 apparent cosmic ray(s), and NOT inside a line,
                        # write out a mask of those points

                        # retrieve the ORIGINAL spectrum
                        #stem_s82_norm + "../rrlyrae_metallicity/src/s82_spectra/original_ascii_files/"

                        # mask points
                        #import ipdb; ipdb.set_trace()
                        #stem_s82_norm + dir_1st_masks
                        #flagged_empirical["wavel"]

                        csv_write_name = stem_s82_norm + dir_1st_masks + "/mask1_" + os.path.basename(matching[p])
                        flagged_empirical.to_csv(csv_write_name, columns = ["wavel","flux_flag_1"])
                        print("Wrote mask of spectrum with apparent ray: " + csv_write_name)

                        counter3 += 1

                        '''
                        df_original_unnorm = pd.read_csv(stem_s82_norm,names=["wavel","flux","noise"], delim_whitespace=True)
                        #df_single_p =

                        # write out

                        fig_write_name = stem_s82_norm + dir_to_normalize_second + os.path.basename(matching[p].split(".")[0]) + ".png"
                        df_dummy.to_csv(csv_write_name)

                        print(csv_write_name)
                        fyi_plot(flagged_empirical_pass=flagged_empirical,
                                df_mean_pass=df_mean,
                                matching_pass=matching,
                                saved_pathname=fig_write_name)


                        # Take list of unnormalized empirical spectra and noise-churned the
                        # spectra, normalize them, and write out normalizations
                        create_spec_realizations.create_spec_realizations_main(num = 1,
                                                                               input_spec_list_dir = "./src/",
                                                                               input_list = "s82_ascii_files.list",
                                                                               unnorm_empirical_spectra_dir = stem_s82_norm + "../rrlyrae_metallicity/src/s82_spectra/original_ascii_files/",
                                                                               unnorm_noise_churned_spectra_dir = stem_s82_norm + intermediary_noise_churn,
                                                                               bkgrnd_output_dir = stem_s82_norm + "bkgrnd_output/",
                                                                               final_dir = stem_s82_norm + dir_normalized_second,
                                                                               noise_level="None",
                                                                               spec_file_type="ascii.no_header")
                        '''
                elif not np.any(np.where(flagged_empirical["flux_flag_1"])):
                    # if there are no identified cosmic rays (i.e., if the list of them
                    # is empty), just write out the mask of points also--a mask with all False
                    #import ipdb; ipdb.set_trace()
                    csv_write_name = stem_s82_norm + dir_1st_masks + "/mask1_" + os.path.basename(matching[p])
                    flagged_empirical.to_csv(csv_write_name, columns = ["wavel","flux_flag_1"])
                    print("Wrote mask of spectrum with NO apparent ray: " + csv_write_name)

                    counter4 += 1

                else:
                    print("Condition unknown!")
                    import ipdb; ipdb.set_trace()

    print("counter1: " + str(counter1))
    print("counter2: " + str(counter2))
    print("counter3: " + str(counter3))
    print("counter4: " + str(counter4))


if __name__ == "__main__":
    main()
