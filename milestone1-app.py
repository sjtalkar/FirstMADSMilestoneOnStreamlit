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

# from Visualization.VizUnemployment import (
#     createUnemploymentChart,
#     createUnemploymentCorrelationLineChart,
#     createUnemploymentMaskChart,
# )
# from Visualization.VizUrbanRural import (
#     ElectionUrbanRuralDensityPlot,
#     UrbanRuralCorrelation,
# )

DataFolder = Path("./data/")

# Set streamlit page to wide format
st.set_page_config(layout="wide")

# Show the header image
bkgd_image = Image.open("./images/title-background.jpg")
st.image(bkgd_image, use_column_width=True)


# Introduction
###########################################
st.markdown(
    """The Nigerian Igbo word “igwebuike”, which means “there is strength in community.” paraphrases the ideal response to the Covid pandemic. To build herd immunity and stop its spread, within and outside borders, a cohesive and co-operative front is called for. However, amidst this pandemic, there is a suggestion that the U.S. has never been as divided as in recent years.

In a year of presidential elections, the leadership rhetoric and messaging regarding Covid response and behavior, as projected by the media, appears to starkly differ along political ideological lines, specifically, Democrat versus Republican. Usage of masks, openness to vaccination and a general appreciation of the severity of the pandemic, as portrayed to the public, arouses curiosity as to whether the response is truly divided along party lines.

We will also explore if other factors, commonly associated with political affiliation, differentiate the response by communities towards US Centers for Disease Control guidelines. Amongst those, employment rates and the urban/rural demographic of the voting population, will be considered.

__Question to answer__: Is there a significant correlation between political affiliation and population response to the COVID pandemic, and the confirmed case and death rates? 

__Additional analyses__: 
* Did this trend continue during the more recent rise of the Delta variant? 
* Are there other factors that could have affected this correlation? 
* Two prominent ones often mentioned with the political divide are unemployment and the urban/rural demographic.
"""
)


# Party affiliation and Covid case trend
###########################################
st.markdown("""---""")
# original_title = '<p style="font-family:Arial Bold; color:Black; font-size: 36px; font-weight:bold;text-align:center;">Is there an observable correlation between political affiliation</p>'
# st.write(
#     original_title, unsafe_allow_html=True,
# )
# original_title = '<p style="font-family:Arial Bold; color:Black; font-size: 36px; font-weight:bold;text-align:center"> and population response to the COVID pandemic</p>'
# st.write(
#     original_title, unsafe_allow_html=True,
# )


st.header(
    "Is there an observable correlation between political affiliation  and population response to the COVID pandemic?",
    anchor="main_question_subheader",
)


st.subheader(
    "Party affiliation and Covid case trend in Presidential election year of 2020",
    anchor="partyandcovid",
)

st.markdown(
    """
The basis of this project began with the observations derived from the visualization below. 
The **task** is to determine if a there is significant difference in the rate of rise of Covid cases between 
normalized (per 100K) populations that professes affiliation to one party or another (Republican, Democrat and Other). 
The **data** to be analyzed was the county level Covid confirmed cases, joined with Presidential election data 
from 2016 and 2020.
We differentiate between populations that voted Republican, Democrat or Other. The affiliation was further sectioned 
into those that stayed loyal to a party from 2016 to 2020, in contrast to those that were perhaps more influenced 
by the political messaging and switched loyalties. The number of cases plotted along the y-axis is the seven day 
rolling average rather than **raw numbers** which can reflect data collection and delay errors.

From the visualization we observed that the rate of rise of the infection was markedly higher, towards the end of 
the first year of the pandemic, in the populations that voted Republican (remained loyal in 2020 or switched from 2016).  
"""
)

