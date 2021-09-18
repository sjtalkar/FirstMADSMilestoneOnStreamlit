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
)

DataFolder = Path("./data/")

# Set streamlit page to wide format
st.set_page_config(layout="wide")

# Show the header image
@st.cache(allow_output_mutation=True)
def load_bkgd_image():
    bkgd_image = Image.open("./images/title-background.jpg")
    return bkgd_image

bkgd_image = load_bkgd_image()

st.image(bkgd_image, use_column_width=True)


# Introduction
###########################################
st.markdown(
    """
The Nigerian Igbo word “igwebuike”, which means “there is strength in community.” paraphrases the ideal response 
to the COVID pandemic. To build herd immunity and stop its spread, within and outside borders, a cohesive and 
co-operative front is called for. However, amidst this pandemic, there is a suggestion that the U.S. has never 
been as divided as in recent years.

In a year of presidential elections, the leadership rhetoric and messaging regarding COVID response and behavior, 
as projected by the media, appears to starkly differ along political ideological lines, specifically, Democrat versus 
Republican. Usage of masks, openness to vaccination and a general appreciation of the severity of the pandemic, as 
portrayed to the public, arouses curiosity as to whether the response is truly divided along party lines.

We will also explore if other factors, commonly associated with political affiliation, differentiate the response 
by communities towards US Centers for Disease Control guidelines. Amongst those, employment rates and the urban/rural 
demographic of the voting population, will be considered.

__Question to answer__: Is there a significant correlation between political affiliation and population response to 
the COVID pandemic, and the confirmed case and death rates? 

__Additional analyses__: 
* Did this trend continue during the more recent rise of the Delta variant? 
* Are there other factors that could have affected this correlation? 
* Two prominent ones often mentioned with the political divide are unemployment and the urban/rural demographic.
"""
)


# Party affiliation and COVID case trend
###########################################
st.markdown("""---""")
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
@st.cache
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
# )
@st.cache
def load_percentile_point_deaths():
    df = pd.read_csv("./data/percentile_point_deaths.csv")
    return df

election_change_and_covid_death_df = pd.read_csv("./data/percentile_point_deaths.csv")
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

daily_vaccination_percent_df = pd.read_csv("./data/daily_vaccination_percent_df.csv")
daily_vaccination_percent_df["Total population"] = daily_vaccination_percent_df["Total population"].astype("int")
daily_vaccination_percent_df["day_num"] = daily_vaccination_percent_df["day_num"].astype("int")
daily_vaccination_percent_df["Percent with one dose"] = daily_vaccination_percent_df["Percent with one dose"].astype("float")

st.altair_chart(createDailyInteractiveVaccinationChart(daily_vaccination_percent_df))

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

@st.cache
def load_state_vaccine_df():
    df = pd.read_csv("./data/state_vaccine_df.csv")
    df["STATEFP"] = df["STATEFP"].astype("int")
    return df

@st.cache
def load_us_case_rolling_df():
    df = pd.read_csv("./data/us_case_rolling_df.csv")
    return df

@st.cache
def load_state_case_rolling_df():
    df = pd.read_csv("./data/state_case_rolling_df.csv")
    df["cases_avg_per_100k"] = df["cases_avg_per_100k"].astype("float")
    df["STATEFP"] = df["STATEFP"].astype("int")
    return df

@st.cache
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
st.markdown("""
Mask usage data was collected in a survey by New York Times (through a professional survey firm). The data was 
gathered from 250,000 people surveyed in a two week period in July 2020 (please see details in Appendix). 
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
mask usage chart. In the heartland, a lukewarm acceptance to the guidelines is observed - select Democrat/Republican 
Low mask usage in Infrequent mask usage chart. 
""")

@st.cache
def load_mask_distribution_df():
    df = pd.read_csv("./data/mask_distribution_df.csv")
    return df

@st.cache
def load_county_pop_mask_df():
    df = pd.read_csv("./data/county_pop_mask_df.csv")
    return df

