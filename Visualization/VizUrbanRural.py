
import pandas as pd
import numpy as np
import altair as alt
import sys

sys.path.append("../ETL")
from ETL.EtlBase import DataFolder
from ETL.EtlUrbanRural import *

#######################################################################################################

def ElectionUrbanRuralDensityPlot(PEUrbanRuralDF:pd.DataFrame()=None):
    '''
    Plots the urban/rural designation of the counties merged with the county-level
        presidential election results as a density plot
    Returns a chart showing:
        x-axis: party - categorical - Winning candidate's party
        y-axis: PctRural - quantitative - Percentage of "how rural" a county is
    
    Called by: Main code
    Functions called: MergeElectionUrbanRural()
    '''    
    
    party_domain = ["DEMOCRAT", "REPUBLICAN"]
    party_range = ["#030D97", "#970D03"]

    if PEUrbanRuralDF is None:
        PEUrbanRuralDF = MergeElectionUrbanRural()
    
    PctRuralDomain = [0, int(PEUrbanRuralDF["PctRural"].max() / 10) * 10]

    densityplot = alt.Chart(
        PEUrbanRuralDF,
        width=500,
        height=400,
        title={
            "text": [
                "Distribution of counties by percent rural"
            ],
            "subtitle": ["Counties won by democratic candidates vs won by republicans",],
        }
    ).transform_density(
        density="PctRural",
        groupby=["party"],
        as_=["Percent Rural", "Density"]
    ).mark_area(orient="vertical", opacity=0.8).encode(
        x=alt.X("Percent Rural:Q",
                scale=alt.Scale(domain=PctRuralDomain)),
        y=alt.Y("Density:Q",
                scale=alt.Scale(domain=[0, 0.02])),
        color=alt.Color("party:N",
                        scale=alt.Scale(domain=party_domain, range=party_range),
                        title="Party", legend=None)
    ).configure_title(
        align="left",
        anchor="start"
    )
    return densityplot

#######################################################################################################

def UrbanRuralCorrelation(PEUrbanRuralDF:pd.DataFrame()=None):
    '''
    Plots the "percent rural" of counties vs fraction of the vote
        for the winning party, a separate chart for each party
    Returns two charts, one for each party, showing:
        x-axis: Fraction of the vote - quantitative
        y-axis: PctRural - quantitative 
    
    Called by: Main code
    Functions called: MergeElectionUrbanRural()
    '''

    
    party_domain = ["DEMOCRAT", "REPUBLICAN"]
    party_range = ["#030D97", "#970D03"]
    
    # Get the data and split into democrat and republican
    if PEUrbanRuralDF is None:
        PEUrbanRuralDF = MergeElectionUrbanRural()

        
    PEUrbanRuralDF2 = PEUrbanRuralDF.copy()
    PEUrbanRuralDF2['fractionvotes'] = PEUrbanRuralDF2['candidatevotes'] / PEUrbanRuralDF2['totalvotes']
    
    PEUrbanRuralDFDem = PEUrbanRuralDF2.copy()
    PEUrbanRuralDFDem = PEUrbanRuralDFDem[PEUrbanRuralDFDem['party'] == 'DEMOCRAT']
    
    PEUrbanRuralDFRep = PEUrbanRuralDF2.copy()
    PEUrbanRuralDFRep = PEUrbanRuralDFRep[PEUrbanRuralDFRep['party'] == 'REPUBLICAN']


    PctRuralDomain = [0, int(PEUrbanRuralDF2["PctRural"].max() / 10) * 10]
    
    # Prepare the democrat chart
    voteDEMplot = alt.Chart(
        PEUrbanRuralDFDem,
        width=400,
        height=200,
        title={
            "text": [
                "Correlation between percent rural and fraction of county vote"
            ],
            "subtitle": ["Counties won by democratic candidates",],
            "align": "left",
            "anchor": "start"
        }
    ).mark_point(filled=True, size=30).encode(
        y=alt.Y(
            "PctRural:Q",
            title="Percent Rural",
            scale=alt.Scale(
                domain=PctRuralDomain)
        ),
        x=alt.X(
            "fractionvotes:Q",
            title="Fraction of Vote",
            scale=alt.Scale(
                domain=[0, 1.0])),
        color=alt.Color("party:N", scale=alt.Scale(domain=party_domain, range=party_range),
                        title="Party", legend=None)
    )

    # Add a regression line
    finalDEMchart=(voteDEMplot + voteDEMplot.transform_regression("fractionvotes",
                                                          "PctRural").mark_line(
        color="black").encode(color=alt.value("black"))
    )
    
    # Prepare the republican chart
    voteREPplot = alt.Chart(
        PEUrbanRuralDFRep,
        width=400,
        height=200,
        title={
            "text": [
                "Correlation between percent rural and fraction of county vote"
            ],
            "subtitle": ["Counties won by republican candidates",],
            "align": "left",
            "anchor": "start"
        }
    ).mark_point(filled=True, size=30).encode(
        y=alt.Y(
            "PctRural:Q",
            title=None,
            scale=alt.Scale(
                domain=PctRuralDomain)
        ),
        x=alt.X(
            "fractionvotes:Q",
            title="Fraction of Vote",
            scale=alt.Scale(
                domain=[0, 1.0])),
        color=alt.Color("party:N", scale=alt.Scale(domain=party_domain, range=party_range),
                        title="Party", legend=None)
    )

    # Add a regression line
    finalREPchart=(voteREPplot + voteREPplot.transform_regression("fractionvotes",
                                                          "PctRural").mark_line(
        color="black").encode(color=alt.value("black"))
    )
    
    finalchart = alt.ConcatChart(concat=[finalDEMchart, finalREPchart])

    return finalchart

#######################################################################################################
