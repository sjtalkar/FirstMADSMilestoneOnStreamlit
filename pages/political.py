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

# Party affiliation and COVID case trend
###########################################
def app():
    st.header(
        "Is There an Observable Correlation Between Political Affiliation and Population Response to the COVID Pandemic?",
        anchor="main_question_subheader",
    )

    st.subheader(
        "Party affiliation and COVID case trend in Presidential election year of 2020",
        anchor="partyandcovid",
    )

    st.markdown(
        """
    The basis of this project began with the observations derived from the visualization below. 
    The **task** is to determine if there is a significant difference in the rate of rise of COVID cases between 
    normalized (per 100K) populations that professes affiliation to one party or another (Republican, Democrat and Other). 
    The **data** to be analyzed was the county level COVID confirmed cases, joined with Presidential election data 
    from 2016 and 2020.
    We differentiate between populations that voted Republican, Democrat or Other. The affiliation was further sectioned 
    into those that stayed loyal to a party from 2016 to 2020, in contrast to those that were perhaps more influenced 
    by the political messaging and switched loyalties. The number of cases plotted along the y-axis is the seven-day 
    rolling average rather than **raw numbers** which can reflect data collection and delay errors.

    From the visualization we observed that the rate of rise of the infection was markedly higher, towards the end of 
    the first year of the pandemic, in the populations that voted Republican (remained loyal in 2020 or switched from 2016).  
    """
    )

    # Get rolling average of cases by segment
    # @st.cache #Remove some caching to reduce memory usage due to Streamlit limitations
    def load_case_rolling_df():
        df = pd.read_csv("./data/case_rolling_df.csv")
        return df

    case_rolling_df = load_case_rolling_df()
    # Create the chart
    (
        base,
        make_selector,
        highlight_segment,
        radio_select,
    ) = createCovidConfirmedTimeseriesChart(case_rolling_df)
    selectors, rules, points, tooltip_text = createTooltip(
        base, radio_select, case_rolling_df
    )

    st.markdown("""---""")
    # Bring all the layers together with layering and concatenation
    st.altair_chart(
        (
            alt.layer(highlight_segment, selectors, points, rules, tooltip_text)
            | make_selector
        ).configure_title(align="left", anchor="start")
    )

    st.markdown("""---""")

    # Strength of affiliation and COVID deaths at County level
    ###########################################
    st.subheader("Strength of affiliation and COVID deaths at County level")
    st.markdown(
        """
    Does strength of affiliation, as determined by the percentile point change in votes received by a party in 2020 
    over 2016, show any correlation to the number of COVID related deaths in that county? 
    With the below visual, we compared the counties voting for each party that suffered the most deaths per 100K population.
    The scatter plot is divided into four quadrants.
    The quadrant to the top right contains counties with most deaths and more percentile point change in votes in favor 
    of a party.
    By selecting each segment in the dropdown the counties that Stayed Democrat suffered marginally less than those that 
    Stayed Republican.

    > [Chart Design Credit to NPR](https://www.npr.org/sections/health-shots/2020/11/06/930897912/many-places-hard-hit-by-covid-19-leaned-more-toward-trump-in-2020-than-2016)
    """
    )

    st.markdown("""---""")

    # election_change_and_covid_death_df = pd.read_csv(
    #     "./data/election_change_and_covid_death_df.csv"
    #
    # Remove some caching to reduce memory usage due to Streamlit limitations)
    # @st.cache
    def load_percentile_point_deaths():
        df = pd.read_csv("./data/percentile_point_deaths.csv")
        return df

    election_change_and_covid_death_df = pd.read_csv(
        "./data/percentile_point_deaths.csv"
    )
    st.altair_chart(
        createPercentPointChangeAvgDeathsChart(
            election_change_and_covid_death_df
        ).configure_title(align="left", anchor="start")
    )

    df = election_change_and_covid_death_df.copy()
    df["deaths_avg_per_100k"] = df["deaths_avg_per_100k"].astype("float")
    df["pct_increase"] = df["pct_increase"].astype("float")
    col1, col2, col3, col4 = st.beta_columns(4)
    formatted_string = "{:.2f}".format(
        election_change_and_covid_death_df["deaths_avg_per_100k"].mean()
    )
    st.write(f"All counties Average Deaths = {formatted_string}")

    for segmentname in [
        "Stayed Democrat",
        "Stayed Republican",
    ]:
        num = len(
            df[
                (df["deaths_avg_per_100k"] >= 1.25)
                & (df["pct_increase"] >= 0)
                & (df["segmentname"] == segmentname)
            ]
        )
        denom = len(
            df[
                (df["segmentname"].str.contains(segmentname.replace("To ", "")))
                | (df["segmentname"].str.contains(segmentname.replace("Stayed ", "")))
            ]
        )
        formatted_string = "{:.4f}".format(num / denom)

        if segmentname == "Stayed Democrat":
            col1.write(f"Fraction of counties in fourth quadrant(per party): ")
            col2.write(f"{segmentname} = {formatted_string}")
        else:
            col3.write(f"{segmentname} = {formatted_string}")

    st.markdown("""---""")

    # Affiliation and Vaccine Adoption Rates By State
    ###########################################
    st.subheader("Affiliation and Vaccine Adoption Rates By State")
    st.markdown(
        """To allow the user to wield the power to pause and view the rate at which states in the U.S. adopted the COVID 
    vaccines after it became available, the below visual offers a slider bar with a duration from first shot as range. 
    As Cassie Kozyrkov writes [here](https://towardsdatascience.com/analytics-is-not-storytelling-a1fe61b1ab6c), 
    "As an analyst, I’m not here to funnel you towards my opinion. I’m here to help you form your own."
    In employing interaction in the below visual (originally seen in static form at this 
    [NPR site](https://www.npr.org/2021/06/09/1004430257/theres-a-stark-red-blue-divide-when-it-comes-to-states-vaccination-rates),
    we notice clearly that "blue" states surged forward in vaccinations earlier than the red states after about three 
    months after its release. 
    The size of the bubbles in the chart below is scaled by population of each state.
    The X-axis positions each state by the percent of its population with at least one shot (since some vaccines require 
    only one shot).
    """
    )

    st.markdown("""---""")

    daily_vaccination_percent_df = pd.read_csv(
        "./data/daily_vaccination_percent_df.csv"
    )
    daily_vaccination_percent_df["Total population"] = daily_vaccination_percent_df[
        "Total population"
    ].astype("int")
    daily_vaccination_percent_df["day_num"] = daily_vaccination_percent_df[
        "day_num"
    ].astype("int")
    daily_vaccination_percent_df[
        "Percent with one dose"
    ] = daily_vaccination_percent_df["Percent with one dose"].astype("float")

    st.altair_chart(
        createDailyInteractiveVaccinationChart(daily_vaccination_percent_df)
    )

    st.markdown("""---""")

    # Vaccinations and the Delta Variant Case Resurgence
    ###########################################
    st.subheader("Vaccinations and the Delta Variant Case Resurgence")
    st.markdown(
        """The chart below allows for selection of a state in the map to learn about case trend
    for the period after the first Delta variant was detected in the US. The US average and per political affiliation 
    averages are also plotted for baseline comparison.

    Efficacy of the vaccine over time, for this pandemic, can only be measured as time progresses, since we do not have a 
    precedent. Mutation of the virus is inevitable and immunity response is constantly being monitored.
    The below visualization presents the resurgence in COVID cases that are observed to be rising especially in states with 
    low adoption. We compare an individual state's trend with mean trends pertaining to the US, combined mean of states that 
    voted Republican and states that voted Democrat. It was noted that the resurgent rising trends were notably seen in 
    states such as Louisiana, Missouri, and Florida where the numbers rose well above all the means. These are "red" states. 
    Vermont has a high vaccination adoption and a notably lower trend. Most of the states that voted Democrat also have 
    trends that initially spiked and later settled closer to their mean.
    """
    )

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_state_vaccine_df():
        df = pd.read_csv("./data/state_vaccine_df.csv")
        df["STATEFP"] = df["STATEFP"].astype("int")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_us_case_rolling_df():
        df = pd.read_csv("./data/us_case_rolling_df.csv")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_state_case_rolling_df():
        df = pd.read_csv("./data/state_case_rolling_df.csv")
        df["cases_avg_per_100k"] = df["cases_avg_per_100k"].astype("float")
        df["STATEFP"] = df["STATEFP"].astype("int")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_state_election_df():
        df = pd.read_csv("./data/state_election_df.csv")
        df["state_fips"] = df["state_fips"].astype("int")
        df["candidatevotes"] = df["candidatevotes"].astype("int")
        df["totalvotes"] = df["totalvotes"].astype("int")
        df["fractionalvotes"] = df["fractionalvotes"].astype("float")
        return df

    state_vaccine_df = load_state_vaccine_df()
    us_case_rolling_df = load_us_case_rolling_df()
    state_case_rolling_df = load_state_case_rolling_df()
    state_election_df = load_state_election_df()

    (
        vaccine_chart,
        us_timeseries,
        stayed_democrat_timeseries,
        stayed_republican_timeseries,
        state_cases_delta_chart,
        state_selectors,
        rules,
        tooltip_text2,
        tooltip_text3,
        tooltip_text4,
        tooltip_text5,
        points,
        rect_area,
        delta_rect_area,
        just_line_state_cases_delta,
    ) = createCombinedVaccinationAndDeltaVariantTrend(
        state_vaccine_df, us_case_rolling_df, state_case_rolling_df, state_election_df
    )

    st.markdown("""---""")

    st.altair_chart(
        (
            vaccine_chart
            & alt.layer(
                (
                    state_cases_delta_chart
                    + us_timeseries
                    + stayed_democrat_timeseries
                    + stayed_republican_timeseries
                    + rect_area
                    + delta_rect_area
                ),
                state_selectors,
                rules,
                tooltip_text2,
                tooltip_text3,
                tooltip_text4,
                tooltip_text5,
                points,
            )
        ).configure_title()
        # .properties(width=200, height=100)
    )

    st.markdown("""---""")

    # Mask Usage by political affiliation
    ###########################################
    st.subheader("Frequent and Infrequent Mask Usage by Political affiliation")
    st.markdown(
        """
    Mask usage data was collected in a survey by New York Times (through a professional survey firm). The data was 
    gathered from 250,000 people surveyed in a two week period in July 2020 (please see details in Appendix). 
    The five choices offered: Never, Rarely, Sometimes, Frequently Always. The estimations of all five for every county, 
    provided as a float adds up to 1.
    This was binned into Not Frequent (Never, Rarely, Sometimes) and Frequent (Frequently, Always) usage which 
    for every county now adds up to 1. Binning is a common technique used to convert a quantitative data into a categorical
    value and this technique was once again applied to bin the estimates into ranges of Low, Medium and High chance of 
    frequent and infrequent usage of masks.
    
    The density plot of mask usage, shows the distribution of infrequent and frequent mask usage among counties (that the 
    surveyed participant resides in) that voted Democrat or Republican.
    We see that relatively, there is a higher probability of mask usage among the counties voting for Democrats over the 
    Republicans.

    To drill into the distribution, the spatial map can be studied at a lower granularity of each county. 
    It also shows that CDC masking guidelines are better appreciated in the well-populated areas along the east 
    and west urban coast of the US (irrespective of affiliation)-select Democrat/Republican - High Mask usage in Frequent 
    mask usage chart. In the heartland, a lukewarm acceptance to the guidelines is observed - select Democrat/Republican 
    Low mask usage in Infrequent mask usage chart. 
    """
    )

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_mask_distribution_df():
        df = pd.read_csv("./data/mask_distribution_df.csv")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_county_pop_mask_df():
        df = pd.read_csv("./data/county_pop_mask_df.csv")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_county_pop_mask_freq_df():
        df = pd.read_csv("./data/county_pop_mask_freq_df.csv")
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_county_pop_mask_infreq_df():
        df = pd.read_csv("./data/county_pop_mask_infreq_df.csv")
        return df

    mask_distribution_df = load_mask_distribution_df()
    #NOTE THIS HAS BEEN COMMENTED OUT
