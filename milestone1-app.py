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
    createUnemploymentMaskChart,
)
from Visualization.VizUrbanRural import (
    ElectionUrbanRuralDensityPlot,
    UrbanRuralCorrelation,
)

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


# col1, col2, col3, col4 = st.beta_columns(4)
formatted_string = "{:.2f}".format(
    election_change_and_covid_death_df["deaths_avg_per_100k"].mean()
)
st.write(f"All counties Average Deaths = {formatted_string}")

for segmentname in [
    "Stayed Democrat",
    "Stayed Republican",
]:
    num = len(
        election_change_and_covid_death_df[
            (election_change_and_covid_death_df["deaths_avg_per_100k"] >= 1.25)
            & (election_change_and_covid_death_df["pct_increase"] >= 0)
            & (election_change_and_covid_death_df["segmentname"] == segmentname)
        ]
    )
    denom = len(
        election_change_and_covid_death_df[
            (
                election_change_and_covid_death_df["segmentname"].str.contains(
                    segmentname.replace("To ", "")
                )
            )
            | (
                election_change_and_covid_death_df["segmentname"].str.contains(
                    segmentname.replace("Stayed ", "")
                )
            )
        ]
    )
    formatted_string = "{:.4f}".format(num / denom)

    if segmentname == "Stayed Democrat":
        st.write(f"Fraction of counties in fourth quadrant(per party): ")
        st.write(f"{segmentname} = {formatted_string}")
    else:
        st.write(f"{segmentname} = {formatted_string}")


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

freq, infreq, excol1 = st.beta_columns(3)

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

# Unemployment rate and Covid
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
    "Has unemployment an effect on the Covid-19 response?",
    anchor="unemploymentandcovid",
)
st.markdown(
    """
Stark unemployment increase was a major side effect of the Covid pandemic. In December 2019 (Elapsed month = 1 in the 
visualization) the mean of the unemployment rate was 3.79% and 50% of the counties had an unemployment rate between 
2.7% and 4.4%. By April 2020 (Elapsed month = 4 in the visualization), unemployment rate had jumped to a mean of 
12.38% and 50% of the counties had an unemployment rate between 8.7% and 15.5%.
"""
)

st.altair_chart(createUnemploymentChart(unemployment_rate_since_2019_df))

st.markdown(
    """
Could unemployment rate have a bigger impact than political affiliation on the response to the Covid-19, by 
pushing more people to wear masks or get vaccinated, thus limiting the number of Covid-19 cases?
"""
)

st.markdown("""---""")


st.markdown(
    """
When we look at the *Republican* and *Democrat* counties' monthly average unemployment rate and Covid-19 cases 
(per 100k people)  since the beginning of the pandemic, we see clearly that they both follow very 
different trends. The correlation between unemployment rate and covid cases also oscillates erratically between 
low values (-0.4 and 0.4). This suggests that there is no correlation between unemployment rate and Covid-19 cases.

What we see however is that the average unemployment rate is constantly higher in *Democrat* counties than in 
*Republican* counties, while at the peak of the pandemic the average Covid-19 cases number was higher in 
*Republican* counties.
"""
)

st.altair_chart(
    createUnemploymentCorrelationLineChart(
        unemployment_covid_correlation_df,
        title="Counties Average Unemployment Rate and Covid-19 Cases Since January 2020",
        sort=[
            "Average Covid Cases per 100k",
            "Average Unemployment Rate",
            "Correlation",
        ],
    )
)

