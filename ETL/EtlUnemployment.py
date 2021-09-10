import re
import pandas as pd
import numpy as np
import requests
import json
import sys

sys.path.append("../ETL")
from datetime import datetime, date
from .EtlBase import DataFolder
from .EtlElection import *
from .EtlCovid import *



##########################################################################################
# Get the unemployment data from December 2019 per county using the BLS APIs
##########################################################################################
def get_counties_bls_laus_codes():
    unemployment_df = pd.read_excel(DataFolder / r"laucntycur14.xlsx",
                                    names=["LAUS_code","state_FIPS","county_FIPS","county_name_and_state_abbreviation","Period","labor_force","employed","unemployed","unemployment_rate"],
                                    header=5,
                                    skipfooter=3)
    unemployment_df["LAUS_code"] = unemployment_df["LAUS_code"].apply(lambda x: "LAU" + x + "03")
    list_laus_codes = unemployment_df["LAUS_code"].unique()
    pd.Series(list_laus_codes).to_csv(r"../DataForPresidentialElectionsAndCovid/bls_laus_codes.csv", header=None, index=None)
    
def split_codes_in_chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
    
def get_unemployment_rates_from_api(apy_key):
    bls_laus_codes = list(pd.read_csv(DataFolder / r"bls_laus_codes.csv", header=None).iloc[:,0])
    #for laus_code in bls_laus_codes:
    headers = {'Content-type': 'application/json'}
    # The API only accepts 50 series codes per query
    i=1
    unemployment_df = pd.DataFrame(columns=["series_id","state_FIPS","county_FIPS","year","month","unemployment_rate","footnotes"])
    for list_codes in split_codes_in_chunks(bls_laus_codes, 50):
        print(str(i) + " - Querying for 50 series from " + list_codes[0] + " to " + list_codes[-1])
        data = json.dumps({"seriesid": list_codes,"startyear":"2019", "endyear":"2021", "registrationkey": apy_key})
        r = requests.post("https://api.bls.gov/publicAPI/v2/timeseries/data/", data=data, headers=headers)
        if r.status_code == 200:
            print(str(i) + " - Answer received processing the data")
            json_data = json.loads(r.text)
            for series in json_data['Results']['series']:
                seriesId = series['seriesID']
                state_fips = seriesId[5:7]
                county_fips = seriesId[7:10]
                for item in series['data']:
                    year = item['year']
                    month = int(item['period'][1:])
                    unemployment_rate = item['value']
                    footnotes=""
                    for footnote in item['footnotes']:
                        if footnote:
                            footnotes = footnotes + footnote['text'] + ','

                    if 1 <= month <= 12:
                        _row = pd.Series([seriesId,state_fips,county_fips,year,month,unemployment_rate,footnotes[0:-1]], index=unemployment_df.columns)
                        unemployment_df = unemployment_df.append(_row, ignore_index=True)
            print(str(i) + " - Dataframe length = " + str(len(unemployment_df)))
            i+=1
        else:
             print(str(i) + " - ERROR - code = " + str(r.status_code))
    unemployment_df.to_csv(r"../DataForPresidentialElectionsAndCovid/bls_unemployment_rates.csv", header=None, index=None)


    