# Get rolling average of cases by segment
case_rolling_df = pd.read_csv("./data/case_rolling_df.csv")
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
    """Does strength of affiliation, as determined by the percentile point change in votes received by a party in 2020 
    over 2016, show any correlation to the number of Covid related deaths in that county? 
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
# )

election_change_and_covid_death_df = pd.read_csv(
    "./data/percentile_point_deaths.csv",
    dtype={
        "COUNTYFP": "int",
        "deaths_avg_per_100k": "float",
        "state": "str",
        "state_po": "str",
        "CTYNAME": "str",
        "party_winner_2020": "str",
        "total_votes_2020": "float",
        "fractionalvotes_2020": "float",
        "party_winner_2016": "str",
        "total_votes_2016": "float",
        "fractionalvotes_2016": "float",
        "changecolor": "str",
        "_merge": "str",
        "pct_increase": "float",
        "segementname": "str",
    },
)
st.altair_chart(
    createPercentPointChangeAvgDeathsChart(
        election_change_and_covid_death_df
    ).configure_title(align="left", anchor="start")
)


st.write(election_change_and_covid_death_df)
# df = election_change_and_covid_death_df.copy()
# df["deaths_avg_per_100k"] = df["deaths_avg_per_100k"].astype("float")
# df["pct_increase"] = df["pct_increase"].astype("float")
col1, col2, col3, col4 = st.columns(4)
# formatted_string = "{:.2f}".format(
#     election_change_and_covid_death_df["deaths_avg_per_100k"].mean()
# )
# st.write(f"All counties Average Deaths = {formatted_string}")

# for segmentname in [
#     "Stayed Democrat",
#     "Stayed Republican",
# ]:
#     num = len(
#         df[
#             (df["deaths_avg_per_100k"] >= 1.25)
#             & (df["pct_increase"] >= 0)
#             & (df["segmentname"] == segmentname)
#         ]
#     )
#     denom = len(
#         df[
#             (df["segmentname"].str.contains(segmentname.replace("To ", "")))
#             | (df["segmentname"].str.contains(segmentname.replace("Stayed ", "")))
#         ]
#     )
#     formatted_string = "{:.4f}".format(num / denom)

#     if segmentname == "Stayed Democrat":
#         col1.write(f"Fraction of counties in fourth quadrant(per party): ")
#         col2.write(f"{segmentname} = {formatted_string}")
#     else:
#         col3.write(f"{segmentname} = {formatted_string}")


st.markdown("""---""")


# Affiliation and Vaccine Adoption Rates By State
###########################################
st.subheader("Affiliation and Vaccine Adoption Rates By State")
st.markdown(
    """To allow the user to wield the power to pause and view the rate at which states in the U.S. adopted the Covid 
