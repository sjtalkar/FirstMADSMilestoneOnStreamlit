import pandas as pd
import numpy as np
import altair as alt
import sys
from vega_datasets import data
from pathlib import Path

sys.path.append("../ETL")
from ETL.EtlBase import segment_color_dict, STAYED_REPUBLICAN, STAYED_DEMOCRAT
from ETL.EtlElection import *
from ETL.EtlVaccine import *
from .VizBase import *

# uses intermediate json files to speed things up
alt.data_transformers.enable("json")
alt.data_transformers.disable_max_rows()


# Formatting in Altair follows : https://github.com/d3/d3-format

########################################################################################
def createStateVaccinationChart():
    """
      THIS FUNCTION creates a chart relating vaccination data to 2020 presidential election winning party.

      Functions called: createStateVaccinationData()
      Called by: Main code

      Input: None
      Returns: Chart final_chart
    """

    source = createStateVaccinationData()
    max_value = source["Total population"].max()
    min_value = source["Total population"].min()
    source["y_center"] = (
        (source["Total population"] - min_value) / (max_value - min_value)
    ) + 0.5

    big_chart = (
        alt.Chart(
            source,
            title=[
                "Percentage of state’s population age 18 and older that has received",
                "at least one dose of a COVID-19 vaccine as of September 4th",
            ],
        )
        .mark_point(filled=True, opacity=1,)
        .encode(
            x=alt.X(
                "Percent with one dose:Q",
                axis=alt.Axis(
                    title=None,
                    format="%",
                    orient="top",
                    values=[0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
                ),
                scale=alt.Scale(domain=[0.30, 0.80]),
            ),
            y=alt.Y("y_center:Q", axis=None),
            color=alt.Color(
                "party_simplified:N",
                scale=alt.Scale(
                    domain=["DEMOCRAT", "REPUBLICAN"], range=["#030D97", "#970D03"]
                ),
            ),
            tooltip=[alt.Tooltip("state_po:N", title="State: ")],
            size=alt.Size(
                "Total population:Q", scale=alt.Scale(range=[100, 3000]), legend=None
            ),
        )
        .properties(width=500, height=200)
    )

    big_chart_line = (
        alt.Chart(pd.DataFrame({"x": [0.5]}))
        .mark_rule(strokeDash=[10, 10])
        .encode(x="x")
    )

    big_chart_text = (
        alt.Chart(source)
        .mark_text(
            align="left",
            baseline="middle",
            dx=-3,
            fontSize=8,
            fontWeight="bold",
            color="white",
        )
        .encode(
            x=alt.X("Percent with one dose:Q"), y=alt.Y("y_center:Q"), text="state_po"
        )
    )

    small_chart = (
        alt.Chart(source, title="Percentage of people vaccinated wih one dose")
        .mark_point(filled=True, opacity=1)
        .encode(
            x=alt.X(
                "Percent with one dose:Q",
                axis=alt.Axis(
                    format="%", orient="top", values=[0, 0.2, 0.4, 0.6, 0.8, 1]
                ),
                scale=alt.Scale(domain=[0, 1]),
                title=None,
            ),
            y=alt.Y("y_center:Q", axis=None),
            color=alt.Color(
                "party_simplified:N",
                legend=alt.Legend(title="Presidential election choice"),
                scale=alt.Scale(
                    domain=["DEMOCRAT", "REPUBLICAN"], range=["#030D97", "#970D03"]
                ),
            ),
            size=alt.Size(
                "Total population:Q", scale=alt.Scale(range=[50, 100]), legend=None
            ),
        )
        .properties(width=400, height=50)
    )

    # Add a rectangle around the data
    box = pd.DataFrame({"x1": [0.3], "x2": [0.8], "y1": [0], "y2": [1.5]})

    rect = (
        alt.Chart(box)
        .mark_rect(fill="white", stroke="black", opacity=0.3)
        .encode(alt.X("x1",), alt.Y("y1",), x2="x2", y2="y2")
    )

    full_x_chart = small_chart + rect

    final_chart = (
        ((big_chart + big_chart_text + big_chart_line) & full_x_chart)
        .resolve_scale(x="independent", y="independent", size="independent")
        .configure_title(fontSize=15)
        .configure_axis(labelColor="#a9a9a9")
    )

    return final_chart


#######################################################################################
def createDailyInteractiveVaccinationChart(df: pd.DataFrame() = None):
    """
        THIS FUNCTION creates an interactive chart. A slider is provided that starts from the first day any resident
        received vaccination and can be moved up until September 4th, 2021.
        The chart shows the percentage of 18 years and above population of a state that as received at least
        one vaccine shot. Since some of the vaccines such as J&J require only one shot, this percentage shows the receptivity
        of the population to a vaccine shot.

        The size of the state bubble is proportional to the population of the state.

    """
    if df is None:
        df = getDailyVaccinationPercentData().copy()

    max_value = df["Total population"].max()
    min_value = df["Total population"].min()

    if (max_value - min_value) == 0:
        df["y_center"] = 0.5
    else:
        df["y_center"] = (
            (df["Total population"] - min_value) / (max_value - min_value)
        ) + 0.5

    # Create Slider
    min_day_num = df.day_num.min()
    max_day_num = df.day_num.max()
    slider = alt.binding_range(
        min=min_day_num,
        max=max_day_num,
        step=1,
        name="Number of days since first vaccination: ",
    )
    slider_selection = alt.selection_single(
        fields=["day_num"], bind=slider, name="day_num", init={"day_num": max_day_num}
    )

    base = (
        alt.Chart(
            df,
            title=[
                "Percentage of state’s population age 18 and older that has received",
                "at least one dose of a COVID-19 vaccine as of September 4th, 2021",
            ],
        )
        .add_selection(slider_selection)
        .transform_filter(slider_selection)
    )

    big_chart_new = base.mark_point().encode(
        x=alt.X(
            "Percent with one dose:Q",
            axis=alt.Axis(
                title=None,
                format="%",
                orient="top",
                values=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            ),
            scale=alt.Scale(domain=[0, 1.0]),
        ),
        y=alt.Y("y_center:Q", axis=None),
        color=alt.Color(
            "party_simplified:N",
            legend=alt.Legend(title="Presidential election choice:"),
            scale=alt.Scale(
                domain=["DEMOCRAT", "REPUBLICAN"], range=["#030D97", "#970D03"],
            ),
        ),
    )

    big_chart = (
        base.mark_point(filled=True, opacity=1,)
        .encode(
            x=alt.X(
                "Percent with one dose:Q",
                axis=alt.Axis(
                    title=None,
                    format="%",
                    orient="top",
                    values=[0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
                ),
                scale=alt.Scale(domain=[0, 1.0]),
            ),
            y=alt.Y("y_center:Q", axis=None),
            color=alt.Color(
                "party_simplified:N",
                legend=alt.Legend(title="Presidential election choice:"),
                scale=alt.Scale(
                    domain=["DEMOCRAT", "REPUBLICAN"], range=["#030D97", "#970D03"],
                ),
            ),
            tooltip=[
                alt.Tooltip("state_po:N", title="State: "),
                alt.Tooltip(
                    "Percent with one dose:Q",
                    title="Percent with one dose:",
                    format=".2%",
                ),
                alt.Tooltip(
                    "Total population:Q", title="Total state population:", format=",.2r"
                ),
            ],
            size=alt.Size(
                "Total population:Q", scale=alt.Scale(range=[150, 3000]), legend=None
            ),
        )
        .properties(width=700, height=450)
    )

    big_chart_line = (
        alt.Chart(pd.DataFrame({"x": [0.5]}))
        .mark_rule(strokeDash=[10, 10])
        .encode(x="x")
    )

    big_chart_text = (
        alt.Chart(df)
        .mark_text(
            align="left",
            baseline="middle",
            dx=-3,
            fontSize=8,
            fontWeight="bold",
            color="white",
        )
        .encode(
            x=alt.X("Percent with one dose:Q"), y=alt.Y("y_center:Q"), text="state_po"
        )
        .transform_filter(slider_selection)
    )

    final_chart = (big_chart + big_chart_text).configure_title(
        align="left", anchor="start"
    )

    return final_chart


#########################################################################################
def plotStateVaccinePct(df, date_in):
    """
        This function generates a US state choropleth map with color scale tuned
        by the number of vaccinations at the latest time in the data.

        Input: Dataframe with State fips STATEFP, Percent with one dose and STNAME
        Output: The choropleth and the click select for each state
    """
    from vega_datasets import data

    source = df[df["date"] == date_in].copy()
    us_states = alt.topo_feature(data.us_10m.url, "states")

    click = alt.selection_multi(fields=["STATEFP"], init=[{"STATEFP": 1}])

    chart = (
        alt.Chart(
            us_states,
            title={
                "text": [
                    "Tracking Covid Case Resurgence After Detection of First Delta variant in the US.",
                    "In Relation to Vaccination Adoption Rates in the States",
                ],
                "subtitle": [
                    "State Level Vaccination Percent Per Population (one dose) as of September 4th, 2021",
                    "Hover and click on State for Covid Case Timeseries",
                ],
            },
        )
        .mark_geoshape(stroke="lightgrey")
        .encode(
            color=alt.condition(
                click,
                alt.value("#00000F"),
                alt.Color(
                    "Percent with one dose:Q", scale=alt.Scale(scheme="lighttealblue"),
                ),
            ),
            tooltip=[
                alt.Tooltip("STNAME:N", title="State name: "),
                alt.Tooltip(
                    "Percent with one dose:Q", title="Population Pct with one shot: "
                ),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(
                source, "STATEFP", ["Percent with one dose", "STATEFP", "STNAME"]
            ),
        )
        .add_selection(click)  ## Make sure you have added the selection here
        .project(type="albersUsa")
        .properties(width=500, height=300)
    )

    return chart, click


#########################################################################################


def createCombinedVaccinationAndDeltaVariantTrend(
    state_vaccine_df: pd.DataFrame() = None,
    us_case_rolling_df: pd.DataFrame() = None,
    state_case_rolling_df: pd.DataFrame() = None,
    state_election_df: pd.DataFrame() = None,
):
    """
                This functions creates a Delta variant timeseries.
                A dropdown selector is created to select  a state but the timeseries can also display the
                state selected in a choropleth map displayed above it since the click selector of the choropleth map
                is added to the timeseries chart.

                Tootltips are created to display the number of cases all through the timeseries

                Input: None
                Output:
                vaccine_chart - The choropleth of US geography colored by vaccination population pct.
                us_timeseries - Timeseries of average US covid cases after emergence of Delta variant
                state_cases_delta_chart - Timeseries of State covid cases after emergence of Delta variant
                state_selectors (Hidden selectors for display of tooltip)
                rules - Tooltip rule line
                tooltip_text1 (Tooltip for state 1)
                tooltip_text2 (Tooltip for state 2)
                tooltip_text3 (Tooltip for US timeline)
                points (Points to display the tootip text)
        """

    if (
        (state_vaccine_df is None)
        or (us_case_rolling_df is None)
        or (state_case_rolling_df is None)
    ):
        # Retrieve the data
        (
            state_vaccine_df,
            us_case_rolling_df,
            state_case_rolling_df,
        ) = getStateVaccinationDataWithAPI()

    if state_election_df is None:
        state_election_df = getStateLevelElectionData2020()

    # Create the vaccination Choropleth/Geo chart
    vaccine_chart, click = plotStateVaccinePct(
        state_vaccine_df, state_vaccine_df.date.max()
    )

    state_case_rolling_df = state_case_rolling_df.merge(
        state_election_df[["state_fips", "party_simplified"]],
        how="left",
        left_on="STATEFP",
        right_on="state_fips",
    )
    state_case_rolling_df = state_case_rolling_df[
        ~state_case_rolling_df["party_simplified"].isnull()
    ]
    state_case_rolling_df["party_simplified"] = np.where(
        state_case_rolling_df["party_simplified"] == "REPUBLICAN",
        "STAYED_REPUBLICAN",
        "STAYED_DEMOCRAT",
    )
    state_case_rolling_df["party_simplified_color"] = state_case_rolling_df[
        "party_simplified"
    ].map(segment_color_dict)

    # Create a baseline US covid cases chart
    us_base = getBaseChart(
        us_case_rolling_df, [state_vaccine_df.date.min(), state_vaccine_df.date.max()]
    )
    us_timeseries = us_base.mark_line(
        strokeDash=[3, 6], strokeWidth=1, color="black"
    ).encode(tooltip=[alt.Tooltip("geoid:N", title="US Country Average Cases:")])

    # Create a "mean" cases timeseries chart of two segments - Stayed Democrat and Stayed Republican
    party_cases_timeseries_df = (
        state_case_rolling_df.groupby(
            ["date", "party_simplified", "party_simplified_color"]
        )
        .agg(
            cases_avg_per_100k=("cases_avg_per_100k", "mean"),
            deaths_avg_per_100k=("deaths_avg_per_100k", "mean"),
        )
        .reset_index()
    )

    # Democrat Mean
    stayed_democrat_base = getBaseChart(
        party_cases_timeseries_df[
            party_cases_timeseries_df["party_simplified"] == "STAYED_DEMOCRAT"
        ],
        [state_vaccine_df.date.min(), state_vaccine_df.date.max()],
    )

    stayed_democrat_timeseries = stayed_democrat_base.mark_line(
        strokeDash=[2, 6], strokeWidth=1, color="blue"
    ).encode(
        tooltip=[
            alt.Tooltip(
                "cases_avg_per_100k:Q", title="Stayed Democrat State Average Cases:"
            ),
        ]
    )

    # Republican Mean
    stayed_republican_base = getBaseChart(
        party_cases_timeseries_df[
            party_cases_timeseries_df["party_simplified"] == "STAYED_REPUBLICAN"
        ],
        [state_vaccine_df.date.min(), state_vaccine_df.date.max()],
    )

    stayed_republican_timeseries = stayed_republican_base.mark_line(
        strokeDash=[2, 4], strokeWidth=1, color="red"
    ).encode(
        tooltip=[
            alt.Tooltip(
                "cases_avg_per_100k:Q", title="Stayed Republican State Average Cases:"
            ),
        ]
    )

    # Create the dropdown selector for state names
    input_dropdown = alt.binding_select(
        options=[None] + state_case_rolling_df["state"].unique().tolist(),
        labels=["None"] + state_case_rolling_df["state"].unique().tolist(),
        name="State: ",
    )
    dropdown_selection = alt.selection_single(
        fields=["state"], bind=input_dropdown, name="State: ", init={"state": "None"}
    )

    # Each timeline will be colored by state affiliation
    state_color_tuples = list(
        state_case_rolling_df.groupby(["state", "party_simplified_color"]).groups.keys()
    )
    state_domain, color_range = zip(*state_color_tuples)

    line_base = alt.Chart(
        state_case_rolling_df,
        title="Covid cases timeseries after emergence of Delta variant in the US in March 2021",
    )

    # Create the line chart base to plot tooltip points
    just_line_state_cases_delta = (
        line_base.mark_line()
        .encode(
            x=alt.X("date:T"),
            y=alt.Y("cases_avg_per_100k:Q"),
            detail="party_simplified",
            # color=alt.Color("changecolor:N", scale=None),
            color=alt.condition(
                # dropdown_selection | click,
                click,
                alt.Color(
                    "state:N",
                    legend=None,
                    scale=alt.Scale(domain=state_domain, range=color_range),
                ),
                alt.value("lightgray"),
            ),
            opacity=alt.condition(
                # dropdown_selection | click, alt.value(1), alt.value(0.2)
                click,
                alt.value(1),
                alt.value(0.2),
            ),
        )
        .properties(height=200, width=500)
    )

    ##############################################################################################
    delta_highlight_df = pd.DataFrame(
        {"start_date": ["03-01-2021"], "stop_date": ["03-31-2021"]}
    )
    delta_highlight_df.start_date = pd.to_datetime(delta_highlight_df.start_date)
    delta_highlight_df.stop_date = pd.to_datetime(delta_highlight_df.stop_date)

    delta_rect_area = (
        alt.Chart(delta_highlight_df.reset_index())
        .mark_rect(opacity=0.2)
        .encode(
            x="start_date",
            x2="stop_date",
            y=alt.value(0),  # pixels from top
            y2=alt.value(200),  # pixels from top
            color=alt.value("lightgrey"),
        )
    )

    ##############################################################################################
    highlight_df = pd.DataFrame(
        {"start_date": ["07-01-2021"], "stop_date": ["07-22-2021"]}
    )
    highlight_df.start_date = pd.to_datetime(highlight_df.start_date)
    highlight_df.stop_date = pd.to_datetime(highlight_df.stop_date)

    rect_area = (
        alt.Chart(highlight_df.reset_index())
        .mark_rect(opacity=0.2)
        .encode(
            x="start_date",
            x2="stop_date",
            y=alt.value(0),  # pixels from top
            y2=alt.value(200),  # pixels from top
            color=alt.value("lightgrey"),
        )
    )

    ##############################################################################################
    ## This is the plot of the timeseries with selections added
    state_cases_delta_chart = (
        line_base.mark_line(strokeWidth=1,).encode(
            x=alt.X("date:T"),
            y=alt.Y("cases_avg_per_100k:Q"),
            detail="party_simplified",
            color=alt.condition(
                # dropdown_selection | click,
                click,
                alt.Color(
                    "state:N",
                    legend=None,
                    scale=alt.Scale(domain=state_domain, range=color_range),
                ),
                alt.value("lightgray"),
            ),
            opacity=alt.condition(
                # dropdown_selection | click,
                click,
                alt.value(1),
                alt.value(0.2),
            ),
        )
        # .properties(height=300, width=800)
        # .add_selection(dropdown_selection)
        .add_selection(click)
    )

    ####################################################################################################
    ## CREATE THE TOOLTIP COMPONENTS
    ####################################################################################################

    # Create a selection that chooses the nearest point & selects based on x-value
    base = line_base

    nearest = alt.selection(
        type="single", nearest=True, on="mouseover", fields=["date"], empty="none"
    )

    # Transparent selectors across the chart. This is what tells us
    # the x-value of the cursor
    state_selectors = (
        alt.Chart(state_case_rolling_df)
        .mark_point()
        .encode(x="date:T", opacity=alt.value(0),)
        .add_selection(nearest)
    )

    # Draw points on the line, and highlight based on selection
    points = just_line_state_cases_delta.mark_point(size=10, dy=-10).encode(
        opacity=alt.condition(nearest, alt.value(1), alt.value(0))
    )
    # .transform_filter(dropdown_selection)

    # Draw text labels near the points, and highlight based on selection
    tooltip_text1 = (
        just_line_state_cases_delta.mark_text(
            align="right", dx=-90, dy=-15, fontSize=8, lineBreak="\n",
        )
        .encode(text=alt.condition(nearest, alt.Text("label:N"), alt.value(" "),))
        .transform_filter(dropdown_selection)
        .transform_calculate(
            label='datum.state + " state :" +  format(datum.cases_avg_per_100k,".2f") '
        )
    )

    # Draw text labels near the points, and highlight based on selection
    tooltip_text2 = (
        just_line_state_cases_delta.mark_text(
            align="left", dx=-100, dy=-15, fontSize=8, lineBreak="\n",
        )
        .encode(text=alt.condition(nearest, alt.Text("label:N"), alt.value(" "),),)
        .transform_filter(click)
        .transform_calculate(
            label='datum.state + " state :" +  format(datum.cases_avg_per_100k,".2f") '
        )
    )

    # US Time series Draw text labels near the points, and highlight based on selection
    tooltip_text3 = (
        us_timeseries.mark_text(
            align="left", dx=-100, dy=-15, fontSize=8, lineBreak="\n",
        )
        .encode(text=alt.condition(nearest, alt.Text("label:N"), alt.value(" "),),)
        .transform_calculate(label='"US mean :" +  datum.cases_avg_per_100k')
    )

    # Stayed Democrat Time series Draw text labels near the points, and highlight based on selection
    tooltip_text4 = (
        stayed_democrat_timeseries.mark_text(
            align="left", dx=-100, dy=-30, fontSize=8, color="#030D97", lineBreak="\n",
        )
        .encode(text=alt.condition(nearest, alt.Text("label:N"), alt.value(" "),))
        .transform_calculate(
            label='"Democrat mean (---):" +  format(datum.cases_avg_per_100k,".2f")'
        )
    )

    tooltip_text5 = (
        stayed_republican_timeseries.mark_text(
            align="left", dx=-100, dy=-60, fontSize=8, color="#970D03", lineBreak="\n",
        )
        .encode(text=alt.condition(nearest, alt.Text("label:N"), alt.value(" "),))
        .transform_calculate(
            label='"Republican mean (---):" +  format(datum.cases_avg_per_100k,".2f")'
        )
    )

    # Draw a rule at the location of the selection
    rules = (
        alt.Chart(state_case_rolling_df)
        .mark_rule(color="darkgrey", strokeWidth=2, strokeDash=[5, 4])
        .encode(x="date:T",)
        .transform_filter(nearest)
    )

    return (
        vaccine_chart,
        us_timeseries,
        stayed_democrat_timeseries,
        stayed_republican_timeseries,
        state_cases_delta_chart,
        state_selectors,
        rules,
        tooltip_text2,
        tooltip_text3,
        tooltip_text4,
        tooltip_text5,
        points,
        rect_area,
        delta_rect_area,
        just_line_state_cases_delta,
    )


################################################################################

import altair as alt
from vega_datasets import data


def altairTestFunction():
    source = data.population.url

    slider = alt.binding_range(min=1850, max=2000, step=10)
    select_year = alt.selection_single(
        name="year", fields=["year"], bind=slider, init={"year": 2000}
    )

    base = (
        alt.Chart(source)
        .add_selection(select_year)
        .transform_filter(select_year)
        .transform_calculate(gender=alt.expr.if_(alt.datum.sex == 1, "Male", "Female"))
        .properties(width=250)
    )

    color_scale = alt.Scale(domain=["Male", "Female"], range=["#1f77b4", "#e377c2"])

    left = (
        base.transform_filter(alt.datum.gender == "Female")
        .encode(
            y=alt.Y("age:O", axis=None),
            x=alt.X(
                "sum(people):Q", title="population", sort=alt.SortOrder("descending")
            ),
            color=alt.Color("gender:N", scale=color_scale, legend=None),
        )
        .mark_bar()
        .properties(title="Female")
    )

    middle = (
        base.encode(y=alt.Y("age:O", axis=None), text=alt.Text("age:Q"),)
        .mark_text()
        .properties(width=20)
    )

    right = (
        base.transform_filter(alt.datum.gender == "Male")
        .encode(
            y=alt.Y("age:O", axis=None),
            x=alt.X("sum(people):Q", title="population"),
            color=alt.Color("gender:N", scale=color_scale, legend=None),
        )
        .mark_bar()
        .properties(title="Male")
    )

    altair_test_chart = alt.concat(left, middle, right, spacing=5)
    return altair_test_chart
