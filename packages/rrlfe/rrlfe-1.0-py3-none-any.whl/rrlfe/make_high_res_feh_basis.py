'''
Reads in literature metallicities and makes new Fe/H basis
'''

import pickle
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from astroquery.simbad import Simbad
from . import *

class LitFehRaw():
    """
    Read in Fe/H values from the literature, before making any transformations
    """

    def __init__(self):
        # map the raw data to object

        # source_dir=config_red["data_dirs"]["DIR_LIT_HIGH_RES_FEH"]):
        source_dir = "/Users/bandari/Documents/git.repos/rrlfe/src/high_res_feh/"

        # stand-in that consists of our program star names
        self.df_our_program_stars = pd.read_csv(source_dir + "our_program_stars_names_only.csv")

        # Fe/H from Layden+ 1994; this may serve as the common basis for RRabs
        self.df_layden_feh = pd.read_csv(source_dir + "layden_1994_abundances.dat")
        # RES: "rather low"

        # Fe/H Clementini+ 1995
        self.df_clementini_feh = pd.read_csv(source_dir + "clementini_1995_abundances.dat")

        # Fe/H Fernley+ 1996
        self.df_fernley96_feh = pd.read_csv(source_dir + "fernley_1996_abundances.dat")
        # RES: 60,000, FeI & FeII, 5900-8100 A

        # Fe/H from Fernley+ 1997
        self.df_fernley97_feh = pd.read_csv(source_dir + "fernley_1997_abundances.dat")
        # RES: 60,000, two FeII lines, 5900-8100 A

        # log(eps) from Lambert+ 1996
        self.df_lambert_logeps = pd.read_csv(source_dir + "lambert_1996_abundances.dat")
        # RES: ~23,000, FeII + photometric models, 3600-9000 A

        # Fe/H from Wallerstein and Huang 2010, arXiv 1004.2017
        self.df_wallerstein_feh = pd.read_csv(source_dir + "wallerstein_huang_2010_abundances.dat")
        # RES: ~30,000, FeII

        # Fe/H from Chadid+ 2017 ApJ 835.2:187 (FeI and II lines)
        self.df_chadid_feh = pd.read_csv(source_dir + "chadid_2017_abundances.dat")
        # RES: 38000, FeI & FeII, 3400-9900 A

        # Fe/H from Liu+ 2013 Res Ast Astroph 13:1307
        self.df_liu_feh = pd.read_csv(source_dir + "liu_2013_abundances.dat")
        # RES: ~60,000, FeI (& FeII?), 5100-6400 A

        # Fe/H from Nemec+ 2013
        self.df_nemec_feh = pd.read_csv(source_dir + "nemec_2013_abundances.dat")
        # RES: ~65,000 or 36,000, FeI & FeII, 5150-5200 A

        # Fe/H from Solano+ 1997
        self.df_solano_feh = pd.read_csv(source_dir + "solano_1997_abundances.dat")
        # RES: 22,000 & 19,000, strong FeI lines, 4160-4390 & 4070-4490 A

        # Fe/H from Pancino+ 2015 MNRAS 447:2404
        self.df_pancino_feh = pd.read_csv(source_dir + "pancino_2015_abundances.dat")
        # RES: >30,000, FeI (weighted average), 4000-8500 A

        # Fe/H from Sneden+ 2017
        self.df_sneden_feh = pd.read_csv(source_dir + "sneden_2017_abundances.dat", delimiter="|")
        # RES: ~27,000 (at 5000 A), FeI & FeII, 3400-9000 A

        # Fe/H from Crestani+ 2021
        self.df_crestani_feh = pd.read_csv(source_dir + "crestani_2021_abundances.dat",
                                            delimiter=",")

        # Fe/H from Kemper+ 1982; this might serve as the common basis for RRcs
        self.df_kemper_feh = pd.read_csv(source_dir + "kemper_1982_abundances.dat")

        # Fe/H from Govea+ 2014
        # note: Govea+ has abundances for each phase value, and this includes NLTE phases
        self.df_govea_feh = pd.read_csv(source_dir + "govea_2014_abundances.dat")


