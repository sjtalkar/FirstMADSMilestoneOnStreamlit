import pandas as pd
from pathlib import Path

from ETL.EtlElection import getStateLevelElectionData2020
from ETL.EtlCovid import (getRollingCaseAverageSegmentLevel,
                          getPercentilePointChageDeathsData)
from ETL.EtlVaccine import (getDailyVaccinationPercentData,
                            getStateVaccinationDataWithAPI)
from ETL.EtlMask import (createDataForMaskUsageDistribution,
                            createDataForFreqAndInFreqMaskUse)
from ETL.EtlUnemployment import (getUnemploymentRateSince122019,
                                getUnemploymentCovidBase,
                                getUnemploymentCovidCorrelationPerMonth,
                                getJuly2020UnemploymentAndMask,
                                getUnemploymentVaccineCorrelationPerMonth)
from ETL.EtlUrbanRural import (MergeElectionUrbanRural,
                               CountyElecUrbanRuralSplit,
                               getUrbanRuralElectionRollingData,
                               getUrbanRuralAvgDeathsData)
#
# This script runs all the functions used to processed all the datasets used in the different visualizaionts
# It then saves all those processed datasets in files to be used in Streamlit. This is done to speed-up the loading time
# of the streamlit page by avoiding processing the data
#

if __name__ == '__main__':

    Path("../data").mkdir(exist_ok=True)

    case_rolling_df = getRollingCaseAverageSegmentLevel()
    case_rolling_df.to_csv(path_or_buf ="../data/case_rolling_df.csv", index=False)

    election_change_and_covid_death_df = getPercentilePointChageDeathsData()
    election_change_and_covid_death_df.to_csv(path_or_buf ="../data/election_change_and_covid_death_df.csv",
                                              index=False)

    daily_vaccination_percent_df = getDailyVaccinationPercentData()
    daily_vaccination_percent_df.to_csv(path_or_buf ="../data/daily_vaccination_percent_df.csv",
                                        index=False)

    state_vaccine_df, us_case_rolling_df, state_case_rolling_df = getStateVaccinationDataWithAPI()
    state_vaccine_df.to_csv(path_or_buf ="../data/state_vaccine_df.csv", index=False)
    us_case_rolling_df.to_csv(path_or_buf ="../data/us_case_rolling_df.csv", index=False)
    state_case_rolling_df.to_csv(path_or_buf ="../data/state_case_rolling_df.csv", index=False)

    state_election_df = getStateLevelElectionData2020()
    state_election_df.to_csv(path_or_buf ="../data/state_election_df.csv", index=False)

    mask_distribution_df = createDataForMaskUsageDistribution()
    mask_distribution_df.to_csv(path_or_buf ="../data/mask_distribution_df.csv", index=False)

    county_pop_mask_df, county_pop_mask_freq_df, county_pop_mask_infreq_df = createDataForFreqAndInFreqMaskUse()
    county_pop_mask_df.to_csv(path_or_buf ="../data/county_pop_mask_df.csv", index=False)
    county_pop_mask_freq_df.to_csv(path_or_buf ="../data/county_pop_mask_freq_df.csv", index=False)
    county_pop_mask_infreq_df.to_csv(path_or_buf ="../data/county_pop_mask_infreq_df.csv", index=False)

    #
    # Package unemployments dataframse
    #

    unemployment_rate_since_2019_df = getUnemploymentRateSince122019()
    unemployment_rate_since_2019_df.to_csv(path_or_buf="../data/unemployment_rate_since_2019_df.csv",
                                           index=False)

    unemployment_covid_df = getUnemploymentCovidBase()
    unemployment_covid_df.to_csv(path_or_buf="../data/unemployment_covid_df.csv", index=False)

    unemployment_covid_correlation_df = getUnemploymentCovidCorrelationPerMonth(unemployment_covid_df)
    unemployment_covid_correlation_df.to_csv(path_or_buf="../data/unemployment_covid_correlation_df.csv",
                                             index=False)

    unemployment_freq_mask_july_df, unemployment_infreq_mask_july_df = getJuly2020UnemploymentAndMask(
        unemployment_covid_df)
    unemployment_freq_mask_july_df.to_csv(path_or_buf="../data/unemployment_freq_mask_july_df.csv",
                                          index=False)
    unemployment_infreq_mask_july_df.to_csv(path_or_buf="../data/unemployment_infreq_mask_july_df.csv",
                                          index=False)

    unemployment_vaccine_correlation_df = getUnemploymentVaccineCorrelationPerMonth(df=unemployment_rate_since_2019_df)
    unemployment_vaccine_correlation_df.to_csv(path_or_buf="../data/unemployment_vaccine_correlation_df.csv",
                                               index=False)

    #
    # Package urban/rural dataframse
    #
    urban_rural_election_df = MergeElectionUrbanRural()
    urban_rural_election_df.to_csv(path_or_buf="../data/urban_rural_election_df.csv",
                                               index=False)

    urban_rural_rolling_avg_full_df, urban_rolling_avg_full_df, rural_rolling_avg_full_df = CountyElecUrbanRuralSplit(
        getUrbanRuralElectionRollingData)
    urban_rural_rolling_avg_full_df.to_csv(path_or_buf="../data/urban_rural_rolling_avg_full_df.csv",
                                   index=False)
    urban_rolling_avg_full_df.to_csv(path_or_buf="../data/urban_rolling_avg_full_df.csv",
                                   index=False)
    rural_rolling_avg_full_df.to_csv(path_or_buf="../data/rural_rolling_avg_full_df.csv",
                                   index=False)

    urban_rural_avgdeaths_full_df, urban_avgdeaths_full_df, rural_avgdeaths_full_df = CountyElecUrbanRuralSplit(
        getUrbanRuralAvgDeathsData)
    urban_rural_avgdeaths_full_df.to_csv(path_or_buf="../data/urban_rural_avgdeaths_full_df.csv",
                                           index=False)
    urban_avgdeaths_full_df.to_csv(path_or_buf="../data/urban_avgdeaths_full_df.csv",
                                     index=False)
    rural_avgdeaths_full_df.to_csv(path_or_buf="../data/rural_avgdeaths_full_df.csv",
                                     index=False)