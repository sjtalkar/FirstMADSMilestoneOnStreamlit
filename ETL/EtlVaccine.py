import os
import pickle
import pandas as pd
import numpy as np

from pathlib import Path
import requests
import sys

sys.path.append("../ETL")
from .EtlBase import DataFolder, US_STATE_ABBRV
from .EtlElection import *


########################################################################################
def createStateVaccinationData():

    """
      THIS FUNCTION obtains vaccination data by state (Questions: by September 4th, 2021), merges into it
      state population data, followed by 2020 presidential election data.
      
      Functions called: getStateLevelElectionData2020()
      Called by: createStateVaccinationChart()

      Input: None
      Returns: Dataframe vaccination_df with the following columns:
      
               STATEFP  ...........................................  (state FIPS)
               STNAME
               People with at least One Dose by State of Residence
               Percent with one dose
               Total population
               state  .............................................  (state name again)
               state_po  ..........................................  (2-letter abbreviation)
               state_fips  ........................................  (state FIPS again)
               candidatevotes
               totalvotes
               party_simplified  ..................................  (DEMOCRAT, REPUBLICAN, LIBERTARIAN or OTHER)
               fractionalvotes
    """
    vaccination_df = pd.read_csv(
        "./data/covid19_vaccinations_in_the_united_states.csv", skiprows=2,
    )

    # Select columns containing at least one dose per 100K since taking that one dose shows openness
    # to taking the vaccine
    vaccination_df = vaccination_df[
        [
            "State/Territory/Federal Entity",
            "People with at least One Dose by State of Residence",
            "Percent of Total Pop with at least One Dose by State of Residence",
        ]
    ].copy()

    # Calculate Total population assumed by data as per percent and numbers
    vaccination_df["Total population"] = (
        (vaccination_df["People with at least One Dose by State of Residence"] * 100)
        / vaccination_df[
            "Percent of Total Pop with at least One Dose by State of Residence"
        ]
    )

    # Read the county population CSV from local file
    population_df = pd.read_csv(
        "./data/County Data Till 2020 co-est2020-alldata.csv", encoding="latin-1",
    )
    state_pop_df = population_df[population_df["SUMLEV"] != 50].copy()
    state_pop_df = state_pop_df[["STATE", "STNAME", "POPESTIMATE2020"]]

    # Merge vaccination and population data on state name
    vaccination_df = vaccination_df.merge(
        state_pop_df,
        how="inner",
        left_on="State/Territory/Federal Entity",
        right_on="STNAME",
    )
    vaccination_df = vaccination_df[
        [
            "STATE",
            "STNAME",
            "People with at least One Dose by State of Residence",
            "Percent of Total Pop with at least One Dose by State of Residence",
            "Total population",
        ]
    ].copy()
    vaccination_df = vaccination_df.rename(
        columns={
            "STATE": "STATEFP",
            "Percent of Total Pop with at least One Dose by State of Residence": "Percent with one dose",
        }
    )

    # Get the presidential election winning party data
    state_election_df = getStateLevelElectionData2020()

    # Merge with vaccinatino and population data
    vaccination_df = vaccination_df.merge(
        state_election_df, how="inner", left_on="STATEFP", right_on="state_fips"
    )

    # for charting purposes
    vaccination_df["Percent with one dose"] = (
        vaccination_df["Percent with one dose"] / 100
    )

    return vaccination_df


