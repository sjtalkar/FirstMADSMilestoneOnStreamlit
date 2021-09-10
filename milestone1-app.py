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