st.markdown(
    """
If there is no correlation between unemployment rate and Covid-19 cases, could there still be one with the Covid-19 
response like mask usage and vaccination?

A slightly positive correlation (0.372) between unemployment rate and *frequent* mask-wearing habits, and a slightly 
negative correlation (-0.371) between unemployment rate and *not frequent* mask-wearing habits seem to validate 
this hypothesis. 
* The higher the unemployment rate is, the more people seem to follow mask wearing guidelines.
* The lower the unemployment rate is, the more people seem __not__ to follow mask wearing guidelines.

However, more than a clear correlation, there seem to be a clearer devide along political affiliation.
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
        title="Counties Average Unemployment Rate and Covid-19 Cases Since December 2020",
        sort=[
            "Average Unemployment Rate",
            "Average % of People with 1 Dose of Vaccine",
            "Correlation",
        ],
    )
)


st.markdown(
    """
As we wanted to verify if unemployment rate could have a stronger impact on the Covid-19 response than political 
affiliation, we see that 
* there is no correlation between Covid-19 case and unemployment rate, and between unemployment rate and Covid-19 
response behaviors like wearing a mask or getting vaccinated 
* In average, 
  * *Democrat* counties have higher unemployment rate, less Covid cases but a better response
  * *Republican* counties have lower unemployment rate, more Covid cases but a worse response

An hypothesis - which we haven’t verified - could be that instead of unemployment rate driving a stronger response, 
the effect could be reverse. Counties applying lower restrictions and guidelines see the number of Covid cases 
increase but as businesses are not forced to close due to strict lock down measures, unemployment did not increase 
as much as in other counties with stricter rules.

"""
)

st.markdown("""---""")

# Unemployment rate and Covid
###########################################
@st.cache
def load_unemployment_rate_since_2019_df():
    df = pd.read_csv(
        "./data/election_urban_rural_df.csv",
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


st.markdown("""---""")

# Expansion of the projects
###########################################
st.header("Annex")
st.subheader("Datasets")
st.markdown(
    "All datasets are publicly available following the information provided below."
)

# col1, col2, col3 = st.columns(3)
# dataset_image = Image.open("./images/dataset_image.jpg")
# col1.image(dataset_image, width=350)
# col2.markdown(
#     """
# | <small>Name</small> | <small>Access</small> |
# |---|---|
# | <small>State presidential election results dataset</small> | [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX) |
# | <small>County presidential election results dataset</small> | [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ) |
# | <small>COVID-19 cases and death rolling averages</small> | [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/rolling-averages)|
# | <small>State level total COVID-19 vaccine dataset</small> | [The U.S. Centers for Disease Control website](https://covid.cdc.gov/covid-data-tracker/#vaccinations) |
# | <small>County level daily COVID-19 vaccine dataset</small> | [The U.S. Centers for Disease Control website](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh) |
# | <small>Mask-wearing survey dataset</small> | [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/mask-use) |
# | <small>Census Bureau population census and estimates dataset</small> | [U.S. Census Bureau website](https://www.census.gov/programs-surveys/popest/technical-documentation/research/evaluation-estimates/2020-evaluation-estimates/2010s-counties-total.html) |
# | <small>Unemployment rate dataset</small> | [Bureau of Labor Statistics website](https://www.bls.gov/web/metro/laucntycur14.zip) |
# | <small>Census Urban and Rural dataset</small> | [U.S. Census Bureau website](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html) |
# """,
#     unsafe_allow_html=True,
# )


st.write(
    "<bold>Note</bold>:<small> Census data obtained through API requires registration [here](https://api.census.gov/data/key_signup.html)</small>",
    unsafe_allow_html=True,
)
st.write(
    "<bold>Note</bold>:<small> Bureau of Labor Statistics website only gives access to the last 14 months of data. To capture the unemployment rate for the desired period, we used the BLS v2 public APIs. Registration is required [here](https://data.bls.gov/registrationEngine/). The LAUS codes of all counties must be passed to the API.</small>",
    unsafe_allow_html=True,
)

st.markdown("""---""")


# st.markdown(
#     "All datasets are publicly available following the information provided below."
# )
st.markdown(
    """
<font size="1">    
| Name | Description | Key Variables | Size | Shape | Format | Access |
|---|---|---|---|---|---|---|
| State presidential election results dataset | *"This data file contains constituency (state-level) returns for elections to the U.S. presidency from 1976 to 2020"* | `year, candidatevotes, totalvotes` | 500KB | 4287 x 15 | CSV | [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/42MVDX) |
| County presidential election results dataset | *"This dataset contains county-level returns for presidential elections from 2000 to 2020"* | `year, county_fips, county_name, party` | 7.4MB | 72603 x 12 | CSV | [Harvard Dataverse website](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ) |
| COVID-19 cases and death rolling averages|This dataset issued by the New York Times *"contains the daily number of new cases and deaths, the seven-day rolling average and the seven-day rolling average per 100,000 residents"* for all counties in the U.S. | `date, geoid, county, state, cases_avg_per_100k, deaths_avg_per_100k` | >85MB | >146M x 10 | CSV | [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/rolling-averages)|
| State level total COVID-19 vaccine dataset | This dataset issued by the US Centers for Disease Control and Prevention (CDC) contains the total COVID-19 Vaccine deliveries and administration data at the state level.| `State/Territory/Federal Entity, People with at least One Dose by State of Residence, Percent of Total Pop with at least One Dose by State of Residence` | 28KB | 63 x 62 | CSV | [The U.S. Centers for Disease Control website](https://covid.cdc.gov/covid-data-tracker/#vaccinations) |
| County level daily COVID-19 vaccine dataset | This dataset issued by the US Centers for Disease Control and Prevention (CDC) contains the daily COVID-19 Vaccine deliveries and administration data at the county level. | `Date, FIPS, Recip_County, Recip_State, Administered_Dose1_Pop_Pct` | 139MB | >840,000 x 27 | CSV | [The U.S. Centers for Disease Control website](https://data.cdc.gov/Vaccinations/COVID-19-Vaccinations-in-the-United-States-County/8xkx-amqh) |
| Mask-wearing survey dataset | This dataset is an estimate of mask usage by county in the United States released by The New York Times. It “comes from a large number of interviews conducted online“ in 2020 between July 2nd and July 14th. | `COUNTYFP, NEVER, RARELY, SOMETIMES, FREQUENTLY, ALWAYS` | 109KB | 3143 x 6 | CSV | [The New York Times GitHub page](https://github.com/nytimes/covid-19-data/tree/master/mask-use) |
| Census Bureau population census and estimates dataset | This dataset contains the 2010 population census data per county and the 2011~2020 population estimates. We are mainly interested in the 2020 estimates | `SUMLEV, STATE, STNAME, CTYNAME, POPESTIMATE2020` | 3.7MB | 3195 x 180 | CSV | [U.S. Census Bureau website](https://www.census.gov/programs-surveys/popest/technical-documentation/research/evaluation-estimates/2020-evaluation-estimates/2010s-counties-total.html) |
| Unemployment rate dataset | The dataset is the collection of labor force county data tables for 2020 issued by the U.S. Bureau of Labor Statistics | `state_FIPS, county_FIPS, year, month , unemployment_rate` | 7.69MB | >96,000 x 7 | CSV | [Bureau of Labor Statistics website](https://www.bls.gov/web/metro/laucntycur14.zip) only gives access to the last 14 months of data. To capture the unemployment rate for the desired period, we used the BLS v2 public APIs. Registration is required [here](https://data.bls.gov/registrationEngine/). The LAUS codes of all counties must be passed to the API.|
| Census Urban and Rural dataset | The dataset classifies all the counties in the U.S. as rural or urban areas |`2015 GEOID, State, 2015 Geography Name, 2010 Census Percent Rural`| 302KB | 3142 x 8 | XLS | [U.S. Census Bureau website](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html) |
</font>
""",
    unsafe_allow_html=True,
)


# Expansion of the project
###########################################
st.subheader("Expansion of project ")

st.markdown(
    """> -  We are keenly following the change in tone in rhetoric from the Republican party as cases are steeply rising in the Southern states which lean "red" in Presidential elections. While several Republican officials continue to question restrictions imposed to stem the spread of the Delta variant,
    several others are now urging mask wearing and social distancing, with some having contracted the virus despite being vaccinated.
> -  It will be interesting to pick the perceived change in tone in the time period between August 2020 (close to Presidential elections) and now (with resurgence in cases). We plan to collect tweets from the then President and incumbent and the current president and challenger(?) regarding the pandemic.
 In addition to this we will pull in tweets from all the Governors of every state, since they set the policy for each state . We can also expand the scope to top officials in both parties but the challenge will be to avoid selection bias. 
> -  The above will involve NLP applied on Twitter data and data scraped from the web and comments made to the press.
> -   We can move away from US shores and look into impact of policies towards Covid containment in various countries and predict what will succeed with the resurgence of cases. We will also dig into patterns of response in various countries to see if we can find clusters or groups with similar reponses. If we do find clusters, we can look into the similarity of what factors drives countries to respond in a certain way of the behavior differs (in terms of lockdown, travel restrictions, social distancing and mask wearing) from WHO recommendations."""
)

# Addendum : Additional Information, citations and disclaimers
###########################################
st.subheader("Appendix : Additional Information, citations and disclaimers")

st.markdown(
    """
**1- API Calls for vaccination data**
[Source: CDC ](https://www.cdc.gov/coronavirus/2019-ncov/vaccines/distributing/reporting-counties.html)

The lowdown on API calls:
To identify and limit rogue requests, most API data provisioning sites require that one acquire an API data token. After creating a Socrata account, I was able to apply for an API token for this application [here](https://data.cdc.gov/signed_out?return_to=%2Fprofile%2Fedit%2Fdeveloper_settings).

For each dataset, the CDC website also provides a URL to which this API taken can be applied. The URL request can be request the reposnse in JSON, CSV and other formats. I chose the CSV format.  Other than the token you can concatenate parameters of your GET request to the URL string.
FOr instance in our call below, the data was requested in batches of 500,000 rows (all columns - although these can be specifically requested). And so we limit the data tp 500,000 and update the offset by 500,000 with every call.

One more note about the APIToken. Since this is a personal secret access key, the token was stored in a **pickle** file (string format serialized) and then retrieved from it for the concatenation. 

The **requests** module of Python is used to submit this token and parameter enhanced URL. Since we are only interested in reading the data, we issue a **GET** command. 

The response **text** is converted to csv using the StringIO to convert it to String and then using pandas read_csv call which saves the data along with the headers into a dataframe.

The data for the vaciinations are updated on a daily basis by the CDC. Using the API enables us to update the visualization as and when the data gets updated. (We are storing it into a CSV file so that we do not send too many calls to the API endpoint as we develop).
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

__Such counties have been ignored from the county level analysis__.
"""
)


st.markdown(
    """
__3- The New Your Times mask wearing survey__
The New York Times is releasing estimates of mask usage by county in the United States.

>his data comes from a large number of interviews conducted online by the global data and survey firm Dynata at the request of The New York Times. The firm asked a question about mask use to obtain 250,000 survey responses between July 2 and July 14, enough data to provide estimates more detailed than the state level. (Several states have imposed new mask requirements since the completion of these interviews.)
Specifically, each participant was asked: How often do you wear a mask in public when you expect to be within six feet of another person?

This survey was conducted a single time, and at this point we have no plans to update the data or conduct the survey again.
The fields have the following definitions:
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
To transform raw survey responses into county-level estimates, the survey data was weighted by age and gender, and survey respondents’ locations were approximated from their ZIP codes. Then estimates of mask-wearing were made for each census tract by taking a weighted average of the 200 nearest responses, with closer responses getting more weight in the average. These tract-level estimates were then rolled up to the county level according to each tract’s total population.

By rolling the estimates up to counties, it reduces a lot of the random noise that is seen at the tract level. In addition, the shapes in the map are constructed from census tracts that have been merged together — this helps in displaying a detailed map, but is less useful than county-level in analyzing the data.
"""
)

st.info(
    """
__Note about the NYT Rolling Average of Covid cases data__

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