def matchmaker(basis_table_pass, input_table_pass):
    """
    Find what stars are common to two input tables, return arrays of FeHs, fit best-fit line

    Parameters:
        input_table (pandas DataFrame): table I'm interested in checking for overlapping stars; cols \n
            "name_match": star name \n
            "feh_single": Fe/H
        basis_table (pandas DataFrame): table with the names for which I am looking for repeats in the other table \n
            "name_match": star name \n
            "feh_single": Fe/H

    Returns:
        pandas dataframe with \n
        1. overlapping star names \n
        2. FeHs from the input_table \n
        3. FeHs from the basis_table \n
        4. residuals in FeH: FeH_input - FeH_basis \n
        5. string indicating the high-res dataset being matched
    """

    basis_table = basis_table_pass.copy(deep=True)
    input_table = input_table_pass.copy(deep=True)

    # make all strings lowercase, to make case insensitive match
    basis_table['name_match'] = basis_table['name_match'].str.lower()
    input_table['name_match'] = input_table['name_match'].str.lower()

    merged_table = basis_table.merge(input_table, how="inner", on="name_match", suffixes=("_basis", "_lit"))

    return merged_table


def find_offsets(match_pass):
    """
    Finds the offsets that need to be added in to overlap datasets as per Crestani+ 2017 Fig. 6

    Parameters:
        match_pass (pandas DataFrame): dataframe containing matched Fe/Hs

    Returns:
        the constant offset that needs to be added back in
    """

    # find offset between (lit vs. Layden) residuals and Chadid+ 2017 at Fe/H=-1.25 (see their Fig. 6)
    chadid_y_125 = -0.10583621694962 # from Chadid line at Fe/H=-1.25
    feh_basis_loc = -1.25 # corresponding x- value (Fe/H in the basis dataset)

    m_lit, b_lit = np.polyfit(match_pass["feh_single_basis"],np.subtract(match_pass["feh_single_lit"],match_pass["feh_single_basis"]),1)
    # find offset between residuals and zero
    y_offset_lit = m_lit*feh_basis_loc + b_lit
    # offset between the offsets ("offset_2"); this is what needs to be added in
    # to bring it in line with lit
    y_offset_2_lit = chadid_y_125 - y_offset_lit

    return y_offset_2_lit


