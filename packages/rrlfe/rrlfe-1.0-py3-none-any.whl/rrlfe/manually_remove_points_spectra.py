#!/usr/bin/env python
# coding: utf-8

# For enabling user to define where points should be masked out

# Created 2021 June 11 by E.S.

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import glob

### USER INPUTS HERE
# read list of names of files to examine
stem = "/Users/bandari/Documents/git.repos/rrlyrae_metallicity/rrlyrae_metallicity/"
#read_spec_directory = stem + "sdss_spectra_cosmic_ray_removal/01a_all_normalized_once/"
read_spec_directory = stem + "sdss_spectra_cosmic_ray_removal/02a_unnormalized_post_mask/"
#write_mask_directory = stem + "sdss_spectra_cosmic_ray_removal/01f_masks/"
write_mask_directory = stem + "sdss_spectra_cosmic_ray_removal/02c_masks_2nd_round/"
write_mask_prefix = "mask1_" # prefix in file names of masks to be written
#list_file_name = "handleman_all_cleaned.txt"
#list_file_name = "handleman_trunc_20210622_cleaned.txt"
list_file_name = "handleman_2nd_round_trunc_20210711.txt"
## END USER INPUTS

list_file_df = pd.read_csv(stem + list_file_name, names=["file_name"])

'''
not working!!
# enable clicking on plot
def onclick(event):

    global ix, iy
    ix, iy = event.xdata, event.ydata
    print("x = "+str(ix)+", y = "+str(iy))

    global coords
    coords.append((ix, iy))

    if len(coords) == 2:
        fig.canvas.mpl_disconnect(cid)

    return coords
'''

def tellme(s):
    print(s)
    plt.title(s, fontsize=16)
    plt.draw()


# loop over each file
for file_num in range(0,len(list_file_df)):

    # read in the file
    read_in_file_name = read_spec_directory + list_file_df["file_name"].iloc[file_num] # + "_000" # this suffix sometimes necessary
    print("Reading in " + read_in_file_name)
    df_spec = pd.read_csv(read_in_file_name, names=["wavel","flux","noise"], delim_whitespace=True)

    # display interactive plot of spectrum
    plt.clf()
    #fig = plt.figure() #figsize=(20,10))
    #ax = fig.add_subplot(111)
    plt.plot([3900,5000],[1,1],"k--")
    plt.plot(df_spec["wavel"],df_spec["flux"])
    plt.title(list_file_df["file_name"].iloc[file_num])
    plt.show()
    #plt.plot()

    raw_num_rays = input("Enter number of cosmic rays: ")
    if raw_num_rays == "x":
        num_rays = int(0)
    else:
        num_rays = int(raw_num_rays)

    mask_ranges_low = np.nan*np.ones(num_rays)
    mask_ranges_high = np.nan*np.ones(num_rays)

    plt.clf()
    plt.plot([3900,5000],[1,1],"k--")
    plt.plot(df_spec["wavel"],df_spec["flux"])
    plt.title(list_file_df["file_name"].iloc[file_num])
    #plt.show()

    # define bad regions
    '''
    break_statement = 0
    while not break_statement:
        # let user loop over regions that are bad
        fig.canvas.draw()
        cid = fig.canvas.mpl_connect('button_press_event', onclick)
        print(cid)
        break_statement = input("Done finding bad regions? [N]: ") or 0
    '''

    for n_ray in range(0,num_rays):
        pts = []
        while len(pts) < 2:
            tellme('Select 2 limits with mouse')
            pts = np.asarray(plt.ginput(2, timeout=-1))
            if len(pts) < 2:
                tellme('Too few points, starting over')
                time.sleep(1)  # Wait a second

        ph = plt.fill(pts[:, 0], pts[:, 1], 'r', lw=2)

        tellme('Happy? KEY CLICK = yes and done with spectrum; MOUSE CLICK = no; ')

        print(pts[:,0])
        # append
        mask_ranges_low[n_ray] = pts[0, 0]
        mask_ranges_high[n_ray] = pts[1, 0]

        if plt.waitforbuttonpress():
          print("button press")
          plt.close()
          break

        # Get rid of fill
        for p in ph:
            p.remove()

    # wavelength ranges to mask
    #mask_range = input("Input wavelength ranges to mask [[,],[,],...[,]]:")
    #mask_ranges_low = [float(i) for i in input("Input wavelength range lower limits to mask (or 0 to skip): ").split(" ")]
    #mask_ranges_high = [float(i) for i in input("Input wavelength range upper limits to mask (or 0 to skip): ").split(" ")]

    #if (len(mask_ranges_low[0]) == 0):
    #    continue

    #initialize mask
    flagged_interactive = pd.DataFrame(df_spec["wavel"].copy())
    flagged_interactive["flux_flag_1"] = False

    # loop over continuous masked regions
    if (len(mask_ranges_low) != 0):
        for t in range(0,len(mask_ranges_low)):

            region_span = np.logical_and(df_spec["wavel"]>mask_ranges_low[t],df_spec["wavel"]<mask_ranges_high[t])
            #plt.plot(df_spec["wavel"].where(region_span),df_spec["flux"].where(region_span),"k--", marker='o')

            # mask out those elements (True: 'bad'; False: 'good; do not mask')
            flagged_interactive["flux_flag_1"].loc[region_span] = True

            print("Masked cosmic rays")

    else:
        print("No cosmic rays")

    #plt.show()

    # write out mask as found interactively
    csv_write_name = write_mask_directory + write_mask_prefix + list_file_df["file_name"].iloc[file_num] # + "_000" # this suffix sometimes necessary
    # write to file (mode=x to avoid overwrite)
    flagged_interactive.to_csv(csv_write_name, columns = ["wavel","flux_flag_1"], mode='x')
    print("Wrote mask of spectrum as found interactively: " + csv_write_name)
    print("--------------------------")
