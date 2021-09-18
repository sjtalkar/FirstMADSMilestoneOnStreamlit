import altair as alt

import sys

from vega_datasets import data

sys.path.append("../ETL")
from ETL.EtlBase import segment_color_dict
from ETL.EtlElection import *
from ETL.EtlCovid import *

# Formatting in Altair follows : https://github.com/d3/d3-format
# uses intermediate json files to speed things up
alt.data_transformers.enable("json")
alt.data_transformers.disable_max_rows()



########################################################################################
def createCovidConfirmedTimeseriesChart(case_rolling_df):
    """
      THIS FUNCTION uses the 'base' encoding chart created by getBaseChart() to create a line chart.
      
      The highlight_segment variable uses the mark_line function to create a line chart out of the encoding. The
      color of the line is set using the conditional color set for the categorical variable using the selection.
      The chart is bound to the selection using add_selection.
      
      It also creates a selector element of a vertical array of circles so the user can select between segment.
      
      Functions called: getSelection(), getBaseChart()
      Called by: Main code
        
      Input: Dataframe with rolling average of cases created by getRollingCaseAverageSegmentLevel()
      Returns: base, make_selector, highlight_segment, radio_select      

    """

    radio_select, change_color_condition = getSelection()

    make_selector = (
        alt.Chart(case_rolling_df)
            .mark_circle()
            .encode(
            y=alt.Y(
                "segmentname:N",
                axis=alt.Axis(
                    title="Pick affiliation", titleFontSize=15, orient="right"
                ),
            ),
            color=change_color_condition,
        )
        .add_selection(radio_select)
    )

    base = getBaseChart(case_rolling_df, ["2020-01-01", "2020-12-31"])

    highlight_segment = (
        base.mark_line(strokeWidth=1)
        .add_selection(radio_select)
        .encode(
            color=change_color_condition,
            strokeDash=alt.condition(
                (alt.datum.segmentname == "To Democrat")
                | (alt.datum.segmentname == "To Republican"),
                alt.value([3, 5]),  # dashed line: 5 pixels  dash + 5 pixels space
                alt.value([0]),  # solid line
            ),
        )
    ).properties(height=200)

    return base, make_selector, highlight_segment, radio_select


########################################################################################
def getSelection():
    """
      THIS FUNCTION creates a selection element and uses it to 'conditionally' set a color
      for a categorical variable (segment).
      
      It return both the single selection as well as the Category for Color choice set based on selection.
      
      Functions called: None
      Called by: createChart()

      Input: None
      Returns: radio_select, change_color_condition

    """

    radio_select = alt.selection_multi(
        fields=["segmentname", "changecolor"], name="Segment",
    )

    change_color_condition = alt.condition(
        radio_select,
        alt.Color("changecolor:N", scale=None, legend=None),
        alt.value("lightgrey"),
    )

    return radio_select, change_color_condition


########################################################################################
def getBaseChart(case_rolling_df, date_range):
    """
      THIS FUNCTION creates a chart by encoding the date along the X positional axis and rolling mean
      along the Y positional axis. The mark (bar/line..) can be decided upon by the calling function.
      
      Functions called: None
      Called by: createChart()

      Input: Dataframe passed by calling function. The date column is expected to be 'date'
             date_range : a list containing min and max date to be considered for the time series eg["2020-01-01", "2020-12-31"]
      Returns: Base chart
      
    """

    # Set the date range for which the timeseries has to be graphed
    domain = date_range

    source = case_rolling_df[
        (case_rolling_df["date"] >= date_range[0])
        & (case_rolling_df["date"] <= date_range[1])
    ].copy()

    base = (
        alt.Chart(
            source,
            title={
                "text": [
                    "Year 2020 Timeseries of Confirmed Covid Cases Per 100K Residents (7 day rolling average)"
                ],
                "subtitle": [
                    "Click on legend colors to select segment(s) with given political affiliation",
                    "Shift + Click for multiple selections",
                ],
            },
        )
        .encode(
            x=alt.X(
                "date:T",
                timeUnit="yearmonthdate",
                scale=alt.Scale(domain=domain),
                axis=alt.Axis(
                    title=None,
                    # format=("%b %Y"),
                    labelAngle=0,
                    # tickCount=6
                ),
            ),
            y=alt.Y(
                "cases_avg_per_100k:Q",
                axis=alt.Axis(title="Cases (rolling mean per 100K)"),
            ),
        )
        #.properties(width=600, height=400)
    )
    return base


########################################################################################
def createTooltip(base, radio_select, case_rolling_df):
    """
      THIS FUNCTION uses the 'base' encoding chart and the selection captured to create four elements
      related to selection.
      
      Functions called: None
      Called by: Main code

      Input: base, radio_select
      Returns: selectors, rules, points, tooltip_text
    """

    # Create a selection that chooses the nearest point & selects based on x-value
    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=["date"], empty="none"
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    selectors = (
        alt.Chart(case_rolling_df)
        .mark_point()
        .encode(x="date:T", opacity=alt.value(0),)
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = (
        base.mark_point(size=5, dy=-10)
        .encode(opacity=alt.condition(nearest, alt.value(1), alt.value(0)))
        .transform_filter(radio_select)
    )

    # Draw text labels near the points, and highlight based on selection
    tooltip_text = (
        base.mark_text(align="left", dx=-60, dy=-15, fontSize=10, lineBreak="\n", )
            .encode(
            text=alt.condition(
                nearest, alt.Text("cases_avg_per_100k:Q", format=".2f"), alt.value(" "),
            ),
        )
        .transform_filter(radio_select)
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(case_rolling_df)
        .mark_rule(color="darkgrey", strokeWidth=2, strokeDash=[5, 4])
        .encode(x="date:T",)
        .transform_filter(nearest)
    )
    return selectors, rules, points, tooltip_text