##########################################################################################
# Get the pre-pandemic December 2019 data
##########################################################################################
def getUnemploymentRateSince122019():
    #
    # Prepare unemployment Data
    # 
    unemployment_df = pd.read_csv(DataFolder / r"bls_unemployment_rates.csv",
                                    names=["LAUS_code","state_fips","county_fips","year","month","unemployment_rate","footnotes"],
                                    header=0)
    # Convert year and month to datetime
    unemployment_df["month"] = unemployment_df.apply(lambda x: pd.to_datetime(f"{x['year']}-{x['month']}", format="%Y-%m").to_period('M'), axis=1)
    # Keep only the data after December 2019
    unemployment_df = unemployment_df[(unemployment_df["month"]>=pd.to_datetime("2019-12", format="%Y-%m").to_period('M'))]
    # Format the county FIPS as the state FIPS followed by the county FIPS
    concatenate_fips = lambda x : int(str(x["state_fips"]) + "{:03d}".format(x["county_fips"]))
    unemployment_df["COUNTYFP"] = unemployment_df.apply(concatenate_fips, axis=1)
    # Keep only US mainland states
    unemployment_df = unemployment_df[unemployment_df["COUNTYFP"] < 57000]
    # Calculate for each record the number of month since the start
    first_month = unemployment_df["month"].min()
    calculate_month_since_start = lambda x : (x - first_month).n + 1
    unemployment_df["month_since_start"] = unemployment_df["month"].apply(calculate_month_since_start)
    unemployment_df["unemployment_rate"] = unemployment_df["unemployment_rate"].astype("float64")
    #
    # Merge election data at the county level
    #
    unemployment_df.drop(columns=["state_fips", "county_fips", "LAUS_code","year","footnotes"], inplace=True)
    election_df = getElectionData()
    election_df = election_df[["COUNTYFP", "party_winner_2020"]]
    election_df.rename(columns={"party_winner_2020": "party"}, inplace = True)
    unemployment_df = pd.merge(unemployment_df, election_df, how="left", on="COUNTYFP" )
    return unemployment_df

##########################################################################################
# Merge the unemployment and Covid cases and death data
##########################################################################################
def getUnemploymentCovidBase():
    """
        THIS FUNCTION reads the county level unemployment rate from the 2020 dataset published by the BLS
        and 
        
        Functions called: 
        
        Input: 
            level (str): "county" or "state". Indicate the level at which the data should be aggregated.
        Returns: Dataframe unemployment_covid_df
                
    """
    
    #
    # Prepare unemployment Data
    # 
    unemployment_df = pd.read_csv(DataFolder / r"bls_unemployment_rates.csv",
                                    names=["LAUS_code","state_fips","county_fips","year","month","unemployment_rate","footnotes"],
                                    header=0)
    # Convert year and month to datetime
    unemployment_df["month"] = unemployment_df.apply(lambda x: pd.to_datetime(f"{x['year']}-{x['month']}", format="%Y-%m").to_period('M'), axis=1)
    # Keep only the data from January 2020 (we only have Covid cases from that month)
    unemployment_df = unemployment_df[(unemployment_df["month"]>=pd.to_datetime("2020-01", format="%Y-%m").to_period('M'))]
    # Format the county FIPS as the state FIPS followed by the county FIPS
    concatenate_fips = lambda x : int(str(x["state_fips"]) + "{:03d}".format(x["county_fips"]))
    unemployment_df["COUNTYFP"] = unemployment_df.apply(concatenate_fips, axis=1)
    # Keep only US mainland states
    unemployment_df = unemployment_df[unemployment_df["COUNTYFP"] < 57000]
    # Calculate for each record the number of month since the start
    first_month = unemployment_df["month"].min()
    unemployment_df["unemployment_rate"] = unemployment_df["unemployment_rate"].astype("float64")
    unemployment_df.drop(columns=["state_fips", "county_fips", "LAUS_code","year","footnotes"], inplace=True)
    #
    # Prepare and merge Covid case and death rates data
    #
    covid_df = getCasesRollingAveragePer100K()
    # Remove non mainland US states
    covid_df = covid_df[covid_df["COUNTYFP"] < 57000]
    # Change period to month and average cases per 100K per month and county
    covid_df["month"] = covid_df["date"].dt.to_period('M')
    covid_df.drop(columns=["date"], inplace=True)
    covid_df = covid_df.groupby(["month", "COUNTYFP"]).sum()
    covid_df.reset_index(inplace=True)
    
    unemployment_covid_df = pd.merge(unemployment_df, covid_df, how="left", on=["month", "COUNTYFP"])
    
    #
    # Merge election data at the county level
    #
    election_df = getElectionData()
    election_df = election_df[["COUNTYFP", "party_winner_2020"]]
    election_df.rename(columns={"party_winner_2020": "party"}, inplace = True)
    unemployment_covid_df = pd.merge(unemployment_covid_df, election_df, how="left", on="COUNTYFP" )
    return unemployment_covid_df


