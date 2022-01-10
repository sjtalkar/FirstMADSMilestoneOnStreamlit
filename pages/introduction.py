# Import necessary libraries
import streamlit as st
import pandas as pd
import numpy as np
import base64
import re
import time

import altair as alt
from pathlib import Path
import streamlit as st
from PIL import Image


def app():
    # Show the header image

    # Remove some caching to reduce memory usage due to Streamlit limitations
    # @st.cache(allow_output_mutation=True)
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

    st.markdown("""---""")
