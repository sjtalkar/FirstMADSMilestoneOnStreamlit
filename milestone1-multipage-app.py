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
from pages import political, demographics, unemployment, conclusion, introduction


DataFolder = Path("./data/")


# Set streamlit page to wide format
st.set_page_config(layout="wide")

app = MultiPage()
app.add_page("Introduction", introduction.app)
app.add_page("Political Affiliation", political.app)
app.add_page("The Urban Rural Divide", demographics.app)
app.add_page("Unemployment and Covid", unemployment.app)
app.add_page("Conclusion and expansion", conclusion.app)

app.run()