def getUnemploymentCovidCorrelationPerMonth(df=None):
    if df is None:
        unemployment_covid_df = getUnemploymentCovidBase()
    else:
        unemployment_covid_df = df.copy()
    # Remove useless data for this dataset
    unemployment_covid_df.drop(columns=["COUNTYFP", "deaths_avg_per_100k"], inplace=True)
    unemployment_covid_df = unemployment_covid_df[unemployment_covid_df["party"] != "OTHER"]
    # Compute the monthly correlation between cases_avg_per_100k and unemployment_rate
    unemployment_covid_df["month"] = unemployment_covid_df["month"].astype(str)
    monthly_correlation_df = unemployment_covid_df.groupby(["month", "party"])[["cases_avg_per_100k", "unemployment_rate"]].corr().iloc[
                             0::2, -1]
    monthly_correlation_df = monthly_correlation_df.reset_index()
    monthly_correlation_df.drop(columns=["level_2"], inplace=True)
    monthly_correlation_df.rename(columns={"unemployment_rate": "correlation"}, inplace=True)
    #Merge the two
    unemployment_covid_df = unemployment_covid_df.groupby(["month", "party"]).mean()
    unemployment_covid_df.reset_index(inplace=True)
    unemployment_covid_correlation_df = pd.merge(unemployment_covid_df, monthly_correlation_df, how="left", on=["month", "party"])
    # Rename data columns and Melt the dataframe for Altair
    unemployment_covid_correlation_df.rename(
        columns={"unemployment_rate": "Average Unemployment Rate", "cases_avg_per_100k": "Average Covid Cases per 100k",
                 "correlation": "Correlation"},
        inplace=True)
    unemployment_covid_correlation_df = unemployment_covid_correlation_df.melt(
        id_vars=[
            "month",
            "party",
        ],
        value_vars=["Average Unemployment Rate", "Average Covid Cases per 100k", "Correlation"],
        col_level=None,
        ignore_index=True,
    )
    return unemployment_covid_correlation_df


def getJuly2020UnemploymentAndMask(df=None):
    if df is None:
        unemployment_covid_df = getUnemploymentCovidBase()
    else:
        unemployment_covid_df = df.copy()
    county_mask_df = pd.read_csv( DataFolder / r"mask-use-by-county.csv",index_col=0)
    july_2020 = pd.to_datetime("2020-07", format="%Y-%m").to_period('M')

    # Mask Data are from July 2020
    # So keep only the unemployment and covid data until July 2020 and aggregate
    unemployment_covid_july_df = unemployment_covid_df[unemployment_covid_df["month"] <= july_2020]
    unemployment_covid_july_df.drop(columns=["month"])
    unemployment_covid_july_df = unemployment_covid_july_df.groupby(["COUNTYFP"]).agg({
            "unemployment_rate": lambda x : x.mean(),
            "cases_avg_per_100k": lambda x : x.sum(),
            "deaths_avg_per_100k": lambda x : x.sum(),
            "party": "first"
        })
    unemployment_covid_july_df.reset_index(inplace=True)

    # Merge the Mask dataset
    unemployment_mask_july_df = pd.merge(unemployment_covid_july_df, county_mask_df, how="left", on="COUNTYFP")

    unemployment_mask_july_df = unemployment_mask_july_df.melt(
        id_vars=[
            "COUNTYFP",
            "unemployment_rate",
            "cases_avg_per_100k",
            "deaths_avg_per_100k",
            "party",
        ],
        value_vars=["NEVER", "RARELY", "SOMETIMES", "FREQUENTLY", "ALWAYS"],
        var_name="mask_usage_type",
        value_name="mask_usage",
        col_level=None,
        ignore_index=True,
    )

    # Create two groups
    unemployment_mask_july_df["mask_usage_type"] = pd.Series(
        np.where(
            unemployment_mask_july_df["mask_usage_type"].isin(["ALWAYS", "FREQUENTLY"]),
            "FREQUENT",
            "NOT FREQUENT",
        )
    )
    # Add up the new groupings of FREQUENT AND NON FREQUENT
    unemployment_mask_july_df = (
        unemployment_mask_july_df.groupby(
            [
                "COUNTYFP",
                "unemployment_rate",
                "cases_avg_per_100k",
                "deaths_avg_per_100k",
                "party",
                "mask_usage_type",
            ]
        )["mask_usage"]
            .sum()
            .reset_index()
    )
    unemployment_freq_mask_july_df = unemployment_mask_july_df[
        unemployment_mask_july_df["mask_usage_type"] == "FREQUENT"]
    unemployment_infreq_mask_july_df = unemployment_mask_july_df[
        unemployment_mask_july_df["mask_usage_type"] == "NOT FREQUENT"]
    return unemployment_freq_mask_july_df, unemployment_infreq_mask_july_df


