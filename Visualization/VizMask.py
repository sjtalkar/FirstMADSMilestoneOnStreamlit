import pandas as pd
import altair as alt
import sys

sys.path.append("../ETL")
from ETL.EtlBase import TO_REPUBLICAN, TO_DEMOCRAT, STAYED_DEMOCRAT, STAYED_REPUBLICAN
from ETL.EtlElection import *
from ETL.EtlVaccine import *
from ETL.EtlMask import *
from .VizBase import *

# uses intermediate json files to speed things up
alt.data_transformers.enable("json")
alt.data_transformers.disable_max_rows()


def plotCountyMaskUsage(df, mask_usage_type, color_scheme):

    source = df[df["mask_usage_type"] == mask_usage_type]

    chart = (
        alt.Chart(counties)
        .mark_geoshape()
        .encode(
            color=alt.Color("mask_usage:Q", scale=alt.Scale(scheme=color_scheme)),
            tooltip=[
                alt.Tooltip("CTYNAME:N", title="County name: "),
                alt.Tooltip("mask_usage:Q", title="Never use mask: "),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                source,
                "COUNTYFP",
                ["mask_usage", "mask_usage_types", "COUNTYFP", "CTYNAME"],
            ),
        )
        .project(type="albersUsa")
        .properties(width=400, height=300)
    )
    return chart


def plotAllMaskUsageTypesForCounties():
    county_pop_mask_df = getCountyPopulationMask()
    county_pop_mask_melt_df = county_pop_mask_df.melt(
        id_vars=[
            "STATE",
            "COUNTYFP",
            "CTYNAME",
            "POPESTIMATE2016",
            "POPESTIMATE2020",
            "RNETMIG2020",
        ],
        value_vars=["NEVER", "RARELY", "SOMETIMES", "FREQUENTLY", "ALWAYS",],
        var_name="mask_usage_type",
        value_name="mask_usage",
        col_level=None,
        ignore_index=True,
    )

    colors = ["purplered", "redpurple", "yelloworangebrown", "purpleblue", "darkblue"]
    usage_types = county_pop_mask_melt_df.mask_usage_type.unique()
    chart_list = []
    for color_scheme, usage_type in tuple(zip(colors, usage_types)):
        chart = plotCountyMaskUsage(
            county_pop_mask_melt_df, usage_type, color_scheme
        ).properties(title=f"Mask usage type: {usage_type}")
        chart_list.append(chart)

    return chart_list