def main():

    # read in raw
    raws = LitFehRaw()

    # make transformations to get single Fe/H value

    # convert outputs in astropy.Table format to DataFrames
    df_our_stars = pd.DataFrame(raws.df_our_program_stars)
    df_govea = pd.DataFrame(raws.df_govea_feh) #avg
    df_layden = pd.DataFrame(raws.df_layden_feh) # simple
    df_clementini = pd.DataFrame(raws.df_clementini_feh) # logeps, then avg
    df_fernley96 = pd.DataFrame(raws.df_fernley96_feh) # simple, add error
    df_fernley97 = pd.DataFrame(raws.df_fernley97_feh) # simple
    df_lambert = pd.DataFrame(raws.df_lambert_logeps) # logeps, then avg
    df_wallerstein = pd.DataFrame(raws.df_wallerstein_feh) # simple, add error
    df_chadid = pd.DataFrame(raws.df_chadid_feh) # avg
    df_liu = pd.DataFrame(raws.df_liu_feh)  # simple, add error (at different phases)
    df_nemec = pd.DataFrame(raws.df_nemec_feh) # simple
    df_solano = pd.DataFrame(raws.df_solano_feh) # simple, add error
    df_pancino = pd.DataFrame(raws.df_pancino_feh) # simple
    df_sneden = pd.DataFrame(raws.df_sneden_feh) # avg (diff phases); note sigma is one of last rows
    df_crestani = pd.DataFrame(raws.df_crestani_feh) # avg
    df_kemper = pd.DataFrame(raws.df_kemper_feh) # simple, add error


    # find net Fe/H values and errors in each DataFrame

    # Govea+ 2014
    cols_govea = ["feIh","feIIh"]
    df_govea["feh_single"] = df_govea[cols_govea].mean(axis=1)
    df_govea["err_feh_single"] = 0.5*np.sqrt(np.add(np.power(df_govea["err_feIh"],2.),np.power(df_govea["err_feIIh"],2.)))

    # Layden 1994
    df_layden["feh_single"] = df_layden["feh"]
    df_layden["err_feh_single"] = df_layden["err_feh"]

    # Clementini+ 1995
    idx_sol = df_clementini["name_match"] == "sol" # row corresponding to solar values
    logepssol = np.mean([df_clementini.loc[idx_sol]["log_eps_feI"][0],df_clementini.loc[idx_sol]["log_eps_feII"][0]]) # net solar logeps
    # estimate errors in solar logeps values (which Clementini does not give), by using averages of the others
    df_clementini.at[idx_sol,"err_log_eps_feI"] = np.mean(df_clementini.loc[~idx_sol]["err_log_eps_feI"])
    df_clementini.at[idx_sol,"err_log_eps_feII"] = np.mean(df_clementini.loc[~idx_sol]["err_log_eps_feII"])
    cols_clementini = ["log_eps_feI", "log_eps_feII"]
    df_clementini["logeps_single"] = df_clementini[cols_clementini].mean(axis=1)
    # avoid rounding error, which is present in authors "feh" column
    df_clementini["err_logeps_single"] = 0.5*np.sqrt(np.add(np.power(df_clementini["err_log_eps_feI"],2.),np.power(df_clementini["err_log_eps_feII"],2.)))
    df_clementini["feh_single"] = np.subtract(df_clementini["logeps_single"],logepssol)
    df_clementini["err_feh_single"] = np.sqrt(np.add(np.power(df_clementini["err_logeps_single"],2.),np.power(df_clementini.loc[idx_sol]["err_logeps_single"][0],2.)))
    #[df_clementini["log_eps_feI"],df_clementini.loc["log_eps_feII"]].mean() # avg logeps values

    # Fernley+ 1996
    df_fernley96["feh_single"] = df_fernley96["feh"]
    df_fernley96["err_feh_single"] = 0.15 # estimate

    # Fernley+ 1997
    df_fernley97["feh_single"] = df_fernley97["feh"]
    df_fernley97["err_feh_single"] = df_fernley97["err_feh"]

    # Lambert+ 1996
    # convert Lambert's log(eps) to Fe/H
    # FeH = log(epsFe) - log(epsFe,sol)
    #     = log(epsFe) - log(NFe,sol/NH,sol)
    #     = log(epsFe) - 7.51 # value of 7.51 from Anstee+ 1997, MNRAS
    df_lambert["feh_single"] = np.subtract(df_lambert["log_eps_fe_spec"],7.51)
    df_lambert["err_feh_single"] = 0.15 # estimate

    # Wallerstein and Huang 2010
    df_wallerstein["feh_single"] = df_wallerstein["feh"]
    df_wallerstein["err_feh_single"] = 0.15 # estimate

    # Chadid+ 2017
    cols_chadid = ["fehI","fehII"]
    df_chadid["feh_single"] = df_chadid[cols_chadid].mean(axis=1)
    df_chadid["err_feh_single"] = 0.5*np.sqrt(np.add(np.power(df_chadid["err_fehI"],2.),np.power(df_chadid["err_fehII"],2.)))

    # Liu+ 2013
    # group multiple Fe/H values from different phase values by star name
    df_liu = df_liu.groupby(["name_match"],axis=0,as_index=False).mean()
    df_liu["feh_single"] = df_liu["feh"]
    df_liu["err_feh_single"] = 0.15 # estimate

    # Nemec+ 2013
    df_nemec["feh_single"] = df_nemec["feh"]
    df_nemec["err_feh_single"] = df_nemec["err_feh"]

    # Solano+ 1997
    df_solano["feh_single"] = df_solano["feh"]
    df_solano["err_feh_single"] = 0.15

    # Pancino+ 2015
    df_pancino["feh_single"] = df_pancino["feh"]
    df_pancino["err_feh_single"] = df_pancino["err_feh"]

    # Sneden+ 2017
    cols_sneden = ["fehI","fehII"]
    df_sneden["feh_single"] = df_sneden[cols_sneden].mean(axis=1)
    df_sneden["err_feh_single"] = 0.5*np.sqrt(np.add(np.power(df_sneden["err_fehI"],2.),np.power(df_sneden["err_fehII"],2.)))
    df_sneden["name_match"] = df_sneden["name"].astype(str) # to avoid col disappearing when grouping
    df_sneden = df_sneden.groupby(["name_match"],axis=0,as_index=False).mean()

    # Crestani+ 2021
    cols_crestani = ["fehI","fehII"]
    df_crestani["feh_single"] = df_crestani[cols_crestani].mean(axis=1)
    df_crestani["err_feh_single"] = 0.5*np.sqrt(np.add(np.power(df_crestani["err_fehI"],2.),np.power(df_crestani["err_fehII"],2.)))

    # Kemper+ 1982
    df_kemper["feh_single"] = df_kemper["feh"]
    df_kemper["err_feh_single"] = 0.15 # estimate

    # match and find offsets: Govea+ 2014 [NO MATCHES!]
    # match and find offsets: Clementini+ 1995
    match_clementini = matchmaker(basis_table_pass=df_layden, input_table_pass=df_clementini)
    offset_clementini = find_offsets(match_clementini)
    # match and find offsets: Fernley+ 1996
    match_fernley96 = matchmaker(basis_table_pass=df_layden, input_table_pass=df_fernley96)
    offset_fernley96 = find_offsets(match_fernley96)
    # match and find offsets: Fernley+ 1997
    match_fernley97 = matchmaker(basis_table_pass=df_layden, input_table_pass=df_fernley97)
    offset_fernley97 = find_offsets(match_fernley97)
    # match and find offsets: Lambert+ 1996
    match_lambert = matchmaker(basis_table_pass=df_layden, input_table_pass=df_lambert)
    offset_lambert = find_offsets(match_lambert)
    # match and find offsets: Wallerstein and Huang 2010
    match_wallerstein = matchmaker(basis_table_pass=df_layden, input_table_pass=df_wallerstein)
    offset_wallerstein = find_offsets(match_wallerstein)
    # match and find offsets: Chadid+ 2017
    match_chadid = matchmaker(basis_table_pass=df_layden, input_table_pass=df_chadid)
    offset_chadid = find_offsets(match_chadid)
    # match and find offsets: Liu+ 2013
    match_liu = matchmaker(basis_table_pass=df_layden, input_table_pass=df_liu)
    offset_liu = find_offsets(match_liu)
    # match and find offsets: Nemec+ 2013
    match_nemec = matchmaker(basis_table_pass=df_layden, input_table_pass=df_nemec)
    offset_nemec = find_offsets(match_nemec)
    # match and find offsets: Solano+ 1997
    match_solano = matchmaker(basis_table_pass=df_layden, input_table_pass=df_solano)
    offset_solano = find_offsets(match_solano)
    # match and find offsets: Pancino+ 2015
    match_pancino = matchmaker(basis_table_pass=df_layden, input_table_pass=df_pancino)
    offset_pancino = find_offsets(match_pancino)
    # match and find offsets: Sneden+ 2017 [NO MATCHES!]
    # match and find offsets: Crestani+ 2021
    match_crestani = matchmaker(basis_table_pass=df_layden, input_table_pass=df_crestani)
    offset_crestani = find_offsets(match_crestani)
    # match and find offsets: Kemper+ 1982 [NO MATCHES!]

    # apply the offsets
    match_clementini["feh_single_lit_synced"] = np.add(offset_clementini,match_clementini["feh_single_lit"])
    match_fernley96["feh_single_lit_synced"] = np.add(offset_fernley96,match_fernley96["feh_single_lit"])
    match_fernley97["feh_single_lit_synced"] = np.add(offset_fernley97,match_fernley97["feh_single_lit"])
    match_lambert["feh_single_lit_synced"] = np.add(offset_lambert,match_lambert["feh_single_lit"])
    match_wallerstein["feh_single_lit_synced"] = np.add(offset_wallerstein,match_wallerstein["feh_single_lit"])
    match_chadid["feh_single_lit_synced"] = np.add(offset_chadid,match_chadid["feh_single_lit"])
    match_liu["feh_single_lit_synced"] = np.add(offset_liu,match_liu["feh_single_lit"])
    match_nemec["feh_single_lit_synced"] = np.add(offset_nemec,match_nemec["feh_single_lit"])
    match_solano["feh_single_lit_synced"] = np.add(offset_solano,match_solano["feh_single_lit"])
    match_pancino["feh_single_lit_synced"] = np.add(offset_pancino,match_pancino["feh_single_lit"])
    match_crestani["feh_single_lit_synced"] = np.add(offset_crestani,match_crestani["feh_single_lit"])

    # merge everything together
    abcissa_feh_high_res_synched = [match_clementini["feh_single_basis"],
                                    match_fernley96["feh_single_basis"],
                                    match_fernley97["feh_single_basis"],
                                    match_lambert["feh_single_basis"],
                                    match_wallerstein["feh_single_basis"],
                                    match_chadid["feh_single_basis"],
                                    match_liu["feh_single_basis"],
                                    match_nemec["feh_single_basis"],
                                    match_solano["feh_single_basis"],
                                    match_pancino["feh_single_basis"],
                                    match_crestani["feh_single_basis"]]

    ordinate_feh_high_res_synched = [match_clementini["feh_single_lit_synced"],
                                    match_fernley96["feh_single_lit_synced"],
                                    match_fernley97["feh_single_lit_synced"],
                                    match_lambert["feh_single_lit_synced"],
                                    match_wallerstein["feh_single_lit_synced"],
                                    match_chadid["feh_single_lit_synced"],
                                    match_liu["feh_single_lit_synced"],
                                    match_nemec["feh_single_lit_synced"],
                                    match_solano["feh_single_lit_synced"],
                                    match_pancino["feh_single_lit_synced"],
                                    match_crestani["feh_single_lit_synced"]]

    df_abcissa_synched = pd.concat(abcissa_feh_high_res_synched)
    df_ordinate_synched = pd.concat(ordinate_feh_high_res_synched)

    # find the final mapping (see Chadid+ 2017 eqn. on p. 8, left-hand column)
    # [Fe/H]_highres = m * [Fe/H]_Lay94 + b
    m_final, b_final = np.polyfit(df_abcissa_synched,df_ordinate_synched,1)
    print("m final: ", m_final)
    print("b final: ", b_final)

    # sanity check
    plt.plot([-2.75,0.05],[-2.75,0.05],linestyle="--",color="gray")
    plt.plot([-2.75,0.05],np.multiply([-2.75,0.05],m_final)+b_final,color="k")
    plt.scatter(df_abcissa_synched,df_ordinate_synched)
    plt.savefig("junk_sanity.pdf")


    plt.clf()
    plt.plot([-2.75,0.05],[-3.,0.25],linestyle="--",color="gray")
    plt.scatter(match_clementini["feh_single_basis"],match_clementini["feh_single_lit"])
    plt.scatter(match_fernley96["feh_single_basis"],match_fernley96["feh_single_lit"])
    plt.scatter(match_fernley97["feh_single_basis"],match_fernley97["feh_single_lit"])
    plt.scatter(match_lambert["feh_single_basis"],match_lambert["feh_single_lit"])
    plt.scatter(match_wallerstein["feh_single_basis"],match_wallerstein["feh_single_lit"])
    plt.scatter(match_chadid["feh_single_basis"],match_chadid["feh_single_lit"])
    plt.scatter(match_liu["feh_single_basis"],match_liu["feh_single_lit"])
    plt.scatter(match_nemec["feh_single_basis"],match_nemec["feh_single_lit"])
    plt.scatter(match_solano["feh_single_basis"],match_solano["feh_single_lit"])
    plt.scatter(match_pancino["feh_single_basis"],match_pancino["feh_single_lit"])
    plt.scatter(match_crestani["feh_single_basis"],match_crestani["feh_single_lit"])
    plt.savefig("test_unsynced.pdf")

    plt.clf()
    plt.plot([-2.75,0.05],[-3.,0.25],linestyle="--",color="gray")
    plt.scatter(match_clementini["feh_single_basis"],match_clementini["feh_single_lit_synced"])
    plt.scatter(match_fernley96["feh_single_basis"],match_fernley96["feh_single_lit_synced"])
    plt.scatter(match_fernley97["feh_single_basis"],match_fernley97["feh_single_lit_synced"])
    plt.scatter(match_lambert["feh_single_basis"],match_lambert["feh_single_lit_synced"])
    plt.scatter(match_wallerstein["feh_single_basis"],match_wallerstein["feh_single_lit_synced"])
    plt.scatter(match_chadid["feh_single_basis"],match_chadid["feh_single_lit_synced"])
    plt.scatter(match_liu["feh_single_basis"],match_liu["feh_single_lit_synced"])
    plt.scatter(match_nemec["feh_single_basis"],match_nemec["feh_single_lit_synced"])
    plt.scatter(match_solano["feh_single_basis"],match_solano["feh_single_lit_synced"])
    plt.scatter(match_pancino["feh_single_basis"],match_pancino["feh_single_lit_synced"])
    plt.scatter(match_crestani["feh_single_basis"],match_crestani["feh_single_lit_synced"])
    plt.savefig("test_synced.pdf")

    # FYI, to see residuals around 1-to-1 line
    plt.clf()
    plt.plot([-1.,1.],[0.,0.],linestyle="--",color="gray")
    plt.scatter(match_clementini["feh_single_basis"],np.subtract(match_clementini["feh_single_lit_synced"],match_clementini["feh_single_basis"]))
    plt.scatter(match_fernley96["feh_single_basis"],np.subtract(match_fernley96["feh_single_lit_synced"],match_fernley96["feh_single_basis"]))
    plt.scatter(match_fernley97["feh_single_basis"],np.subtract(match_fernley97["feh_single_lit_synced"],match_fernley97["feh_single_basis"]))
    plt.scatter(match_lambert["feh_single_basis"],np.subtract(match_lambert["feh_single_lit_synced"],match_lambert["feh_single_basis"]))
    plt.scatter(match_wallerstein["feh_single_basis"],np.subtract(match_wallerstein["feh_single_lit_synced"],match_wallerstein["feh_single_basis"]))
    plt.scatter(match_chadid["feh_single_basis"],np.subtract(match_chadid["feh_single_lit_synced"],match_chadid["feh_single_basis"]))
    plt.scatter(match_liu["feh_single_basis"],np.subtract(match_liu["feh_single_lit_synced"],match_liu["feh_single_basis"]))
    plt.scatter(match_nemec["feh_single_basis"],np.subtract(match_nemec["feh_single_lit_synced"],match_nemec["feh_single_basis"]))
    plt.scatter(match_solano["feh_single_basis"],np.subtract(match_solano["feh_single_lit_synced"],match_solano["feh_single_basis"]))
    plt.scatter(match_pancino["feh_single_basis"],np.subtract(match_pancino["feh_single_lit_synced"],match_pancino["feh_single_basis"]))
    plt.scatter(match_crestani["feh_single_basis"],np.subtract(match_crestani["feh_single_lit_synced"],match_crestani["feh_single_basis"]))
    plt.savefig("test_resids.pdf")

    resids_synched = [np.subtract(match_clementini["feh_single_lit_synced"],match_clementini["feh_single_basis"]),
                        np.subtract(match_fernley96["feh_single_lit_synced"],match_fernley96["feh_single_basis"]),
                        np.subtract(match_fernley97["feh_single_lit_synced"],match_fernley97["feh_single_basis"]),
                        np.subtract(match_lambert["feh_single_lit_synced"],match_lambert["feh_single_basis"]),
                        np.subtract(match_wallerstein["feh_single_lit_synced"],match_wallerstein["feh_single_basis"]),
                        np.subtract(match_chadid["feh_single_lit_synced"],match_chadid["feh_single_basis"]),
                        np.subtract(match_liu["feh_single_lit_synced"],match_liu["feh_single_basis"]),
                        np.subtract(match_nemec["feh_single_lit_synced"],match_nemec["feh_single_basis"]),
                        np.subtract(match_solano["feh_single_lit_synced"],match_solano["feh_single_basis"]),
                        np.subtract(match_pancino["feh_single_lit_synced"],match_pancino["feh_single_basis"]),
                        np.subtract(match_crestani["feh_single_lit_synced"],match_crestani["feh_single_basis"])
                        ]
    df_fyi_resids_synched = pd.concat(resids_synched)

    resids_nonsynched = [np.subtract(match_clementini["feh_single_lit"],match_clementini["feh_single_basis"]),
                        np.subtract(match_fernley96["feh_single_lit"],match_fernley96["feh_single_basis"]),
                        np.subtract(match_fernley97["feh_single_lit"],match_fernley97["feh_single_basis"]),
                        np.subtract(match_lambert["feh_single_lit"],match_lambert["feh_single_basis"]),
                        np.subtract(match_wallerstein["feh_single_lit"],match_wallerstein["feh_single_basis"]),
                        np.subtract(match_chadid["feh_single_lit"],match_chadid["feh_single_basis"]),
                        np.subtract(match_liu["feh_single_lit"],match_liu["feh_single_basis"]),
                        np.subtract(match_nemec["feh_single_lit"],match_nemec["feh_single_basis"]),
                        np.subtract(match_solano["feh_single_lit"],match_solano["feh_single_basis"]),
                        np.subtract(match_pancino["feh_single_lit"],match_pancino["feh_single_basis"]),
                        np.subtract(match_crestani["feh_single_lit"],match_crestani["feh_single_basis"])
                        ]
    df_fyi_resids_nonsynched = pd.concat(resids_nonsynched)


# entry point
if __name__ == '__main__':
    sys.exit(main())
