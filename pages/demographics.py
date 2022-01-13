import pandas as pd
import numpy as np
import base64
import re
import time

import altair as alt
from pathlib import Path
import streamlit as st
from PIL import Image

from Visualization.VizBase import createTooltip, createCovidConfirmedTimeseriesChart
from Visualization.VizCovid import createPercentPointChangeAvgDeathsChart
from Visualization.VizVaccine import (
    createStateVaccinationChart,
    createDailyInteractiveVaccinationChart,
    createCombinedVaccinationAndDeltaVariantTrend,
    altairTestFunction,
)
from Visualization.VizMask import (
    createMaskUsageDistributionChart,
    createFreqCountyMaskUsageWithRanges,
)
from Visualization.VizUnemployment import (
    createUnemploymentChart,
    createUnemploymentCorrelationLineChart,
    createUnemploymentCorrelationLineCombinedChart,
    createUnemploymentMaskChart,
)
from Visualization.VizUrbanRural import (
    ElectionUrbanRuralDensityPlot,
    UrbanRuralCorrelation,
    UrbanRuralRollingAvgCompChart,
    UrbanRuralRollingAvgSingleChart,
    UrbanRuralAvgDeathsCompChart,
    UrbanRuralMaskPlots,
)

# Import necessary libraries
import streamlit as st

from Multiapp import MultiPage