def createCombinedElectoralAndMaskUsageCharts():
    election_winners_df = getElectionSegmentsData()
    counties = alt.topo_feature(data.us_10m.url, "counties")
    us_states = alt.topo_feature(data.us_10m.url, "states")
    source = election_winners_df
    source["COUNTYANDFP"] = (
        election_winners_df["CTYNAME"].str.capitalize()
        + " ("
        + election_winners_df["COUNTYFP"].astype(str)
        + ")"
    )
    source["segmentname"] = election_winners_df["changecolor"].map(color_segment_dict)

    # Create a selection based on COUNTYFP since several states can have counties with same name
    click = alt.selection_multi(fields=["COUNTYANDFP"])

    # input_dropdown = alt.binding_select(options=source['segmentname'].unique().tolist(), name='Affiliation: ')
    input_dropdown = alt.binding_select(
        options=["To Democrat", "To Republican"], name="Affiliation: "
    )
    segment_selection = alt.selection_single(
        fields=["segmentname"], bind=input_dropdown, name="Affiliation: "
    )

    county_winners_chart = (
        alt.Chart(
            counties, title="Counties that changed affiliations in 2020 elections"
        )
        .mark_geoshape()
        .encode(
            color=alt.Color("changecolor:N", scale=None),
            tooltip=[
                alt.Tooltip("state:N", title="State: "),
                alt.Tooltip("CTYNAME:N", title="County name: "),
                alt.Tooltip(
                    "party_winner_2016:N", title="2016 Presidential election winner: "
                ),
                alt.Tooltip(
                    "party_winner_2020:N", title="2020 Presidential election winner: "
                ),
            ],
            # opacity=alt.condition(click, alt.value(0.8), alt.value(0.2)),
            opacity=alt.condition(segment_selection, alt.value(0.8), alt.value(0.2)),
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                source,
                "COUNTYFP",
                [
                    "party_winner_2016",
                    "party_winner_2020",
                    "COUNTYFP",
                    "CTYNAME",
                    "COUNTYANDFP",
                    "changecolor",
                    "state",
                    "state_po",
                    "segmentname",
                ],
            ),
        )
        .add_selection(
            segment_selection  ## Make sure you have added the selection here
        )
        .add_selection(click)  ## Make sure you have added the selection here
        .project(type="albersUsa")
        .properties(width=550, height=200)
    )

    outline = (
        alt.Chart(us_states)
        .mark_geoshape(stroke="grey", fillOpacity=0)
        .project(type="albersUsa")
        .properties(width=550, height=200)
    )
    #############################################
    county_pop_mask_melt_df = createFrequentAndInfrequentMaskUsers()
    county_pop_mask_melt_df["COUNTYANDFP"] = (
        county_pop_mask_melt_df["CTYNAME"].str.replace(" County", "")
        + " ("
        + county_pop_mask_melt_df["COUNTYFP"].astype(str)
        + ")"
    )
    county_pop_mask_melt_df["segmentname"] = county_pop_mask_melt_df["changecolor"].map(
        color_segment_dict
    )

    county_pop_mask_melt_df.sort_values(
        by=["mask_usage_type", "mask_usage"], inplace=True
    )

    county_pop_mask_republican = county_pop_mask_melt_df[
        county_pop_mask_melt_df["changecolor"].isin([TO_REPUBLICAN])
    ].copy()
    county_pop_mask_democrat = county_pop_mask_melt_df[
        county_pop_mask_melt_df["changecolor"].isin([TO_DEMOCRAT])
    ].copy()
    county_pop_mask_republican.sort_values(
        by=["mask_usage_type", "mask_usage"], inplace=True
    )
    county_pop_mask_democrat.sort_values(
        by=["mask_usage_type", "mask_usage"], inplace=True
    )
    county_order_republican = county_pop_mask_republican[
        county_pop_mask_republican["mask_usage_type"] == "FREQUENT"
    ]["COUNTYFP"].unique()
    county_order_democrat = county_pop_mask_democrat[
        county_pop_mask_democrat["mask_usage_type"] == "FREQUENT"
    ]["COUNTYFP"].unique()

    county_pop_mask_stayed_republican = county_pop_mask_melt_df[
        county_pop_mask_melt_df["changecolor"].isin([STAYED_REPUBLICAN])
    ].copy()
    county_pop_mask_stayed_democrat = county_pop_mask_melt_df[
        county_pop_mask_melt_df["changecolor"].isin([STAYED_DEMOCRAT])
    ].copy()
    county_pop_mask_stayed_republican.sort_values(
        by=["mask_usage_type", "mask_usage"], inplace=True
    )
    county_pop_mask_stayed_democrat.sort_values(
        by=["mask_usage_type", "mask_usage"], inplace=True
    )
    county_order_stayed_republican = county_pop_mask_stayed_republican[
        county_pop_mask_stayed_republican["mask_usage_type"] == "FREQUENT"
    ]["COUNTYFP"].unique()
    county_order_stayed_democrat = county_pop_mask_stayed_democrat[
        county_pop_mask_stayed_democrat["mask_usage_type"] == "FREQUENT"
    ]["COUNTYFP"].unique()

    a = (
        alt.Chart(county_pop_mask_republican)
        .mark_bar()
        .encode(
            x=alt.X("COUNTYANDFP:N", title="", sort=county_order_republican),
            y=alt.Y("mask_usage:Q", title=""),
            color=alt.Color(
                "mask_usage_type:N",
                scale=alt.Scale(
                    domain=["FREQUENT", "NOT FREQUENT"],
                    range=["#ddccbb", STAYED_REPUBLICAN],
                ),
                legend=alt.Legend(title="Mask usage type"),
            ),
            opacity=alt.condition(segment_selection, alt.value(0.8), alt.value(0.2)),
        )
        .add_selection(
            segment_selection  ## Make sure you have added the selection here
        )
        .add_selection(click)  ## Make sure you have added the selection here
        .properties(height=100, width=200)
    )

    a1 = (
        alt.Chart(county_pop_mask_stayed_republican)
        .mark_bar()
        .encode(
            x=alt.X("COUNTYANDFP:N", title="", sort=county_order_stayed_republican),
            y=alt.Y("mask_usage:Q", title=""),
            color=alt.Color(
                "mask_usage_type:N",
                scale=alt.Scale(
                    domain=["FREQUENT", "NOT FREQUENT"],
                    range=["#ddccbb", STAYED_REPUBLICAN],
                ),
                legend=alt.Legend(title="Mask usage type"),
            ),
            opacity=alt.condition(segment_selection, alt.value(0.8), alt.value(0.2)),
        )
        .add_selection(
            segment_selection  ## Make sure you have added the selection here
        )
        .properties(height=100, width=200)
    )

    b = (
        alt.Chart(county_pop_mask_democrat)
        .mark_bar()
        .encode(
            alt.X("COUNTYANDFP:N", title="", sort=county_order_democrat),
            alt.Y("mask_usage:Q", title=""),
            alt.Color(
                "mask_usage_type:N",
                scale=alt.Scale(
                    domain=["FREQUENT", "NOT FREQUENT"],
                    range=["#ddccbb", STAYED_DEMOCRAT],
                ),
                legend=alt.Legend(title="Mask usage type"),
            ),
            opacity=alt.condition(segment_selection, alt.value(0.8), alt.value(0.2)),
        )
        .add_selection(
            segment_selection  ## Make sure you have added the selection here
        )
        .properties(height=100, width=700)
    )

    return (
        (county_winners_chart + outline)
        & alt.vconcat(a, b).resolve_scale(color="independent")
    ).configure_concat(spacing=10)