vaccines after it became available, the below visual offers a slider bar with a duration from first shot as range. 
As Cassie Kozyrkov writes [here](https://towardsdatascience.com/analytics-is-not-storytelling-a1fe61b1ab6c), "As an analyst, I’m not here to funnel you towards my opinion. I’m here to help you form your own."
In employing interaction in the below visual (originally seen in static form at this [NPR site](https://www.npr.org/2021/06/09/1004430257/theres-a-stark-red-blue-divide-when-it-comes-to-states-vaccination-rates),
we notice clearly that "blue" states surged forward in vaccinations earlier than the red states after about three 
months after its release. 
The size of the bubbles in the chart below is scaled by population of each state.
The Y-axis positions each state by the percent of its population with at least one shot (since some vaccines require 
only one shot).
"""
)

st.markdown("""---""")

daily_vaccination_percent_df = pd.read_csv("./data/daily_vaccination_percent_df.csv")

daily_vaccination_percent_df["Total population"] = daily_vaccination_percent_df[
    "Total population"
].astype("int")
daily_vaccination_percent_df["day_num"] = daily_vaccination_percent_df[
    "day_num"
].astype("int")
daily_vaccination_percent_df["Percent with one dose"] = daily_vaccination_percent_df[
    "Percent with one dose"
].astype("float")

st.altair_chart(createDailyInteractiveVaccinationChart(daily_vaccination_percent_df))

st.markdown("""---""")


# Vaccinations and the Delta Variant Case Resurgence
###########################################
st.subheader("Vaccinations and the Delta Variant Case Resurgence")
st.markdown(
    """The chart below allows for selection of a state in the map to learn about case trend
for the period after the first Delta variant was detected in the US.The US average and per party averages are also 
plotted for baseline comparison.

Efficacy of the vaccine over time, for this pandemic, can only be measured as time progresses, since we do not have a 
precedent. Mutation of the virus is inevitable and immunity response is constantly being monitored.
The below visualization presents the resurgence in Covid cases that are observed to be rising especially in states with 
low adoption. We compare an individual state's trend with mean trends pertaining to the US, combined mean of states that 
voted Republican and states that voted Democrat. It was noted that the resurgent rising trends were notably seen in 
states such as Louisiana, Missouri, and Florida where the numbers rose well above all the means. These are "red" states. 
Vermont has a high vaccination adoption and a notably lower trend. Most of the states that voted Democrat also have 
trends that initially spiked and later settled closer to their mean.
"""
)

state_vaccine_df = pd.read_csv("./data/state_vaccine_df.csv")
us_case_rolling_df = pd.read_csv("./data/us_case_rolling_df.csv")
state_case_rolling_df = pd.read_csv("./data/state_case_rolling_df.csv")
state_election_df = pd.read_csv("./data/state_election_df.csv")

state_vaccine_df["STATEFP"] = state_vaccine_df["STATEFP"].astype("int")
state_case_rolling_df["cases_avg_per_100k"] = state_case_rolling_df[
    "cases_avg_per_100k"
].astype("float")
state_case_rolling_df["STATEFP"] = state_case_rolling_df["STATEFP"].astype("int")

state_election_df["state_fips"] = state_election_df["state_fips"].astype("int")
state_election_df["candidatevotes"] = state_election_df["candidatevotes"].astype("int")
state_election_df["totalvotes"] = state_election_df["totalvotes"].astype("int")
state_election_df["fractionalvotes"] = state_election_df["fractionalvotes"].astype(
    "float"
)


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
    )  # .properties(width=200, height=100)
)

st.markdown("""---""")

# Mask Usage by political affiliation
###########################################
st.subheader("Frequent and Infrequent Mask Usage by Political affiliation")
st.markdown(
    """Mask usage data was collected in a survey by New York Times (through a professional survey firm). The data was 
    gathered from 250,000 people surveyed in a two week period in July 2020 (please see details in Addendum). 
    The five choices offered: Never, Rarely, Sometimes, Frequently Always. The estimations of all five for every county, 
    provided as a float adds up to 1.
This was binned into Not Frequent (Never, Rarely, Sometimes) and Infrequent (Frequently, Always) usage which 
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
mask usage chart. In the heartland, a lukewam acceptance to the guidelines is observed - select Democrat/Republican 
Low mask usage in Infrequent mask usage chart. 
"""
)

mask_distribution_df = pd.read_csv("./data/mask_distribution_df.csv")
# st.markdown("""---""")
st.altair_chart(createMaskUsageDistributionChart(mask_distribution_df))
# st.markdown("""---""")
county_pop_mask_df = pd.read_csv("./data/county_pop_mask_df.csv")
county_pop_mask_freq_df = pd.read_csv("./data/county_pop_mask_freq_df.csv")
county_pop_mask_infreq_df = pd.read_csv("./data/county_pop_mask_infreq_df.csv")

st.write(county_pop_mask_df)
st.write(county_pop_mask_freq_df)
st.write(county_pop_mask_infreq_df)


# freq, infreq, excol1 = st.columns(3)

# (
#     county_mask_chart,
#     legend_republican,
#     legend_democrat,
#     average_mask_chart,
# ) = createFreqCountyMaskUsageWithRanges(
#     "FREQUENT",
#     county_pop_mask_df,
#     county_pop_mask_freq_df,
#     county_pop_mask_infreq_df,
#     mask_distribution_df,
# )
# freq.altair_chart(
#     (
#         (county_mask_chart)
#         & (average_mask_chart | legend_republican | legend_democrat).resolve_scale(
#             color="independent"
#         )
#     ).configure_title(align="left", anchor="start")
# )

# (
#     county_mask_chart,
#     legend_republican,
#     legend_democrat,
#     average_mask_chart,
# ) = createFreqCountyMaskUsageWithRanges(
#     "INFREQUENT",
#     county_pop_mask_df,
#     county_pop_mask_freq_df,
#     county_pop_mask_infreq_df,
#     mask_distribution_df,
# )

# infreq.altair_chart(
#     (
#         (county_mask_chart)
#         & (average_mask_chart | legend_republican | legend_democrat).resolve_scale(
#             color="independent"
#         )
#     ).configure_title(align="left", anchor="start")
# )

st.markdown("""---""")

