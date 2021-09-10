
import pandas as pd
import numpy as np
import altair as alt
import sys

sys.path.append("../ETL")
from .EtlBase import DataFolder

#########################################################################################################

def GetCountyUrbanRuralData():
    '''
    Reads in an Excel file with Census Bureau urban/rural designation of US counties.    
    Returns a dataframe with the following columns:
        county_fips: The FIPS number of a county
        Urban/Rural: String designating a county as "urban" or "rural"
        PctRural: Percentage of "how rural" a county is according to the census
    
    Called by: MergeElectionUrbanRural()
               CountyElecUrbanRuralSplit()
    Functions called: None
    '''

    # Note: Data input file path
    CountyUrbanRural = pd.read_excel(DataFolder / 'County_Rural_Lookup.xlsx',skiprows=3, usecols='A:H')
    
    # Drop last six rows of footnotes
    CountyUrbanRural = CountyUrbanRural[:-6]
    
    # According to the input file notes, a county is considered urban if it is
    # less than 50% rural. The Rural designation is mainly based on population density.
    
    # Add urban/rural column and retain percentage for later use in charts.
    CountyUrbanRural['UrbanRural'] = CountyUrbanRural['2010 Census \nPercent Rural'] \
                                 .map(lambda x: 'urban' if x<50 else 'rural')
    
    CountyUrbanRural = CountyUrbanRural[['2015 GEOID', 'UrbanRural', '2010 Census \nPercent Rural']]
    
    CountyUrbanRural.rename(columns={'2015 GEOID': 'county_fips',
                                 '2010 Census \nPercent Rural': 'PctRural'}, inplace=True)
    
    # Need this column to be integer type
    CountyUrbanRural['county_fips'] = CountyUrbanRural['county_fips'].astype(int)
    
    return CountyUrbanRural

#########################################################################################################

def GetCountyElectionData():
    '''
    Reads in a CSV file with county-level presidential election results.
    Returns a dataframe for 2020 results with the following columns:
        state_po: State two-letter abbreviation
        county_name: Full county name
        county_fips: The FIPS number of a county
        candidate: Winning candidate name
        party: Winning candidate's party
        candidatevotes: Number of votes for the winning candidate
        totalvotes: Total votes cast in the county
    
    Called by: MergeElectionUrbanRural()
    Functions called: None
    '''

    # Election data by county 2000-2020
    # Note: Data input file path
    PECountyDF = pd.read_csv(DataFolder / 'countypres_2000-2020.csv')
    
    # Only interested in 2020
    PECountyDF = PECountyDF[PECountyDF['year'] == 2020]
    
    # Choose columns of interest.
    # Don't really need the candidate, but keep for later sanity checks and counts.
    PECountyDF = PECountyDF[['state_po', 'county_name', 'county_fips', 'candidate', 'party',
                         'candidatevotes','totalvotes']]
    
    # Only need the winning party
    # Source: https://stackoverflow.com/questions/15705630/ \
    #                 get-the-rows-which-have-the-max-value-in-groups-using-groupby
    idx = PECountyDF.groupby(['state_po', 'county_name', 'county_fips', 'totalvotes'])['candidatevotes'] \
                .transform(max) == PECountyDF['candidatevotes']
    PECountyDF = PECountyDF[idx]
    
    # Clean the county FIPS codes
    # Need the column to be integer type for the merge later on
    PECountyDF['county_fips'] = PECountyDF['county_fips'].astype(int)
    
    # Checked what effect a winning but unknown party has. Won't be able
    # to determine conservative/liberal leaning, so checked if dropping
    # them has a significant effect. There are no rows with winners
    # except 13 Vermont counties. Drop these counties since political
    # affiliation can't be easily determined.
    PECountyDF = PECountyDF[PECountyDF['party'] != 'OTHER']
    
    # Some states allow candidates to appear on multiple party lines.
    # Checked if that occurs in selected data, and where. None remaining
    # after losing candidates were excluded.
    
    return PECountyDF

#########################################################################################################

def MergeElectionUrbanRural():
    '''
    Merges the urban/rural designation of the counties with the county-level
        presidential election results.
    Returns a dataframe with the following columns:
        state_po: State two-letter abbreviation
        county_name: Full county name
        county_fips: The FIPS number of a county
        candidate: Winning candidate name
        party: Winning candidate's party
        candidatevotes: Number of votes for the winning candidate
        totalvotes: Total votes cast in the county
        Urban/Rural: String designating a county as "urban" or "rural"
        PctRural: Percentage of "how rural" a county is according to the census
    
    Called by: PlotElectionUrbanRural()
    Functions called:
        GetCountyUrbanRuralData()
        GetCountyElectionData()
    '''

    UrbanRuralDF = GetCountyUrbanRuralData()
    CountyElecDF = GetCountyElectionData()
    
    ElecUrbanRuralDF = CountyElecDF.merge(UrbanRuralDF, on='county_fips', how='inner')
    
    return ElecUrbanRuralDF

#########################################################################################################

def CountyElecUrbanRuralSplit():
    '''
    Reads in a CSV file with county-level presidential election results.
    Merges the data with the urban/rural designations of the counties.
    Splits the data by designation and writes out to two CSV files with
    the following columns:
        year: Election year
        state: Full state name
        state_po: State two-letter abbreviation
        county_name: Full county name
        county_fips: The FIPS number of a county
        office: PRESIDENT since this is for presidential elections only
        candidate: Winning candidate name
        party: Winning candidate's party
        candidatevotes: Number of votes for the winning candidate
        totalvotes: Total votes cast in the county
        version: [Relevant to data collection]
        mode: [Relevant to data collection]
        Urban/Rural: String designating a county as "urban" or "rural"
        PctRural: Percentage of "how rural" a county is according to the census
    Returns: None

    Called by: Main code
    Functions called: GetCountyUrbanRuralData()
    '''
    
    # Get full election results data once again.
    CountyPresDF = pd.read_csv(DataFolder / 'countypres_2000-2020.csv')
    
    # Get the urban/rural designation of each county
    CountyUrbanRural = GetCountyUrbanRuralData()
    
    # Merge the two to allow filtering by designation.
    CountyPresFull = CountyPresDF.merge(CountyUrbanRural, on='county_fips', how='inner')
    
    # Split in to urban and rural, and write each to a separate file
    CountyPresFullUrban = CountyPresFull[CountyPresFull['UrbanRural']=='urban']
    CountyPresFullUrban.to_csv(DataFolder / 'CountyPresFullUrban', index=False)
    
    CountyPresFullRural = CountyPresFull[CountyPresFull['UrbanRural']=='rural']
    CountyPresFullRural.to_csv(DataFolder / 'CountyPresFullRural', index=False)
    
    return

#########################################################################################################
