import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.append("../ETL")
from .EtlBase import (
    DataFolder,
    TO_REPUBLICAN,
    TO_DEMOCRAT,
    STAYED_DEMOCRAT,
    STAYED_REPUBLICAN,
)
from .EtlElection import *
from .EtlCovid import *


def getCountyPopulationMask():
    # Read the persidential election CSV from local disk
    population_df = pd.read_csv(
        DataFolder / r"County Data Till 2020 co-est2020-alldata.csv",
        encoding="latin-1",
    )

    county_pop_df = population_df[population_df["SUMLEV"] == 50].copy()
    county_pop_df["COUNTYFP"] = county_pop_df["STATE"].astype("str").str.pad(
        2, "left", "0"
    ) + county_pop_df["COUNTY"].astype("str").str.pad(3, "left", "0")
    county_pop_df["COUNTYFP"] = county_pop_df["COUNTYFP"].astype("int")
    county_pop_df = county_pop_df[
        [
            "STATE",
            "COUNTYFP",
            "CTYNAME",
            "POPESTIMATE2016",
            "POPESTIMATE2020",
            "RNETMIG2020",
        ]
    ]

    # Since county FIPS 2261 (Valdez–Cordova Census Area, Alaska)
    # split into 2063 (Chugach Census Area) and 2066 (Copper River Census Area) in 2020,
    # combine the population data into the older FIP so that we get mask data for it

    county_pop_df.loc[
        county_pop_df[
            (county_pop_df["STATE"] == 2) & (county_pop_df["COUNTYFP"] == 2063)
            | (county_pop_df["COUNTYFP"] == 2066)
        ].index,
        "COUNTYFP",
    ] = 2261

    county_pop_df.loc[
        county_pop_df[
            (county_pop_df["STATE"] == 2) & (county_pop_df["COUNTYFP"] == 2261)
        ].index,
        "CTYNAME",
    ] = "(Valdez–Cordova Census Area, Alaska)"

    county_pop_df = (
        county_pop_df.groupby(["STATE", "COUNTYFP", "CTYNAME"]).agg("sum").reset_index()
    )

    county_mask_df = pd.read_csv(
        r"https://raw.githubusercontent.com/nytimes/covid-19-data/master/mask-use/mask-use-by-county.csv"
    )
    # county_mask_df.to_csv( r"../DataForPresidentialElectionsAndCovid/Dataset 7 Covid/mask-use-by-county.csv")
    county_pop_mask_df = pd.merge(
        county_pop_df, county_mask_df, how="right", on=["COUNTYFP"], indicator=True
    )
    return county_pop_mask_df


##########################################################################################
def createFrequentAndInfrequentMaskUsers():
    # Add up groupings of frequent and non frequent
    county_pop_mask_df = getCountyPopulationMask()
    election_winners_df = getElectionSegmentsData()
    county_pop_mask_melt_df = county_pop_mask_df.melt(
        id_vars=[
            "STATE",
            "COUNTYFP",
            "CTYNAME",
            "POPESTIMATE2016",
            "POPESTIMATE2020",
            "RNETMIG2020",
        ],
        value_vars=["NEVER", "RARELY", "SOMETIMES", "FREQUENTLY", "ALWAYS"],
        var_name="mask_usage_type",
        value_name="mask_usage",
        col_level=None,
        ignore_index=True,
    )

    # Create two groups
    county_pop_mask_melt_df["mask_usage_type"] = pd.Series(
        np.where(
            county_pop_mask_melt_df["mask_usage_type"].isin(["ALWAYS", "FREQUENTLY"]),
            "FREQUENT",
            "NOT FREQUENT",
        )
    )

    # Add up the new groupings of FREQUENT AND NON FREQUENT
    county_pop_mask_melt_df = (
        county_pop_mask_melt_df.groupby(
            [
                "STATE",
                "COUNTYFP",
                "CTYNAME",
                "POPESTIMATE2016",
                "POPESTIMATE2020",
                "RNETMIG2020",
                "mask_usage_type",
            ]
        )["mask_usage"]
        .sum()
        .reset_index()
    )

    changes_df = election_winners_df[
        election_winners_df.changecolor.isin(
            [TO_DEMOCRAT, TO_REPUBLICAN, STAYED_DEMOCRAT, STAYED_REPUBLICAN]
        )
    ][["COUNTYFP", "changecolor"]]
    county_pop_mask_melt_df = county_pop_mask_melt_df.merge(
        changes_df, how="inner", on="COUNTYFP"
    )
    return county_pop_mask_melt_df