########################################################################################
def getDailyVaccinationPercentData():
    """
        This function retrieves the daily percentage of vaccinated people in each state
        The day_num column is the count of days from the date of first vaccination administered in any state,
        which will be used in the slider providing interactivity. 
        
        Input: None
        Output: 'Date', 
                'Location'
                'Percent with one dose'
                 'state'
                 'state_po',
                 'state_fips'
                 'STATEFP'
                 'STNAME'
                 'Total population'
                 'candidatevotes'
                 'totalvotes'
                 'party_simplified'
                 'fractionalvotes'
                 'day_num'
      
    """
    vaccination_df = pd.read_csv(
        "./data/COVID-19_Vaccinations_in_the_United_States_Jurisdiction.csv"
    )
    ## Percent of population with at lease one dose based on the jurisdiction where recipient lives
    vaccination_df = vaccination_df[
        ["Date", "Location", "Administered_Dose1_Recip_18PlusPop_Pct"]
    ].copy()
    vaccination_df["Date"] = pd.to_datetime(vaccination_df["Date"])

    state_election_df = getStateLevelElectionData2020()
    vaccination_df = vaccination_df.merge(
        state_election_df, how="inner", left_on="Location", right_on="state_po"
    )
    vaccination_df.drop(
        columns=["candidatevotes", "totalvotes", "party_simplified", "fractionalvotes"],
        inplace=True,
    )

    # Read the persidential election CSV from local disk
    population_df = pd.read_csv(
        "./data/County Data Till 2020 co-est2020-alldata.csv", encoding="latin-1",
    )
    state_pop_df = population_df[population_df["SUMLEV"] != 50].copy()
    state_pop_df = state_pop_df[["STATE", "STNAME", "POPESTIMATE2020"]]

    vaccination_df = vaccination_df.merge(
        state_pop_df, how="inner", left_on="state_fips", right_on="STATE"
    )
    vaccination_df = vaccination_df.rename(
        columns={
            "STATE": "STATEFP",
            "Administered_Dose1_Recip_18PlusPop_Pct": "Percent with one dose",
            "POPESTIMATE2020": "Total population",
        }
    )

    state_election_df = getStateLevelElectionData2020()
    vaccination_df = vaccination_df.merge(
        state_election_df,
        how="inner",
        left_on=["STATEFP", "state_po", "state", "state_fips"],
        right_on=["state_fips", "state_po", "state", "state_fips"],
    )

    # for charting purposes
    vaccination_df["Percent with one dose"] = (
        vaccination_df["Percent with one dose"] / 100
    )

    # vaccination_df[vaccination_df['Date'].dt.year == 2020]['Percent with one dose'].unique()

    min_date = vaccination_df[vaccination_df["Percent with one dose"] > 0]["Date"].min()
    max_date = vaccination_df[vaccination_df["Percent with one dose"] > 0]["Date"].max()
    vaccination_df["day_num"] = (vaccination_df["Date"] - min_date).dt.days

    vaccination_df = vaccination_df[vaccination_df["Percent with one dose"] > 0].copy()

    return vaccination_df


#######################################################################################
##############THIS SECTION CLEANS AND SETS UP CHARTS FOR DELTA VARIANT VISUALS
#######################################################################################