@st.cache
def load_county_pop_mask_freq_df():
    df = pd.read_csv("./data/county_pop_mask_freq_df.csv")
    return df

@st.cache
def load_county_pop_mask_infreq_df():
    df = pd.read_csv("./data/county_pop_mask_infreq_df.csv")
    return df

mask_distribution_df = load_mask_distribution_df()
st.altair_chart(createMaskUsageDistributionChart(mask_distribution_df))

county_pop_mask_df = load_county_pop_mask_df()
county_pop_mask_freq_df = load_county_pop_mask_freq_df()
county_pop_mask_infreq_df = load_county_pop_mask_infreq_df()

freq, infreq = st.beta_columns(2)
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
freq.altair_chart(
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

infreq.altair_chart(
    (
        (county_mask_chart)
        & (average_mask_chart | legend_republican | legend_democrat).resolve_scale(
            color="independent"
        )
    ).configure_title(align="left", anchor="start")
)
st.markdown("""---""")

# Unemployment rate and COVID
###########################################
@st.cache
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


@st.cache
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


@st.cache
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


@st.cache
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


@st.cache
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


@st.cache
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


@st.cache
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


urban_rural_election_df = load_urban_rural_election_df()

urban_rural_rolling_avg_full_df = load_urban_rural_rolling_avg_full_df()
urban_rolling_avg_full_df = load_urban_rolling_avg_full_df()
rural_rolling_avg_full_df = load_rural_rolling_avg_full_df()

urban_rural_avgdeaths_full_df = load_urban_rural_avgdeaths_full_df()
urban_avgdeaths_full_df = load_urban_avgdeaths_full_df()
rural_avgdeaths_full_df = load_rural_avgdeaths_full_df()

st.header(
    "Does the Urban/Rural Demographic Influence the COVID Effects?",
    anchor="urbanruralandcovid",
)

st.markdown("""
Among the socioeconomic factors frequently and strongly associated with political affiliation is the urban/rural 
demographic of the voting population. Could this factor influence the pattern we have seen above, of the COVID-19 
effects being split along party lines?

The Census Bureau defines urban areas by population size, specifically 2,500 or greater. Also from the Census Bureau, 
we obtained a list of US counties with a ‘percent rural’ designation, meaning the percentage of county population 
living in rural areas.
""")

st.subheader("Political affiliation")

st.markdown("""
Since we want to see the effect of political affiliation on the COVID response, the next question is: How strongly 
democrat or republican were those counties? For that, we used the ratio of winning party votes to total votes, which 
we call the ‘vote fraction’. Plotting against the Percent Rural designation of each county, we find no correlation 
(-0.07) for counties won by the democratic candidate, and a weak positive correlation (0.25) for counties won by the 
republican candidate.
""")

st.altair_chart(ElectionUrbanRuralDensityPlot(urban_rural_election_df))

st.markdown("""
Merging that with the presidential election county results, we see there seems to be a clear divide in political 
affiliation between rural areas and urban centers. Counties less than about 32% rural were more likely to vote democrat,
 while those above were more likely to vote republican.

The merge was done on the county FIPS code, and about 40 counties were lost in the merge due to mismatches. Out of 
more than 3000 counties, this was considered an acceptable loss.
""")

st.altair_chart(UrbanRuralCorrelation(urban_rural_election_df))

st.markdown("""
This is a positive initial result, since it implies that the urban/rural nature of a county has little to no effect 
on the strength of the affiliation.
""")

st.subheader("COVID effects")

st.markdown("""
Finally, we come to the main question, which is whether the urban/rural nature has an effect on the effects of the 
COVID pandemic, indicated by the rolling case average and the deaths.

The Census Bureau classifies counties with 50% or more of their population living in rural areas as ‘mostly rural’, 
while the remainder are classified as ‘mostly urban’. We split the counties by that designation, and for each, we repeat 
the analyses performed above.
""")


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

st.markdown("""
For COVID rolling case average, we find that the same trends hold as those found earlier for all counties: Initially, 
the case numbers are higher for counties that voted democrat, but in September 2020, the rise in case numbers for 
counties that voted republican is steeper.

As for COVID deaths, once again, we find the same trends hold for both urban and rural counties as those found earlier 
for the complete set of counties: The number of deaths per 100K population is higher for more counties that are 
strongly republican.

So in conclusion, we can say that the urban or rural nature of a county does not have an effect on the effects of the 
COVID pandemic as represented by the rolling case average and the death rate.
""")

st.markdown("""---""")

# Unemployment rate and COVID
###########################################
@st.cache
def load_unemployment_rate_since_2019_df():
    df = pd.read_csv(
        "./data/unemployment_rate_since_2019_df.csv",
        dtype={
            "month": str,
            "unemployment_rate": float,
            "COUNTYFP": int,
            "month_since_start": int,
            "party": str,
        },
    )
    return df


@st.cache
def load_unemployment_covid_correlation_df():
    df = pd.read_csv(
        "./data/unemployment_covid_correlation_df.csv",
        dtype={"month": str, "party": str, "variable": str, "value": float},
    )
    return df


@st.cache
def load_unemployment_and_mask_df():
    dtypes = {
        "COUNTYFP": int,
        "unemployment_rate": float,
        "cases_avg_per_100k": float,
        "deaths_avg_per_100k": float,
        "party": str,
        "NEVER": float,
        "RARELY": float,
        "SOMETIMES": float,
        "FREQUENTLY": float,
        "ALWAYS": float,
    }
    freq_df = pd.read_csv("./data/unemployment_freq_mask_july_df.csv", dtype=dtypes,)
    infreq_df = pd.read_csv(
        "./data/unemployment_infreq_mask_july_df.csv", dtype=dtypes,
    )
    return freq_df, infreq_df


@st.cache
def load_unemployment_vaccine_correlation_df():
    df = pd.read_csv(
        "./data/unemployment_vaccine_correlation_df.csv",
        dtype={"month": str, "party": str, "variable": str, "value": float},
    )
    return df


unemployment_rate_since_2019_df = load_unemployment_rate_since_2019_df()
unemployment_covid_correlation_df = load_unemployment_covid_correlation_df()
(
    unemployment_freq_mask_july_df,
    unemployment_infreq_mask_july_df,
) = load_unemployment_and_mask_df()
unemployment_vaccine_correlation_df = load_unemployment_vaccine_correlation_df()


st.header(
    "Does Unemployment Influence the COVID Response?",
    anchor="unemploymentandcovid",
)
st.markdown(
    """
Stark unemployment increase was a major side effect of the COVID pandemic. In December 2019 (Elapsed month = 1 in the 
visualization below) the mean of the unemployment rate was 3.79% with an inter-quartile range (the range between 
the 25th and 75th percentile of 2.7% to 4.4%. By April 2020 (Elapsed month = 4), 
unemployment rate had jumped to a mean of 12.38% with an inter-quartile range 8.7% of 15.5%.

Both the numbers and the visualization clearly show an increase in unemployment rate but also an in the disparities 
between counties as the inter-quartile distance (visualized as the width of the distribution) increased from a 
narrow 1.7 points to 6.8 points.
"""
)

st.altair_chart(createUnemploymentChart(unemployment_rate_since_2019_df))

st.markdown(
    """
Could unemployment rate have a bigger impact than political affiliation on the response to the COVID, by 
pushing more people to wear masks or get vaccinated?
"""
)

st.markdown("""---""")


st.markdown(
    """
When we look at the *Republican* and *Democrat* counties' monthly average unemployment rate and COVID cases 
(per 100k people)  since the beginning of the pandemic, we see clearly that they both follow very 
different trends. The correlation between unemployment rate and COVID cases also oscillates erratically between 
low values (-0.4 and 0.4). This suggests that there is no correlation between unemployment rate and COVID cases.

What we see however is that the average unemployment rate is constantly higher in *Democrat* counties than in 
*Republican* counties, while at the peak of the pandemic the average COVID cases number was higher in 
*Republican* counties.
"""
)

st.altair_chart(
    createUnemploymentCorrelationLineChart(
        unemployment_covid_correlation_df,
        title="Counties Average Unemployment Rate and COVID Cases Since January 2020",
        sort=[
            "Average COVID Cases per 100k",
            "Average Unemployment Rate",
            "Correlation",
        ],
    )
)

st.markdown(
    """
If there is no correlation between unemployment rate and COVID cases, could there still be one with the COVID 
response like mask usage and vaccination?

Looking at July 2020 data, a slightly positive correlation (0.348) between unemployment rate and *frequent* 
mask-wearing habits, and a slightly negative correlation (-0.348) between unemployment rate and *not frequent* 
mask-wearing habits doesn't really help to validate or reject the hypothesis of a correlation between them.

However, more than a clear correlation, there appears to be a more clear divide along political affiliation.
* Most counties with high unemployment and high mask usage are Democrat,
* while most counties with low mask usage and low unemployment are Republican.

It seems that political affiliation is a stronger differentiator in following CDC mask-wearing guidelines than 
unemployment rate.
"""
)

st.altair_chart(
    createUnemploymentMaskChart(
        unemployment_freq_mask_july_df, unemployment_infreq_mask_july_df
    )
)

st.markdown(
    """
When we look at vaccination, the above pattern seems even more clear. The correlation between the percentage of the 
population with at least 1 dose of vaccination and the unemployment rate is even less clear. However, as for 
mask-wearing behaviors, we also see that 
* the counties with high vaccination and high unemployment rates are mainly Democrat
* the counties with low vaccination and low unemployment rates are mainly Republican

As for mask-wearing, the political affiliation seems to be a stronger differentiator in following CDC vaccination 
guidelines than unemployment rate.
"""
)

st.altair_chart(
    createUnemploymentCorrelationLineChart(
        unemployment_vaccine_correlation_df,
        title="Counties Average Unemployment Rate and Vaccination Rate Since December 2020",
        sort=[
            "Average Unemployment Rate",
            "Average % of People with 1 Dose of Vaccine",
            "Correlation",
        ],
    )
)


st.markdown("""
As we wanted to verify if unemployment rate could have a stronger impact on the COVID response than political 
affiliation, we see that 
* there is no correlation between COVID case and unemployment rate, and between unemployment rate and COVID 
response behaviors like wearing a mask or getting vaccinated 
* On average, Democrat counties have higher unemployment rate, less COVID cases but better follow COVID response 
CDC guidelines while Republican counties show opposite trends and behaviors
""")

st.markdown("""---""")

# Conclusion
###########################################
st.header("Conclusion",
    anchor="conclusion")

st.markdown(
    """
Preliminary EDA clearly indicated a distinct difference in rates of infection along party lines at the county levels. 
Towards the beginning of July of 2021, we show evidence of cases rising steeply in states with low vaccination rates. 
These states that predominantly voted Republican (such as Louisiana and Mississippi), are clustered in the Southern 
parts of the United States and can visually be spotted as states with low vaccination rates. The short-term NYT mask 
adherence survey data also showed marginally higher adherence rates among counties that voted Democrat. We also noted 
that socio-economic factors such as unemployment and urban or rural demographics only served to further highlight the 
split in response, and ultimately the effects of COVID,  along political lines.  
""")

st.markdown("""---""")

# Expansion of the projects
###########################################
st.header("Annex",
            anchor="annex")

st.subheader("Datasets",
             anchor="datasets")

st.markdown(
    "All datasets are publicly available following the information provided below."
)

st.write(
    "<bold>Note</bold>:<small> Census data obtained through API requires registration [here](https://api.census.gov/data/key_signup.html)</small>",
    unsafe_allow_html=True,
)
st.write(
    "<bold>Note</bold>:<small> Bureau of Labor Statistics website only gives access to the last 14 months of data. To capture the unemployment rate for the desired period, we used the BLS v2 public APIs. Registration is required [here](https://data.bls.gov/registrationEngine/). The LAUS codes of all counties must be passed to the API.</small>",
    unsafe_allow_html=True,
)

st.markdown(
    """
||<font size="2"> Name </font>|<font size="2"> Description </font>|<font size="2"> Key Variables</font> |<font size="2"> Size </font>|<font size="2"> Shape </font>|<font size="2"> Format </font>|<font size="2"> Access </font>|
|---|---|---|---|---|---|---|---|
|<font size="2"> 1 </font>|<font size="2">State presidential election results dataset </font>|<font size="2"> *"This data file contains constituency (state-level) returns for elections to the U.S. presidency from 1976 to 2020"* </font>|<font size="2"> `year, candidatevotes, totalvotes` </font>|<font size="2"> 500KB </font>|<font size="2"> 4287 x 15 </font>|<font size="2"> CSV </font>|<font size="2"> [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX) </font>|
|<font size="2"> 2 </font>|<font size="2">County presidential election results dataset </font>|<font size="2"> *"This dataset contains county-level returns for presidential elections from 2000 to 2020"* </font>|<font size="2"> `year, county_fips, county_name, party` </font>|<font size="2"> 7.4MB </font>|<font size="2"> 72603 x 12 </font>|<font size="2"> CSV </font>|<font size="2"> [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ) </font>|
|<font size="2"> 3 </font>|<font size="2">COVID-19 cases and death rolling averages</font>|<font size="2">This dataset issued by the New York Times *"contains the daily number of new cases and deaths, the seven-day rolling average and the seven-day rolling average per 100,000 residents"* for all counties in the U.S. </font>|<font size="2"> `date, geoid, county, state, cases_avg_per_100k, deaths_avg_per_100k` </font>|<font size="2"> >85MB </font>|<font size="2"> >146M x 10 </font>|<font size="2"> CSV </font>|<font size="2"> [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/rolling-averages)</font>|
|<font size="2"> 4 </font>|<font size="2">State level total COVID-19 vaccine dataset </font>|<font size="2"> This dataset issued by the US Centers for Disease Control and Prevention (CDC) contains the total COVID-19 Vaccine deliveries and administration data at the state level.</font>|<font size="2"> `State/Territory/Federal Entity, People with at least One Dose by State of Residence, Percent of Total Pop with at least One Dose by State of Residence` </font>|<font size="2"> 28KB </font>|<font size="2"> 63 x 62 </font>|<font size="2"> CSV </font>|<font size="2"> [The U.S. Centers for Disease Control website](https://covid.cdc.gov/covid-data-tracker/#vaccinations) </font>|
|<font size="2"> 5 </font>|<font size="2">County level daily COVID-19 vaccine dataset </font>|<font size="2"> This dataset issued by the US Centers for Disease Control and Prevention (CDC) contains the daily COVID-19 Vaccine deliveries and administration data at the county level. </font>|<font size="2"> `Date, FIPS, Recip_County, Recip_State, Administered_Dose1_Pop_Pct` </font>|<font size="2"> 139MB </font>|<font size="2"> >840,000 x 27 </font>|<font size="2"> CSV </font>|<font size="2"> [The U.S. Centers for Disease Control website](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh) </font>|
|<font size="2"> 6 </font>|<font size="2">Mask-wearing survey dataset </font>|<font size="2"> This dataset is an estimate of mask usage by county in the United States released by The New York Times. It “comes from a large number of interviews conducted online“ in 2020 between July 2nd and July 14th. </font>|<font size="2"> `COUNTYFP, NEVER, RARELY, SOMETIMES, FREQUENTLY, ALWAYS` </font>|<font size="2"> 109KB </font>|<font size="2"> 3143 x 6 </font>|<font size="2"> CSV </font>|<font size="2"> [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/mask-use) </font>|
|<font size="2"> 7 </font>|<font size="2">Census Bureau population census and estimates dataset </font>|<font size="2"> This dataset contains the 2010 population census data per county and the 2011~2020 population estimates. We are mainly interested in the 2020 estimates </font>|<font size="2"> `SUMLEV, STATE, STNAME, CTYNAME, POPESTIMATE2020` </font>|<font size="2"> 3.7MB </font>|<font size="2"> 3195 x 180 </font>|<font size="2"> CSV </font>|<font size="2"> [U.S. Census Bureau website](https://www.census.gov/programs-surveys/popest/technical-documentation/research/evaluation-estimates/2020-evaluation-estimates/2010s-counties-total.html) </font>|
|<font size="2"> 8 </font>|<font size="2">Unemployment rate dataset </font>|<font size="2"> The dataset is the collection of labor force county data tables for 2020 issued by the U.S. Bureau of Labor Statistics </font>|<font size="2"> `state_FIPS, county_FIPS, year, month , unemployment_rate` </font>|<font size="2"> 7.69MB </font>|<font size="2"> >96,000 x 7 </font>|<font size="2"> CSV </font>|<font size="2"> [Bureau of Labor Statistics website](https://www.bls.gov/web/metro/laucntycur14.zip) only gives access to the last 14 months of data. To capture the unemployment rate for the desired period, we used the BLS v2 public APIs. Registration is required [here](https://data.bls.gov/registrationEngine/). The LAUS codes of all counties must be passed to the API.</font>|
|<font size="2"> 9 </font>|<font size="2">Census Urban and Rural dataset </font>|<font size="2"> The dataset classifies all the counties in the U.S. as rural or urban areas </font>|<font size="2">`2015 GEOID, State, 2015 Geography Name, 2010 Census Percent Rural`</font>|<font size="2"> 302KB </font>|<font size="2"> 3142 x 8 </font>|<font size="2"> XLS </font>|<font size="2"> [U.S. Census Bureau website](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html) </font>|
""",
    unsafe_allow_html=True,
)

st.subheader("Merging everything using FIPS codes",
             anchor="mergingdatasets")

st.markdown("""
The datasets were joined using FIPS codes. FIPS stands for Federal Information Processing Standards, which are 
published by the National Institute of Standards and Technology (NIST) that every tract, county and state in the US 
is assigned. The code had to be extracted from a combined Geo code or had to be formed by concatenation if state and 
counties were separately coded and served as the primary key to merge the datasets.

For each visualization, the county/state level election data was combined with a feature of interest, such as 
vaccination rate, COVID cases, unemployment, urban.rural demographics. Below is an example on the data transformation 
flow used to generate the data for the first figure on the unemployment rate effect on the COVID response "Counties 
Average Unemployment Rate and Vaccination Rate Since January 2021".
""")

@st.cache(allow_output_mutation=True)
def load_data_workflow_image():
    data_image = Image.open("./images/data-workflow.jpg")
    return data_image

data_workflow_image = load_data_workflow_image()

st.image(data_workflow_image, width=600)

st.markdown("""
Thanks to the clean nature of these already curated datasets coming from reliable sources and the FIPS codes, there 
was no major challenge of missing or incorrect data. The main challenges we faced were:
* _FIPS codes_: Alaska for has 29 counties + 1 unorganized borough. However for the elections, unlike in other states, 
the results are reported by election districts and not by counties. And election districts have their own geographical 
boundaries and FIPS code which do not match counties (except for 3 counties). It is as such very hard to define the 
political affiliation of a county in Alaska and such counties were dropped. Out of a total of more than 3,000 counties, 
we considered this acceptable.
* _Vaccination_: States such as Texas and Hawaii only record vaccinations administered at the state level, in contrast 
to other states which report it at the county level. For visualizations at the county level, these states 
have been ignored.
""")

# Expansion of the projects
###########################################
st.subheader("Expansion of project",
             anchor="projectexpansion"
             )

st.markdown("""
> -  We are keenly following the change in tone in rhetoric from the Republican party as cases are steeply 
rising in the Southern states which lean "red" in Presidential elections. While several Republican officials 
continue to question restrictions imposed to stem the spread of the Delta variant,
several others are now urging mask wearing and social distancing, with some having contracted the virus despite 
being vaccinated.
> -  It would be interesting to pick the perceived change in tone in the time period between August 2020 (close to 
Presidential elections) and now (with resurgence in cases). We plan to collect tweets from the then President and 
incumbent and the current president regarding the pandemic.
 In addition to this we will pull in tweets from all the Governors of every state, since they set the policy for 
 each state . We can also expand the scope to top officials in both parties but the challenge will be to avoid 
 selection bias. 
> -  The above will involve NLP applied on Twitter data and data scraped from the web and comments made to the press.
> -   We can move away from US shores and look into impact of policies towards COVID containment in various countries 
and predict what will succeed with the resurgence of cases. We will also dig into patterns of response in various 
countries to see if we can find clusters or groups with similar reponses. If we do find clusters, we can look into 
the similarity of what factors drives countries to respond in a certain way of the behavior differs (in terms of 
lockdown, travel restrictions, social distancing and mask wearing) from WHO recommendations.
""")

# Addendum : Additional Information, citations and disclaimers
###########################################
st.subheader("Appendix : Additional Information, citations and disclaimers",
             anchor="appendix")

st.markdown(
    """
**1- API Calls for vaccination data**
[Source: CDC ](https://www.cdc.gov/coronavirus/2019-ncov/vaccines/distributing/reporting-counties.html)

Most API require an API access key. After creating a Socrata account, I is possible to apply for a CDC API access ke 
[here](https://data.cdc.gov/signed_out?return_to=%2Fprofile%2Fedit%2Fdeveloper_settings).

For each dataset, the CDC website also provides a URL to which this API taken can be applied. The URL request get the 
response in JSON, CSV and other formats. I chose the CSV format. Other than the token you can concatenate 
parameters of your GET request to the URL string.
In our case, the data was requested in batches of 500,000 rows (all columns - although these can be 
specifically requested). 

One more note about the APIToken. Since this is a personal secret access key, the token was stored in a **pickle** file 
(string format serialized) and then retrieved from it for the concatenation. 

The **requests** module of Python is used to submit this token and parameter enhanced URL. Since we are only interested 
in reading the data, we issue a **GET** command. 

The response **text** is converted to csv using the StringIO to convert it to String and then using pandas read_csv call 
which saves the data along with the headers into a dataframe.

The data for the vacinations are updated on a daily basis by the CDC. Using the API enables us to update the 
visualization as and when the data gets updated. (We are storing it into a CSV file so that we do not send too many 
calls to the API endpoint as we develop).
"""
)

st.markdown(
    """
__2- Data at County Level Issues__

* Alaska has 29 counties + 1 unorganized borough. However for the elections, unlike in other states, the results are 
reported by election districts and not by counties. And election districts have their own geographical boundaries 
and FIPS code, which do not match counties FIPS codes (except for 3 counties). It is as such very hard to define the 
political affiliation of a county in Alaska.
* California does not report the county of residence for persons receiving a vaccine when the resident’s county 
has a population of fewer than 20,000 people. (CDC)
* Hawaii does not provide CDC with county-of-residence information. (CDC)
* Texas provides data that are aggregated at the state level and cannot be stratified by county. 
* For several counties in Colorado the percent of population is marked as 0 - this appears to be a reporting and 
recording issue to me but I am not sure how a large number of counties in Colorado have no vaccination counts at all.

__Such counties have been ignored from the county level analysis__. Out of a total of more than 3,000 counties, we 
considered this acceptable.
"""
)


st.markdown(
    """
__3- The New Your Times mask wearing survey__
The New York Times is releasing estimates of mask usage by county in the United States.

>These data come from a large number of interviews conducted online by the global data and survey firm Dynata at the 
request of The New York Times. The firm asked a question about mask use to obtain 250,000 survey responses between 
July 2 and July 14, enough data to provide estimates more detailed than the state level. (Several states have imposed 
new mask requirements since the completion of these interviews.)
Specifically, each participant was asked: How often do you wear a mask in public when you expect to be within six feet 
of another person?

This survey was conducted a single time, and at this point we have no plans to update the data or conduct the survey 
again. The fields have the following definitions:
"""
)

st.info(
    """
```COUNTYFP: The county FIPS code.
NEVER: The estimated share of people in this county who would say never in response to the question 
 “How often do you wear a mask in public when you expect to be within six feet of another person?”
RARELY: The estimated share of people in this county who would say rarely
SOMETIMES: The estimated share of people in this county who would say sometimes
FREQUENTLY: The estimated share of people in this county who would say frequently
ALWAYS: The estimated share of people in this county who would say always```
"""
)


st.markdown(
    """
What the numbers mean
To transform raw survey responses into county-level estimates, the survey data was weighted by age and gender, and 
survey respondents’ locations were approximated from their ZIP codes. Then estimates of mask-wearing were made for 
each census tract by taking a weighted average of the 200 nearest responses, with closer responses getting more weight 
in the average. These tract-level estimates were then rolled up to the county level according to each tract’s total 
population.

By rolling the estimates up to counties, it reduces a lot of the random noise that is seen at the tract level. In 
addition, the shapes in the map are constructed from census tracts that have been merged together — this helps in 
displaying a detailed map, but is less useful than county-level in analyzing the data.
"""
)

st.info(
    """
__Note about dataset from The New York Times about Rolling Average of COVID cases__

The data in these files is a different version of the data in our main U.S. cases and deaths files.

Instead of cumulative totals, each file contains the daily number of new cases and deaths, the
seven-day rolling average and the seven-day rolling average per 100,000 residents.
                      
__Confirmed Cases__

Confirmed cases are counts of individuals whose coronavirus infections were confirmed by a
laboratory test and reported by a federal, state, territorial or local government agency. Only
tests that detect viral RNA in a sample are considered confirmatory. These are often called
molecular or RT-PCR tests.
      
Another dataset : https://dataverse.harvard.edu/file.xhtml?fileId=4593425&version=54.1
      
Since the first reported coronavirus case in Washington State on Jan. 21, 2020, The Times has
tracked cases of coronavirus in real time as they were identified after testing. Because of the
widespread shortage of testing, however, the data is necessarily limited in the picture it presents
of the outbreak.
  
This data is for cumulative cases
    
We can join the NYTime latest data with population data from census for 2020
df = pd.read_csv('https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv')
"""
)

st.markdown("""---""")

st.markdown(
    """
__News article sources for motivation__:

[An Associated Press analysis](https://fortune.com/2020/11/06/trump-voters-covid-cases-red-counties-2020-election-results) reveals that in 376 counties with the highest number of new cases per capita, the overwhelming majority—93% of those counties—went for Trump, a rate above other less severely hit areas.

Many places Hard Hit By COVID-19 leaned More Toward Trump In 2020 Than 2016 Support for President Trump increased in 2020 in many of the U.S. counties that lost lives at the highest rate to COVID-19, according to an NPR analysis.

Of the 100 counties with the highest COVID-19 death rates per capita, 68 had a higher proportion of votes cast for Trump this cycle than they did in 2016. This includes both Republican-leaning counties and counties that supported Joe Biden. [See the NPR article here](https://www.npr.org/sections/health-shots/2020/11/06/930897912/many-places-hard-hit-by-covid-19-leaned-more-toward-trump-in-2020-than-2016)."""
)
st.markdown("""---""")
