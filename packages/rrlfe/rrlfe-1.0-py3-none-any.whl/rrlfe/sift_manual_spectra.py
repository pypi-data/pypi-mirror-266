
# This reads in pngs, displays them, and the user decides whether to
# 1) has rays in absorption lines and should be discarded ('d')
# 2) is spectrum with no rays ('n')
# 3) is spectrum with rays and needs to be handled manually ('w')

# importing matplotlib modules
import matplotlib.image as mpimg
import matplotlib.pyplot as plt

import glob
import os

# file list
file_list = glob.glob("/Users/bandari/Documents/git.repos/rrlyrae_metallicity/"+\
                    "rrlyrae_metallicity/sdss_spectra_cosmic_ray_removal/01b_plots_to_inspect_manually/*png")
print(file_list)

# Read Images
mng = plt.get_current_fig_manager()
mng.full_screen_toggle()
for file_num in range(0,len(file_list)):

    # initialize lists of file names
    disc = open("discard.txt","a+") # d: 'discard'
    norays = open("norays.txt","a+") # g: 'good'
    handleman = open("handleman.txt","a+") # c: 'cosmic ray'

    img = mpimg.imread(file_list[file_num])

    # Output Images
    fig = plt.figure(figsize=(20,10))
    plt.imshow(img)
    plt.show()

    choice = input("[d]isc/[g]ood/[c]osmic: ")

    plt.clf()

    dat_file_name = os.path.basename(file_list[file_num]).split(".")[-2]+".dat"
    if choice == "d":
        disc.write(dat_file_name+"\n")
        disc.close()
    elif choice == "g":
        norays.write(dat_file_name+"\n")
        norays.close()
    elif choice == "c":
        handleman.write(dat_file_name+"\n")
        handleman.close()
    else:
        print("Unacceptable!")
    print(dat_file_name + " written to file.")