def getStateVaccinationDataWithAPI():

    """ 
        THIS FUNCTION uses API calls to get the latest vaccination data at the state level
        It also gets the latest covid cases and deaths at the state levels from the NYT site that is regularly updated
        Functions called: None
        Called by: charting procedure
        
        Input arguments: None
        Returns: Three Dataframe 
                    state_vaccine_df, 
                    us_case_rolling_df with rolling average of cases at country = US  level 
                    state_case_rolling_df with rolling average of cases at state level
                 Columns: 
        
    """

    ##########################################################################################################
    # # ### Read the pickle file with stored token
    # pickle_in = open("APIToken.pickle","rb")
    # APITokenIn = pickle.load(pickle_in)
    # curr_offset = 0
    # num_file = 1
    # url = f"https://data.cdc.gov/resource/unsk-b7fc.csv?$$app_token={APITokenIn}&$limit=500000&$offset={curr_offset}&$order=date"
    # response = requests.request("GET", url)
    # df = csv_to_dataframe(response)
    # #df.to_csv(r'..\DataForPresidentialElectionsAndCovid\Dataset 9 State Vaccine Data Using API\StateVaccineDataFile1.csv')
    # curr_offset = curr_offset + 500000
    # num_file = num_file + 1
    # state_vaccine_df = df[['date','location','mmwr_week', 'administered_dose1_recip',  'administered_dose1_recip', 'administered_dose1_pop_pct', ]].copy()

    ############### When developing comment above and uncomment out read from file below ###########################
    folder_name = os.listdir(DataFolder)
    path_name = DataFolder

    state_vaccine_df = pd.DataFrame()
    for name in folder_name:
        if name.startswith("StateVaccineDataFile"):
            df = pd.read_csv(path_name / name)
            df = df[
                [
                    "date",
                    "location",
                    "mmwr_week",
                    "administered_dose1_recip",
                    "administered_dose1_pop_pct",
                ]
            ].copy()
            if len(df) > 0:
                state_vaccine_df = state_vaccine_df.append(df, ignore_index=True)
                # print(name)

    #########################################################################################################

    # Read the county population CSV from local file
    population_df = pd.read_csv(
        DataFolder / r"County Data Till 2020 co-est2020-alldata.csv",
        encoding="latin-1",
    )
    state_pop_df = population_df[population_df["SUMLEV"] != 50].copy()
    state_pop_df = state_pop_df[["STATE", "STNAME", "POPESTIMATE2020"]]
    state_pop_df["st_abbr"] = state_pop_df["STNAME"].map(US_STATE_ABBRV)

    # Merge vaccination and population data on state name
    state_vaccine_df = state_vaccine_df.merge(
        state_pop_df, how="inner", left_on="location", right_on="st_abbr"
    )
    state_vaccine_df = state_vaccine_df.rename(
        columns={
            "STATE": "STATEFP",
            "administered_dose1_pop_pct": "Percent with one dose",
        }
    )

    state_vaccine_df.drop(columns=["st_abbr"], inplace=True)

    state_vaccine_df["date"] = pd.to_datetime(state_vaccine_df["date"])
    min_vaccine_date = state_vaccine_df[state_vaccine_df["Percent with one dose"] > 0][
        "date"
    ].min()
    max_date = state_vaccine_df[state_vaccine_df["Percent with one dose"] > 0][
        "date"
    ].max()
    state_vaccine_df = state_vaccine_df[
        state_vaccine_df["date"] >= min_vaccine_date
    ].copy()
    state_vaccine_df["day_num"] = (state_vaccine_df["date"] - min_vaccine_date).dt.days

    state_vaccine_df["vacc_rank"] = state_vaccine_df.groupby("date")[
        "Percent with one dose"
    ].rank("dense", ascending=True)
    state_vaccine_df["vacc_rank"] = state_vaccine_df["vacc_rank"].astype(int)
    state_vaccine_df["vacc_rank"] = np.where(
        state_vaccine_df["vacc_rank"] > 5, "", state_vaccine_df["vacc_rank"]
    )
    # state_vaccine_df['vacc_rank'] = state_vaccine_df['state'] + " "  + state_vaccine_df['vacc_rank'].astype(str)

    us_case_rolling_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us.csv"
    )
    us_case_rolling_df["date"] = pd.to_datetime(us_case_rolling_df["date"])

    state_case_rolling_df = pd.read_csv(
        "https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-states.csv"
    )
    # state_case_rolling_df.to_csv(DataFolder / r"Dataset 7 Covid/July_21_rolling_average_us-states.csv")
    state_case_rolling_df["date"] = pd.to_datetime(state_case_rolling_df["date"])
    state_case_rolling_df.sort_values(by=["state", "date"], inplace=True)

    state_case_rolling_df = state_case_rolling_df[
        ["date", "geoid", "state", "cases_avg_per_100k", "deaths_avg_per_100k"]
    ].copy()

    us_case_rolling_df = us_case_rolling_df[
        ["date", "geoid", "cases_avg_per_100k", "deaths_avg_per_100k"]
    ].copy()

    state_case_rolling_df["STATEFP"] = state_case_rolling_df["geoid"].str.slice(4)
    state_case_rolling_df["STATEFP"] = state_case_rolling_df["STATEFP"].astype(int)
    state_case_rolling_df.drop(columns=["geoid"], inplace=True)

    state_case_rolling_df = state_case_rolling_df[
        (state_case_rolling_df.date >= min_vaccine_date)
        & (state_case_rolling_df.date <= max_date)
    ]
    us_case_rolling_df = us_case_rolling_df[
        (us_case_rolling_df.date >= min_vaccine_date)
        & (us_case_rolling_df.date <= max_date)
    ]

    return state_vaccine_df, us_case_rolling_df, state_case_rolling_df