def getUnemploymentVaccineCorrelationPerMonth(df=None):
    if df is None:
        unemployment_df = getUnemploymentRateSince122019()
    else:
        unemployment_df = df.copy()
    # Remove data from December 2019 (pre-covid)
    unemployment_df = unemployment_df[unemployment_df["month_since_start"] != 1]
    unemployment_df.drop(columns=["month_since_start"], inplace=True)

    county_vaccine_df = pd.read_csv(DataFolder / r"COVID-19_Vaccinations_in_the_United_States_County.zip",
                                    compression="zip")
    county_vaccine_df = county_vaccine_df[["Date", "FIPS", "Recip_County", "Recip_State", "Administered_Dose1_Pop_Pct"]]
    county_vaccine_df = county_vaccine_df.rename(
        columns={
            "FIPS": "COUNTYFP",
            "Administered_Dose1_Pop_Pct": "percent_with_1_dose",
        }
    )
    # Remove unknown counties and non mainland US states and unknown counties
    county_vaccine_df = county_vaccine_df[county_vaccine_df["COUNTYFP"] != "UNK"]
    county_vaccine_df["COUNTYFP"] = county_vaccine_df["COUNTYFP"].astype("int")
    county_vaccine_df = county_vaccine_df[county_vaccine_df["COUNTYFP"] < 57000]
    # Get the month as a period
    county_vaccine_df["month"] = pd.to_datetime(county_vaccine_df["Date"], format="%m/%d/%Y").dt.to_period('M')
    county_vaccine_df = county_vaccine_df.groupby(["month", "COUNTYFP"]).max()
    county_vaccine_df.reset_index(inplace=True)
    county_vaccine_df.drop(columns=["Date"], inplace=True)
    #Merg unemployment and vaccination
    unemployment_vaccine_df = pd.merge(county_vaccine_df, unemployment_df, how="left", on=["month", "COUNTYFP"])
    unemployment_vaccine_df.drop(columns=["COUNTYFP"], inplace=True)
    unemployment_vaccine_df.dropna(inplace=True)
    unemployment_vaccine_df["month"] = unemployment_vaccine_df["month"].astype(str)
    # Compute the monthly correlation between cases_avg_per_100k and unemployment_rate
    monthly_correlation_df = unemployment_vaccine_df.groupby(["month", "party"])[
                                 ["percent_with_1_dose", "unemployment_rate"]].corr().iloc[
                             0::2, -1]
    monthly_correlation_df = monthly_correlation_df.reset_index()
    monthly_correlation_df.drop(columns=["level_2"], inplace=True)
    monthly_correlation_df.rename(columns={"unemployment_rate": "correlation"}, inplace=True)
    # Merge the two
    unemployment_vaccine_df = unemployment_vaccine_df.groupby(["month", "party"]).mean()
    unemployment_vaccine_df.reset_index(inplace=True)
    unemployment_vaccine_df = pd.merge(unemployment_vaccine_df, monthly_correlation_df, how="left",
                                       on=["month", "party"])
    # Rename column names and Melt for Altair
    unemployment_vaccine_df.rename(
        columns={"unemployment_rate": "Average Unemployment Rate",
                 "percent_with_1_dose": "Average % of People with 1 Dose of Vaccine",
                 "correlation": "Correlation"},
        inplace=True)
    unemployment_vaccine_df = unemployment_vaccine_df.melt(
        id_vars=[
            "month",
            "party",
        ],
        value_vars=["Average Unemployment Rate", "Average % of People with 1 Dose of Vaccine",
                    "Correlation"],
        col_level=None,
        ignore_index=True,
    )
    return unemployment_vaccine_df