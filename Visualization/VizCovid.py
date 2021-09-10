import pandas as pd
import altair as alt
import sys
from vega_datasets import data
import plotly.graph_objs as go

sys.path.append("../ETL")
from ETL.EtlElection import *
from ETL.EtlCovid import *
from .VizBase import *

# uses intermediate json files to speed things up
alt.data_transformers.enable("json")
alt.data_transformers.disable_max_rows()


def createPercentPointChangeAvgDeathsChart(df: pd.DataFrame() = None):
    """
      THIS FUNCTION showing average COVID deaths versus percent change for each political affiliation.

      Functions called: None
      Called by: Main code

      Input: None
      Returns: Percent point change chart
    """

    if df is None:
        df = getPercentilePointChageDeathsData()

    input_dropdown = alt.binding_select(
        options=df["segmentname"].unique().tolist(), name="Affiliation: "
    )
    selection = alt.selection_single(
        fields=["segmentname"], bind=input_dropdown, name="Affiliation: "
    )

    perc_point_deaths_chart = (
        alt.Chart(
            df,
            title={
                "text": [
                    "Covid deaths in election year (2020) versus percentage point difference in votes (from 2016 to 2020)"
                ],
                "subtitle": ["Select party affiliation from dropdown",],
            },
        )
        .mark_circle()
        .encode(
            x=alt.X("pct_increase:Q", title="Percent point change"),
            y=alt.Y("deaths_avg_per_100k:Q", title="Average deaths per 100K"),
            color=alt.condition(
                selection,
                alt.Color("changecolor:N", scale=None, legend=None),
                alt.value("#EDEDED"),
            ),
            opacity=alt.condition(selection, alt.value(1), alt.value(0.1)),
            # size= alt.Size("totalvotes_2020:Q", scale=alt.Scale(domain=[100,20000]) , legend=None),
            tooltip=[
                alt.Tooltip("CTYNAME:N", title="County Name:"),
                alt.Tooltip("state:N", title="State Name:"),
                alt.Tooltip(
                    "pct_increase:N", title="Percent Point Increase:", format=".2f"
                ),
            ],
        )
        .properties(height=300, width=800)
        .add_selection(selection)
    )

    mark_more_deaths_line1 = (
        alt.Chart(pd.DataFrame({"x": [0]})).mark_rule(strokeDash=[2, 5]).encode(x="x")
    )
    mark_more_deaths_line2 = (
        alt.Chart(pd.DataFrame({"y": [1.13]}))
        .mark_rule(strokeDash=[2, 5])
        .encode(y="y")
    )

    annotations = [
        [8, 1.8, "Counties above this line\nhad the highest COVID-19 death rates"]
    ]
    a_df = pd.DataFrame(annotations, columns=["x", "y", "note"])

    more_deaths_text = (
        alt.Chart(a_df)
        .mark_text(align="left", baseline="middle", fontSize=10, dx=7)
        .encode(x="x:Q", y="y:Q", text=alt.Text("note:N"))
    )

    return (
        perc_point_deaths_chart
        + mark_more_deaths_line1
        + mark_more_deaths_line2
        + more_deaths_text
    )


def createSankeyForAffilitionChange():
    """
        This function creates a Sankey chart that shows the County affiliation change from
        2016 to 2019
        The interactive tooltip will offer the actual numbers
    """
    election_winners_df = getElectionSegmentsData()
    sankey_df = (
        election_winners_df.groupby(["party_winner_2016", "party_winner_2020"])
        .agg(countiesingroup=("totalvotes_2016", "count"))
        .reset_index()
    )

    sankey_df["party_winner_2016"] = sankey_df["party_winner_2016"] + "_2016"
    sankey_df["party_winner_2020"] = sankey_df["party_winner_2020"] + "_2020"

    label_list = (
        sankey_df["party_winner_2016"].unique().tolist()
        + sankey_df["party_winner_2020"].unique().tolist()
    )
    label_idx_dict = {}
    for idx, label in enumerate(label_list):
        label_idx_dict[label] = idx

    label_list = [
        f"Voted {label.split('_')[0].capitalize()} in {label.split('_')[1]}"
        for label in label_list
    ]

    sankey_df["2016_idx"] = sankey_df["party_winner_2016"].map(label_idx_dict)
    sankey_df["2020_idx"] = sankey_df["party_winner_2020"].map(label_idx_dict)

    source = sankey_df["2016_idx"].tolist()
    target = sankey_df["2020_idx"].tolist()
    values = sankey_df["countiesingroup"].tolist()
    color_link = ["#BEDDFE", "#FAED27", "#FF0000", "#0000FF", "#FFE9EC"]
    color_node = ["#80CEE1", "#FF6961", "#0000FF", "#96D2B7", "#FF0000"]

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label_list,
                    color=color_node,
                    customdata=label_list,
                    hovertemplate="%{customdata} has  %{value} counties<extra></extra>",
                ),
                link=dict(
                    source=source,
                    target=target,
                    value=values,
                    color=color_link,
                    hovertemplate="Link from  %{source.customdata}<br />"
                    + "to %{target.customdata}<br />has  %{value} counties<extra></extra>",
                ),
            )
        ]
    )

    fig.update_layout(
        title_text="County affiliation change from 2016 to 2020", font_size=12,
    )

    # Set the theme
    fig.layout.template = "custom_dark"
    return fig