############################################################################################################
######################Mask Data Charts with interactive legend
############################################################################################################
def createFreqCountyMaskUsageWithRanges(
    _type: str,
    county_pop_mask_df: pd.DataFrame() = None,
    county_pop_mask_freq_df: pd.DataFrame() = None,
    county_pop_mask_infreq_df: pd.DataFrame() = None,
    small_avg_df: pd.DataFrame() = None,
):
    """[This function accepts the type of Mask usage - Frequent or Infrequent and creates a
        Geo chart with colors based o nrange of frequent mask usage]

    Args:
        _type ([string]): ["FREQUENT"/"NON FREQUENT"]

    Returns:
        [_type]: [description]
    """

    counties = alt.topo_feature(data.us_10m.url, "counties")
    # Setup interactivty
    click = alt.selection_single(
        fields=["range_color"], init={"range_color": "#C5DDF9"}
    )

    if (
        (county_pop_mask_df is None)
        or (county_pop_mask_freq_df is None)
        or (county_pop_mask_infreq_df is None)
    ):
        # Get data
        (
            county_pop_mask_df,
            county_pop_mask_freq_df,
            county_pop_mask_infreq_df,
        ) = createDataForFreqAndInFreqMaskUse()

    if small_avg_df is None:
        small_avg_df = createDataForMaskUsageDistribution()

    if _type == "FREQUENT":
        source = county_pop_mask_freq_df
    else:
        source = county_pop_mask_infreq_df

    county_mask_chart = (
        alt.Chart(
            counties,
            title={
                "text": [
                    f"{_type.capitalize()} Mask Usage From Survey Response by County and Political Affiliation"
                ],
                "subtitle": [
                    "Hover for tooltip with state and mask usage percent value",
                    "Click on legend colors for selecting counties with given political affiliation",
                    "and chosen range of mask usage",
                ],
            },
        )
        .mark_geoshape(stroke="#706545", strokeWidth=0.1)
        .encode(
            color=alt.condition(
                click, alt.value("#F9A602"), alt.Color("range_color:N", scale=None),
            ),
            tooltip=[
                # alt.Tooltip('state:N', title='State: '),
                alt.Tooltip("CTYNAME:N", title="County name: "),
                alt.Tooltip("mask_usage_type:N", title="Mask Usage Type: "),
                alt.Tooltip("mask_usage:Q", title="Mask Usage Percent: ", format=".0%"),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                source,
                "COUNTYFP",
                [
                    "COUNTYFP",
                    "CTYNAME",
                    "mask_usage_type",
                    "mask_usage",
                    "mask_usage_range",
                    "range_color",
                ],
            ),
        )
        .add_selection(click)
        .project(type="albersUsa")
        .properties(width=550, height=200)
    )

    # Create interactive model name legend
    legend_democrat = (
        alt.Chart(
            source[source["segmentname"] == "Democrat"],
            title={"text": "Democrat(2020)", "fontSize": 10},
        )
        .mark_point(size=50, filled=True)
        .encode(
            y=alt.Y(
                "mask_usage_range:N",
                axis=alt.Axis(orient="right"),
                title=None,
                sort=["Low (<=50%)", "Moderate (50%-80%)", "High (>80%)",],
            ),
            color=alt.condition(
                click,
                alt.value("#F9A602"),
                alt.Color(
                    "mask_usage_range:N",
                    scale=alt.Scale(
                        domain=["Low (<=50%)", "Moderate (50%-80%)", "High (>80%)",],
                        range=["#C5DDF9", "#3CA0EE", "#0015BC"],
                    ),
                    legend=None,
                ),
            ),
        )
        .add_selection(click)
        .properties(width=20, height=30)
    )

    legend_republican = (
        alt.Chart(
            source[source["segmentname"] == "Republican"],
            title={"text": "Select: Republican(2020)", "fontSize": 10},
        )
        .mark_point(size=50, filled=True)
        .encode(
            y=alt.Y(
                "mask_usage_range:N",
                axis=alt.Axis(orient="right"),
                title=None,
                sort=["Low (<=50%)", "Moderate (50%-80%)", "High (>80%)",],
            ),
            color=alt.condition(
                click,
                alt.value("#F9A602"),
                alt.Color(
                    "mask_usage_range:N",
                    scale=alt.Scale(
                        domain=["Low (<=50%)", "Moderate (50%-80%)", "High (>80%)",],
                        range=["#F2A595", "#EE8778", "#970D03"],
                    ),
                    legend=None,
                ),
            ),
        )
        .add_selection(click)
        .properties(width=20, height=30)
    )

    # create an average chart with just two parties
    average_mask_chart = (
        alt.Chart(small_avg_df, title="")
        .mark_bar(width=5)
        .encode(
            y=alt.Y(
                "mask_usage_type:N",
                title="",
                axis=alt.Axis(orient="right", labelFontSize=5),
            ),
            x=alt.X("mean(mask_usage):Q", title=None),
            color=alt.Color("changecolor:N", scale=None, legend=None),
            row=alt.Row("party:N", title=None, header=alt.Header(labels=False)),
        )
        .properties(width=50, height=20)
    )

    return county_mask_chart, legend_republican, legend_democrat, average_mask_chart


def createMaskUsageDistributionChart(df: pd.DataFrame() = None):
    if df is None:
        df = createDataForMaskUsageDistribution()

    density_chart = (
        alt.Chart(
            df,
            title={
                "text": [
                    "Mask Usage Survey Response Distribution by Political Affiliation"
                ],
                "subtitle": [
                    "Estimates from The New York Times, based on roughly 250,000 interviews"
                    " conducted by Dynata from July 2 to July 14, 2020."
                ],
            },
        )
        .transform_density(
            density="mask_usage",
            groupby=["mask_usage_type", "changecolor"],
            as_=["mask_usage", "Density"],
        )
        .mark_area(orient="vertical", opacity=0.8)
        .encode(
            x=alt.X("mask_usage:Q", axis=alt.Axis(title=None, format=".0%")),
            y="Density:Q",
            color=alt.Color("changecolor:N", scale=None),
            facet=alt.Facet(
                "mask_usage_type:N",
                title=None,
                header=alt.Header(
                    labelOrient="top", labelFontSize=8, labelFontWeight="bold"
                ),
            ),
        )
        .properties(height=100, width=300)
    )

    return density_chart