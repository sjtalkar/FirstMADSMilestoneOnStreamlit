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

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
    def load_unemployment_covid_correlation_df():
        df = pd.read_csv(
            "./data/unemployment_covid_correlation_df.csv",
            dtype={"month": str, "party": str, "variable": str, "value": float},
        )
        return df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
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
        freq_df = pd.read_csv(
            "./data/unemployment_freq_mask_july_df.csv", dtype=dtypes,
        )
        infreq_df = pd.read_csv(
            "./data/unemployment_infreq_mask_july_df.csv", dtype=dtypes,
        )
        return freq_df, infreq_df

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache
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

    st.subheader("COVID effects")

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

    st.subheader("COVID response")

    st.markdown(
        """
    When we look at the Republican and Democrat counties' monthly average unemployment rate and COVID cases 
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

    st.markdown(
        """
    As we wanted to verify if unemployment rate could have a stronger impact on the COVID response than political 
    affiliation, we see that 
    * there is no correlation between COVID case and unemployment rate, and between unemployment rate and COVID 
    response behaviors like wearing a mask or getting vaccinated 
    * On average, Democrat counties have higher unemployment rate, less COVID cases but better follow COVID response 
    CDC guidelines while Republican counties show opposite trends and behaviors
    """
    )

    st.markdown("""---""")

    # Conclusion
    ###########################################
    st.header("Conclusion", anchor="conclusion")

    st.markdown(
        """
    Preliminary EDA clearly indicated a distinct difference in rates of infection along party lines at the county levels. 
    Towards the beginning of July of 2021, we show evidence of cases rising steeply in states with low vaccination rates. 
    These states that predominantly voted Republican (such as Louisiana and Mississippi), are clustered in the Southern 
    parts of the United States and can visually be spotted as states with low vaccination rates. The short-term NYT mask 
    adherence survey data also showed marginally higher adherence rates among counties that voted Democrat. We also noted 
    that socio-economic factors such as unemployment and urban or rural demographics only served to further highlight the 
    split in response, and ultimately the effects of COVID,  along political lines.  
    """
    )

    st.markdown("""---""")