#    st.altair_chart(createMaskUsageDistributionChart(mask_distribution_df))

    county_pop_mask_df = load_county_pop_mask_df()
    county_pop_mask_freq_df = load_county_pop_mask_freq_df()
    county_pop_mask_infreq_df = load_county_pop_mask_infreq_df()

#     freq, infreq = st.beta_columns(2)
    (
        county_mask_chart,
        legend_republican,
        legend_democrat,
        average_mask_chart,
    ) = createFreqCountyMaskUsageWithRanges(
        "FREQUENT",
        county_pop_mask_df,
        county_pop_mask_freq_df,
        county_pop_mask_infreq_df,
        mask_distribution_df,
    )
    st.altair_chart(
        (
            (county_mask_chart)
            & (average_mask_chart | legend_republican | legend_democrat).resolve_scale(
                color="independent"
            )
        ).configure_title(align="left", anchor="start")
    )

    (
        county_mask_chart,
        legend_republican,
        legend_democrat,
        average_mask_chart,
    ) = createFreqCountyMaskUsageWithRanges(
        "INFREQUENT",
        county_pop_mask_df,
        county_pop_mask_freq_df,
        county_pop_mask_infreq_df,
        mask_distribution_df,
    )

    st.altair_chart(
       (
        (county_mask_chart)
            & (average_mask_chart | legend_republican | legend_democrat).resolve_scale(
                color="independent"
            )
        ).configure_title(align="left", anchor="start")
    )
    st.markdown("""---""")