def app():
    
    # Unemployment rate and COVID
    ###########################################
    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_rural_election_df():
        df = pd.read_csv(
            "./data/urban_rural_election_df.csv",
            dtype={
                "state_po": str,
                "county_name": str,
                "county_fips": int,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "UrbanRural": str,
                "PctRural": float,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_rural_rolling_avg_full_df():
        df = pd.read_csv(
            "./data/urban_rural_rolling_avg_full_df.csv",
            dtype={
                "year": int,
                "state": str,
                "state_po": str,
                "county_name": str,
                "county_fips": float,
                "office": str,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "version": int,
                "mode": str,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_rolling_avg_full_df():
        df = pd.read_csv(
            "./data/urban_rolling_avg_full_df.csv",
            dtype={
                "year": int,
                "state": str,
                "state_po": str,
                "county_name": str,
                "county_fips": float,
                "office": str,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "version": int,
                "mode": str,
                "UrbanRural": str,
                "PctRural": float,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_rural_rolling_avg_full_df():
        df = pd.read_csv(
            "./data/rural_rolling_avg_full_df.csv",
            dtype={
                "year": int,
                "state": str,
                "state_po": str,
                "county_name": str,
                "county_fips": float,
                "office": str,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "version": int,
                "mode": str,
                "UrbanRural": str,
                "PctRural": float,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_rural_avgdeaths_full_df():
        df = pd.read_csv(
            "./data/urban_rural_avgdeaths_full_df.csv",
            dtype={
                "COUNTYFP": int,
                "deaths_avg_per_100k": float,
                "state": str,
                "state_po": str,
                "CTYNAME": str,
                "party_winner_2020": str,
                "totalvotes_2020": float,
                "fractionalvotes_2020": float,
                "party_winner_2016": str,
                "totalvotes_2016": float,
                "fractionalvotes_2016": float,
                "changecolor": str,
                "_merge": str,
                "pct_increase": float,
                "segmentname": str,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_avgdeaths_full_df():
        df = pd.read_csv(
            "./data/urban_avgdeaths_full_df.csv",
            dtype={
                "COUNTYFP": int,
                "deaths_avg_per_100k": float,
                "state": str,
                "state_po": str,
                "CTYNAME": str,
                "party_winner_2020": str,
                "totalvotes_2020": float,
                "fractionalvotes_2020": float,
                "party_winner_2016": str,
                "totalvotes_2016": float,
                "fractionalvotes_2016": float,
                "changecolor": str,
                "_merge": str,
                "pct_increase": float,
                "segmentname": str,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_rural_avgdeaths_full_df():
        df = pd.read_csv(
            "./data/rural_avgdeaths_full_df.csv",
            dtype={
                "COUNTYFP": int,
                "deaths_avg_per_100k": float,
                "state": str,
                "state_po": str,
                "CTYNAME": str,
                "party_winner_2020": str,
                "totalvotes_2020": float,
                "fractionalvotes_2020": float,
                "party_winner_2016": str,
                "totalvotes_2016": float,
                "fractionalvotes_2016": float,
                "changecolor": str,
                "_merge": str,
                "pct_increase": float,
                "segmentname": str,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_urban_mask_df():
        df = pd.read_csv(
            "./data/urban_mask_df.csv",
            dtype={
                "state_po": str,
                "county_name": str,
                "county_fips": int,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "UrbanRural": str,
                "PctRural": float,
                "Infrequent": float,
                "Frequent": float,
            },
        )
        return df


    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_rural_mask_df():
        df = pd.read_csv(
            "./data/rural_mask_df.csv",
            dtype={
                "state_po": str,
                "county_name": str,
                "county_fips": int,
                "candidate": str,
                "party": str,
                "candidatevotes": float,
                "totalvotes": float,
                "UrbanRural": str,
                "PctRural": float,
                "Infrequent": float,
                "Frequent": float,
            },
        )
        return df


    urban_rural_election_df = load_urban_rural_election_df()

    urban_rural_rolling_avg_full_df = load_urban_rural_rolling_avg_full_df()
    urban_rolling_avg_full_df = load_urban_rolling_avg_full_df()
    rural_rolling_avg_full_df = load_rural_rolling_avg_full_df()

    urban_rural_avgdeaths_full_df = load_urban_rural_avgdeaths_full_df()
    urban_avgdeaths_full_df = load_urban_avgdeaths_full_df()
    rural_avgdeaths_full_df = load_rural_avgdeaths_full_df()

    urban_mask_df = load_urban_mask_df()
    rural_mask_df = load_rural_mask_df()

    st.header(
        "Does the Urban/Rural Demographic Influence the COVID Response?",
        anchor="urbanruralandcovid",
    )

    st.markdown(
        """
    Among the socioeconomic factors frequently and strongly associated with political affiliation is the urban/rural 
    demographic of the voting population. Could this factor influence the pattern we have seen above, of the COVID-19 
    effects being split along party lines?

    The Census Bureau defines urban areas by population size, specifically 2,500 or greater. Also from the Census Bureau, 
    we obtained a list of US counties with a ‘percent rural’ designation, meaning the percentage of county population 
    living in rural areas.
    """
    )

    st.subheader("Political affiliation")

    st.markdown(
        """
    Since we want to see the effect of political affiliation on the COVID response, the next question is: How strongly 
    democrat or republican were those counties? For that, we used the ratio of winning party votes to total votes, which 
    we call the ‘vote fraction’. Plotting against the Percent Rural designation of each county, we find no correlation 
    (-0.07) for counties won by the democratic candidate, and a weak positive correlation (0.25) for counties won by the 
    republican candidate.
    """
    )

    #COMMENTED OUT THE DENSITY PLOT
    #st.altair_chart(ElectionUrbanRuralDensityPlot(urban_rural_election_df))

    st.markdown(
        """
    Merging that with the presidential election county results, we see there seems to be a clear divide in political 
    affiliation between rural areas and urban centers. Counties less than about 32% rural were more likely to vote democrat,
    while those above were more likely to vote republican.

    The merge was done on the county FIPS code, and about 40 counties were lost in the merge due to mismatches. Out of 
    more than 3000 counties, this was considered an acceptable loss.
    """
    )

    st.altair_chart(UrbanRuralCorrelation(urban_rural_election_df))

    st.markdown(
        """
    This is a positive initial result, since it implies that the urban/rural nature of a county has little to no effect 
    on the strength of the affiliation.

    Finally, we come to the main question, which is whether the urban/rural nature has an effect on the effects of the 
    COVID pandemic, indicated by the rolling case average and the deaths.
    """
    )

    st.subheader("COVID effects")

    st.markdown(
        """
    The Census Bureau classifies counties with 50% or more of their population living in rural areas as ‘mostly rural’, 
    while the remainder are classified as ‘mostly urban’. We split the counties by that designation, and for each, we repeat 
    the analyses performed above.
    """
    )


    st.altair_chart(
        UrbanRuralRollingAvgCompChart(
            urban_rural_rolling_avg_full_df,
            urban_rolling_avg_full_df,
            rural_rolling_avg_full_df,
        )
    )

    st.altair_chart(
        UrbanRuralAvgDeathsCompChart(
            urban_rural_avgdeaths_full_df, urban_avgdeaths_full_df, rural_avgdeaths_full_df
        )
    )

    st.markdown(
        """
    For COVID rolling case average, we find that the same trends hold as those found earlier for all counties: Initially, 
    the case numbers are higher for counties that voted Democrat, but in September 2020, the rise in case numbers for 
    counties that voted Republican is steeper.

    As for COVID deaths, we also find the same trends hold for both urban and rural counties as those found earlier for 
    the complete set of counties: The number of deaths per 100K population is higher for more counties that are strongly 
    republican.
    """
    )

    st.subheader("COVID response")

    st.markdown(
        """
    For influence of the urban/rural nature of the counties on the COVID response, we look at frequency of mask usage, 
    as defined earlier.
    """
    )

    #COMMENTED OUT THE UrbanRuralMaskPlots
    #st.altair_chart(UrbanRuralMaskPlots(urban_mask_df, rural_mask_df))

    st.markdown(
        """
    We find the same trends, unchanged, as in the analysis of total counties: Counties won by the Democratic candidate, 
    compared to those won by the Republican candidate, were more likely to use masks frequently, and less likely to use 
    them infrequently. This trend held for both counties classified as urban and those classified as rural.

    So we can conclude that the urban or rural nature of a county does not have an influence either
    * on effects of the COVID pandemic as represented by the rolling case average and the death rate
    * or on response to the COVID pandemic as represented by the frequency of mask usage.

    """
    )

    st.markdown("""---""")

