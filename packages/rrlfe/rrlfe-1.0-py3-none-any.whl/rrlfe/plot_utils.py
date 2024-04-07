'''
Take data the pipeline has written out, and generate FYI plots
'''

def plot_isometal():

    # plot data points
    cmap = plt.get_cmap(name='jet')
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)

    # make set of colors/markers I can loop over
    colors = ['red', 'blue', 'orange', 'teal', 'black', 'green', 'purple']*10
    markers = ['o', '^', '>', 's', '<']*10

    '''
    for y in range(0, len(unique_star_names)):
        # loop over every star, overlay the set of points for that star on the plot

        x_data = data_to_plot['balmer'].where(
            data_to_plot['star_name'] == unique_star_names[y])
        y_data = data_to_plot['K'].where(
            data_to_plot['star_name'] == unique_star_names[y])

        err_x_data = data_to_plot['err_balmer'].where(
            data_to_plot['star_name'] == unique_star_names[y])
        err_y_data = data_to_plot['err_K'].where(
            data_to_plot['star_name'] == unique_star_names[y])

        empirical_spectrum_names = data_to_plot['original_spec_file_name'].where(
            data_to_plot['star_name'] == unique_star_names[y])

        # plot, and keep the same color for each star
        #color_this_star = cmap(float(y)/len(unique_star_names))
        ax.errorbar(x_data,
                    y_data,
                    yerr=err_y_data,
                    xerr=err_x_data,
                    linestyle='',
                    fmt=markers[y],
                    markerfacecolor=colors[y],
                    color=colors[y])


        bad_phase_locs = np.logical_or(data_to_plot['phase'] > self.max_good,
                                       data_to_plot['phase'] < self.min_good)
        x_data_bad_phase = x_data.where(bad_phase_locs)
        y_data_bad_phase = y_data.where(bad_phase_locs)

        # overplot unfilled markers to denote bad phase region
        ax.errorbar(x_data_bad_phase,
                    y_data_bad_phase,
                    linestyle='',
                    fmt=markers[y],
                    markerfacecolor='white',
                    color=colors[y])

        # add star nam
        ax.annotate(unique_star_names[y],
                    xy=(np.array(x_data.dropna())[0],
                        np.array(y_data.dropna())[0]),
                    xytext=(np.array(x_data.dropna())[0],
                            np.array(y_data.dropna())[0]))

        # overplot the name of the empirical spectrum at each data point
        empirical_spectra_names_this_star = np.array(empirical_spectrum_names.dropna())
        for spec_annotate_num in range(0,len(empirical_spectra_names_this_star)):
            ax.annotate(empirical_spectra_names_this_star[spec_annotate_num],
                    xy=(np.array(x_data.dropna())[spec_annotate_num],
                        np.array(y_data.dropna())[spec_annotate_num]),
                    xytext=(np.array(x_data.dropna())[spec_annotate_num],
                            np.array(y_data.dropna())[spec_annotate_num]),
                    fontsize=6)
    '''
    # connect lines between each 'star'; that is, with the same gravity and metallicity
    df_20m10 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m10')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20m15 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m15')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20m20 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m20')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20m25 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m25')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20m30 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m30')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20p02 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20p02')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m05 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m05')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m10 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m10')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m15 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m15')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m20 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m20')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m25 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m25')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25m30 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25m30')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m05 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m05')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m10 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m10')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m15 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m15')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m20 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m20')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m25 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m25')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30m30 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30m30')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30p00 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30p00')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25p00 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25p00')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_30p02 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('30p02')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_25p02 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('25p02')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20m05 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20m05')].sort_values(by=["original_spec_file_name"]).reset_index()
    df_20p00 = data_to_plot[data_to_plot['original_spec_file_name'].str.contains('20p00')].sort_values(by=["original_spec_file_name"]).reset_index()

    # establish color map
    n = 16
    colors = pl.cm.jet(np.linspace(0,1,n))
    # definition for making the annotation a bit simpler
    def annotate_fcn(ax_pass, stuff_2_plot):
        for spec_annotate_num in range(0,len(stuff_2_plot)):
            ax_pass.annotate(stuff_2_plot["original_spec_file_name"][spec_annotate_num],
                    xy=(stuff_2_plot["balmer"][spec_annotate_num],stuff_2_plot["K"][spec_annotate_num]),fontsize=6)
    # definition for making the dashed-line plots a bit simpler
    def dashed_line_plot(ax_pass,df_pass):
        ax_pass.errorbar(df_pass["balmer"], df_pass["K"], yerr=df_pass["err_K"], xerr=df_pass["err_balmer"],
                    fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5, linestyle = "--", alpha = 0.2)

    dashed_line_plot(ax,df_20m05)
    annotate_fcn(ax,df_20m05)

    dashed_line_plot(ax,df_20p00)
    annotate_fcn(ax,df_20p00)

    dashed_line_plot(ax,df_20m10)
    annotate_fcn(ax,df_20m10)

    dashed_line_plot(ax,df_20m15)
    annotate_fcn(ax,df_20m15)

    dashed_line_plot(ax,df_20m20)
    annotate_fcn(ax,df_20m20)

    dashed_line_plot(ax,df_20m25)
    annotate_fcn(ax,df_20m25)

    dashed_line_plot(ax,df_20m30)
    annotate_fcn(ax,df_20m30)

    dashed_line_plot(ax,df_20p02)
    annotate_fcn(ax,df_20p02)

    dashed_line_plot(ax,df_25m30)
    annotate_fcn(ax,df_25m30)

    dashed_line_plot(ax,df_25m25)
    annotate_fcn(ax,df_25m25)

    dashed_line_plot(ax,df_25m20)
    annotate_fcn(ax,df_25m20)

    dashed_line_plot(ax,df_25m15)
    annotate_fcn(ax,df_25m15)

    dashed_line_plot(ax,df_25m10)
    annotate_fcn(ax,df_25m10)

    dashed_line_plot(ax,df_25m05)
    annotate_fcn(ax,df_25m05)

    dashed_line_plot(ax,df_25p00)
    annotate_fcn(ax,df_25p00)

    dashed_line_plot(ax,df_25p02)
    annotate_fcn(ax,df_25p02)

    dashed_line_plot(ax,df_30m30)
    annotate_fcn(ax,df_30m30)

    dashed_line_plot(ax,df_30m25)
    annotate_fcn(ax,df_30m25)

    dashed_line_plot(ax,df_30m20)
    annotate_fcn(ax,df_30m20)

    dashed_line_plot(ax,df_30m15)
    annotate_fcn(ax,df_30m15)

    dashed_line_plot(ax,df_30m10)
    annotate_fcn(ax,df_30m10)

    dashed_line_plot(ax,df_30m05)
    annotate_fcn(ax,df_30m05)

    dashed_line_plot(ax,df_30p00)
    annotate_fcn(ax,df_30p00)

    dashed_line_plot(ax,df_30p02)
    annotate_fcn(ax,df_30p02)

    # now remove data for Teff<6000K and Teff>7500K
    df_25m30 = df_25m30.where(np.logical_and(df_25m30["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m30["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25m25 = df_25m25.where(np.logical_and(df_25m25["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m25["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25m20 = df_25m20.where(np.logical_and(df_25m20["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m20["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25m15 = df_25m15.where(np.logical_and(df_25m15["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m15["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25m10 = df_25m10.where(np.logical_and(df_25m10["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m10["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25m05 = df_25m05.where(np.logical_and(df_25m05["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25m05["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25p00 = df_25p00.where(np.logical_and(df_25p00["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25p00["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_25p02 = df_25p02.where(np.logical_and(df_25p02["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_25p02["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m30 = df_30m30.where(np.logical_and(df_30m30["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m30["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m25 = df_30m25.where(np.logical_and(df_30m25["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m25["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m20 = df_30m20.where(np.logical_and(df_30m20["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m20["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m15 = df_30m15.where(np.logical_and(df_30m15["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m15["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m10 = df_30m10.where(np.logical_and(df_30m10["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m10["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30m05 = df_30m05.where(np.logical_and(df_30m05["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30m05["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30p00 = df_30p00.where(np.logical_and(df_30p00["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30p00["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()
    df_30p02 = df_30p02.where(np.logical_and(df_30p02["original_spec_file_name"].str[:4].astype(int) >= 6000,
                                  df_30p02["original_spec_file_name"].str[:4].astype(int) <= 7500)).dropna().reset_index()

    # solid line plots, of data which we want to use for the calibration
    ax.errorbar(df_25m30["balmer"], df_25m30["K"], yerr=df_25m30["err_K"], xerr=df_25m30["err_balmer"], linestyle="-", color=colors[0],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m30)
    ax.errorbar(df_25m25["balmer"], df_25m25["K"], yerr=df_25m25["err_K"], xerr=df_25m25["err_balmer"], linestyle="-", color=colors[1],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m25)
    ax.errorbar(df_25m20["balmer"], df_25m20["K"], yerr=df_25m20["err_K"], xerr=df_25m20["err_balmer"], linestyle="-", color=colors[2],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m20)
    ax.errorbar(df_25m15["balmer"], df_25m15["K"], yerr=df_25m15["err_K"], xerr=df_25m15["err_balmer"], linestyle="-", color=colors[3],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m15)
    ax.errorbar(df_25m10["balmer"], df_25m10["K"], yerr=df_25m10["err_K"], xerr=df_25m10["err_balmer"], linestyle="-", color=colors[4],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m10)
    ax.errorbar(df_25m05["balmer"], df_25m05["K"], yerr=df_25m05["err_K"], xerr=df_25m05["err_balmer"], linestyle="-", color=colors[5],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25m05)
    ax.errorbar(df_25p00["balmer"], df_25p00["K"], yerr=df_25p00["err_K"], xerr=df_25p00["err_balmer"], linestyle="-", color=colors[6],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25p00)
    ax.errorbar(df_25p02["balmer"], df_25p02["K"], yerr=df_25p02["err_K"], xerr=df_25p02["err_balmer"], linestyle="-", color=colors[7],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_25p02)
    ax.errorbar(df_30m30["balmer"], df_30m30["K"], yerr=df_30m30["err_K"], xerr=df_30m30["err_balmer"], linestyle="-", color=colors[8],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m30)
    ax.errorbar(df_30m25["balmer"], df_30m25["K"], yerr=df_30m25["err_K"], xerr=df_30m25["err_balmer"], linestyle="-", color=colors[9],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m25)
    ax.errorbar(df_30m20["balmer"], df_30m20["K"], yerr=df_30m20["err_K"], xerr=df_30m20["err_balmer"], linestyle="-", color=colors[10],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m20)
    ax.errorbar(df_30m15["balmer"], df_30m15["K"], yerr=df_30m15["err_K"], xerr=df_30m15["err_balmer"], linestyle="-", color=colors[11],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m15)
    ax.errorbar(df_30m10["balmer"], df_30m10["K"], yerr=df_30m10["err_K"], xerr=df_30m10["err_balmer"], linestyle="-", color=colors[12],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m10)
    ax.errorbar(df_30m05["balmer"], df_30m05["K"], yerr=df_30m05["err_K"], xerr=df_30m05["err_balmer"], linestyle="-", color=colors[13],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30m05)
    ax.errorbar(df_30p00["balmer"], df_30p00["K"], yerr=df_30p00["err_K"], xerr=df_30p00["err_balmer"], linestyle="-", color=colors[14],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30p00)
    ax.errorbar(df_30p02["balmer"], df_30p02["K"], yerr=df_30p02["err_K"], xerr=df_30p02["err_balmer"], linestyle="-", color=colors[15],
                 fmt='o', elinewidth=0.5, ecolor='k', capsize=5, capthick=0.5)
    annotate_fcn(ax,df_30p02)

    plt.title('KH plot\n(unfilled markers = bad phase region)')
    plt.ylabel('CaIIK EW ($m\AA$?)')
    plt.xlabel('Balmer EW ($m\AA$?)')
    plt.tight_layout()
    plt.savefig(self.plot_write_subdir + config["file_names"]["KH_PLOT_NAME"])

    plt.ylim([0,20])
    plt.savefig(self.plot_write_subdir + "stretched_" + config["file_names"]["KH_PLOT_NAME"])

    plt.close()

    logging.info("HK plots saved as ")
    logging.info(self.plot_write_subdir + config["file_names"]["KH_PLOT_NAME"])
    logging.info(self.plot_write_subdir + "stretched_" + config["file_names"]["KH_PLOT_NAME"])

    # return stuff to enable testing
    return unique_star_names, data_to_plot
