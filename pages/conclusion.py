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
    # Expansion of the projects
    ###########################################
    st.header("Annex", anchor="annex")

    st.subheader("Datasets", anchor="datasets")

    st.markdown(
        "All datasets are publicly available following the information provided below."
    )

    st.write(
        "<bold>Note</bold>:<small> Census data obtained through API requires registration [here](https://api.census.gov/data/key_signup.html)</small>",
        unsafe_allow_html=True,
    )
    st.write(
        "<bold>Note</bold>:<small> Unemployment rate since 2019 was obtained through Bureau of Labor Statistics API v2 and requires registration [here](https://data.bls.gov/registrationEngine/)</small>",
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

    st.subheader("Merging everything using FIPS codes", anchor="mergingdatasets")

    st.markdown(
        """
    The datasets were joined using FIPS codes. FIPS stands for Federal Information Processing Standards, which are 
    published by the National Institute of Standards and Technology (NIST) that every tract, county and state in the US 
    is assigned. The code had to be extracted from a combined Geo code or had to be formed by concatenation if state and 
    counties were separately coded and served as the primary key to merge the datasets.

    For each visualization, the county/state level election data was combined with a feature of interest, such as 
    vaccination rate, COVID cases, unemployment, urban.rural demographics. Below is an example on the data transformation 
    flow used to generate the data for the first figure on the unemployment rate effect on the COVID response "Counties 
    Average Unemployment Rate and Vaccination Rate Since January 2021".
    """
    )

    # @st.cache(allow_output_mutation=True)
    def load_data_workflow_image():
        data_image = Image.open("./images/data-workflow.jpg")
        return data_image

    data_workflow_image = load_data_workflow_image()

    st.image(data_workflow_image, width=600)

    st.markdown(
        """
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
    """
    )

    # Expansion of the projects
    ###########################################
    st.subheader("Expansion of project", anchor="projectexpansion")

    st.markdown(
        """
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
    """
    )

    # Addendum : Additional Information, citations and disclaimers
    ###########################################
    st.subheader(
        "Appendix : Additional Information, citations and disclaimers",
        anchor="appendix",
    )

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
