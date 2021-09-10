from pathlib import Path

DataFolder = Path("../DataForPresidentialElectionsAndCovid/")

## Color global variables
TO_OTHER = "#556B2F"
TO_DEMOCRAT = "#11A3D6"
TO_REPUBLICAN = "#AB5A68"
STAYED_DEMOCRAT = "#030D97"
STAYED_REPUBLICAN = "#970D03"
STAYED_OTHER = "#B4D3B2"

segment_color_dict = {
    "TO_OTHER": TO_OTHER,
    "TO_DEMOCRAT": TO_DEMOCRAT,
    "TO_REPUBLICAN": TO_REPUBLICAN,
    "STAYED_DEMOCRAT": STAYED_DEMOCRAT,
    "STAYED_REPUBLICAN": STAYED_REPUBLICAN,
    "STAYED_OTHER": STAYED_OTHER,
}

color_segment_dict = {
    TO_OTHER: "To other",
    TO_DEMOCRAT: "To Democrat",
    TO_REPUBLICAN: "To Republican",
    STAYED_DEMOCRAT: "Stayed Democrat",
    STAYED_REPUBLICAN: "Stayed Republican",
    STAYED_OTHER: "Stayed Other",
}

US_STATE_ABBRV = {
    "Alabama": "AL",
    "Alaska": "AK",
    "American Samoa": "AS",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "District of Columbia": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Guam": "GU",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Northern Mariana Islands": "MP",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Puerto Rico": "PR",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virgin Islands": "VI",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
}