##########################################################################################
def getMaskUsageRange(mask_usage):
    """This function creates ranges for percentage mask usage
       The three ranges created are "Low (<=50%)", "Moderate (50%-80%)" and "High (>80%)"

    Args:
        mask_usage ([float]): [Estimated mask usage value]

    Returns:
        [string]: [Range of usage]
    """
    if mask_usage <= 0.5:
        return "Low (<=50%)"
    elif mask_usage > 0.5 and mask_usage <= 0.8:
        return "Moderate (50%-80%)"
    else:
        return "High (>80%)"


def getColorRangeMaskUsage(segmentname, mask_usage_range):
    """[This function comverts a combination of political affiliation and mask usage range into a color]

    Args:
        segmentname ([String]): [Democrat/Republican]
        mask_usage_range ([type]): [Ranges of mask uasge percentage]

    Returns:
        [string]: [Hex Code of color]
    """
    legend_dict = {
        ("Democrat", "Low (<=50%)"): "#C5DDF9",
        ("Democrat", "Moderate (50%-80%)"): "#3CA0EE",
        ("Democrat", "High (>80%)"): "#0015BC",
        ("Republican", "Low (<=50%)"): "#F2A595",
        ("Republican", "Moderate (50%-80%)"): "#EE8778",
        ("Republican", "High (>80%)"): "#970D03",
    }
    return legend_dict[(segmentname, mask_usage_range)]


def createDataForFreqAndInFreqMaskUse():
    """[This function creates three dataframes]

    Returns:
        [Pandas dataframes]: [A consolidated dataframe, frequent mask usage dataframe and infrequent mask usage dataframe]
    """
    county_pop_mask_df = createFrequentAndInfrequentMaskUsers()
    county_pop_mask_df["segmentname"] = county_pop_mask_df["changecolor"].map(
        color_segment_dict
    )
    county_pop_mask_df.segmentname = county_pop_mask_df.segmentname.str.replace(
        "Stayed ", ""
    )
    county_pop_mask_df.segmentname = county_pop_mask_df.segmentname.str.replace(
        "To ", ""
    )

    county_pop_mask_df = county_pop_mask_df[
        ["STATE", "COUNTYFP", "CTYNAME", "mask_usage_type", "mask_usage", "segmentname"]
    ].copy()
    county_pop_mask_df["mask_usage_range"] = county_pop_mask_df["mask_usage"].apply(
        lambda x: getMaskUsageRange(x)
    )

    county_pop_mask_df["range_color"] = county_pop_mask_df[
        ["segmentname", "mask_usage_range"]
    ].apply(
        lambda x: getColorRangeMaskUsage(x["segmentname"], x["mask_usage_range"]),
        axis=1,
    )

    county_pop_mask_freq_df = county_pop_mask_df[
        county_pop_mask_df["mask_usage_type"] == "FREQUENT"
    ].copy()
    county_pop_mask_infreq_df = county_pop_mask_df[
        county_pop_mask_df["mask_usage_type"] == "NOT FREQUENT"
    ].copy()
    return county_pop_mask_df, county_pop_mask_freq_df, county_pop_mask_infreq_df


##########################################################################################
def createDataForMaskUsageDistribution():
    """This function creates a copy of the dataframe sent in containing column changecolor
        It replaces the changed affilition color to loyalty color.

    """

    df = createFrequentAndInfrequentMaskUsers()
    df["changecolor"] = df["changecolor"].str.replace(TO_DEMOCRAT, STAYED_DEMOCRAT)
    df["changecolor"] = df["changecolor"].str.replace(TO_REPUBLICAN, STAYED_REPUBLICAN)
    df["party"] = np.where(
        df["changecolor"] == STAYED_REPUBLICAN, "Republican", "Democrat"
    )

    return df
