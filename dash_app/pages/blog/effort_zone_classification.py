from __future__ import annotations

import dash
from dash import dcc, html

from utils.config import (
    LT_HR, LT_POWER, LT_PACE
)

dash.register_page(
    __name__,
    path="/blog/effort_zone_classification",
    name="Effort Zone Classification",
)

LT_VALUES = [LT_HR, LT_POWER, str(LT_PACE)]

HIKING_HR_PERCENT_MAX = 0.75
EASY_HR_PERCENT_MAX = 0.85
HIKING_HR_ZONE_MAX = round(LT_HR * HIKING_HR_PERCENT_MAX, 1)
EASY_HR_ZONE_MAX = round(LT_HR * EASY_HR_PERCENT_MAX, 1)
MODERATE_HR_ZONE_MAX = round(LT_HR * 1.0, 1)

HIKING_POWER_PERCENT_MAX = 0.50
EASY_POWER_PERCENT_MAX = 0.75
HIKING_POWER_ZONE_MAX = round(LT_POWER * HIKING_POWER_PERCENT_MAX, 1)
EASY_POWER_ZONE_MAX = round(LT_POWER * EASY_POWER_PERCENT_MAX, 1)
MODERATE_POWER_ZONE_MAX = round(LT_POWER * 1.0, 1)

ZONE_ROWS = [
    ("Hiking", f"< {HIKING_HR_ZONE_MAX}", f"< {HIKING_POWER_ZONE_MAX}", "15:00+"),
    ("Easy", f"{HIKING_HR_ZONE_MAX}-{EASY_HR_ZONE_MAX}", f"{HIKING_POWER_ZONE_MAX}–{EASY_POWER_ZONE_MAX}",  "9:30-15:00"),
    ("Moderate", f"{EASY_HR_ZONE_MAX}–{LT_HR}", f"{EASY_POWER_ZONE_MAX}–{LT_POWER}", "7:33–9:30"),
    ("Hard", f"{LT_HR}+", f"{LT_POWER}+", f"< 7:33"),
]
ZONE_VALUE_COUNTS = [
    # Zone, % of time HR, % of time Power, Hours, n Activities
    ("Hiking",   "15.7%", "16.9%", "33.4", "22"),
    ("Easy",     "30.3%", "40.4%", "64.6", "54"),
    ("Moderate", "49.2%", "38.2%", "104.9", "89"),
    ("Hard",      "4.8%",  "4.4%", "10.1", "0"),
]

layout = html.Div(
    style={"maxWidth": "75%", "padding": "0 1.5rem"},
    children=[
        html.H1("Defining Running Effort Zones with Lactate Threshold"),
        html.P([
            "Jupyter notebook with code and analysis: ",
            html.A(
                "lactate_threshold_based_effort_zones.ipynb",
                href="https://github.com/AntonioPelayo/my-run-forecast/blob/main/notebooks/lactate_threshold_based_effort_zones.ipynb"
            )
        ]),
        html.P(
            """
            Using my running data over the past year, tracked using my Garmin
            watch, I wanted to see if I could identify different effort zones
            (hiking, easy, moderate, hard) based on real physiological signals
            like heart rate and power.
            """
        ),
        html.P(
            """
            As a starting point for zone labels, I used my watch's predicted
            lactate threshold values:
            """
        ),
        # LT Values
        html.Table(
            style={"borderCollapse": "collapse", "margin": "1rem 0"},
            children=[
                html.Thead(html.Tr([html.Th(
                    col,
                    style={
                        "textAlign": "left",
                        "paddingRight": "2rem",
                    }
                ) for col in (
                    "Heart Rate (BPM)", "Power Range (Watts)", "Pace (min/mile)"
                )])),
                html.Tbody([html.Tr([
                    html.Td(cell, style={"paddingRight": "2rem"})
                    for cell in LT_VALUES
                ])])
            ]
        ),
        html.P(
            """
            Lactatce threshold in running is a physiological marker that
            corresponds to an effort level above aerobic capacity and when
            fast-twitch muscle fibers begin to fatigue.
            To me, this means that an "easy" zone is below the LT, my
            "moderate" zone is around the LT, and the "hard" zone is above LT.
            """
        ),
        html.P(
            """
            In my training, I have also found that about 165 BPM is where I
            personally need to transition from nose-breathing to mouth-breathing,
            which is another physiological signal of increased effort that I
            use to decide when to start hiking on steep terrain. So we'll
            define my Easy zone as just below that, about 85% of my LT heart
            rate, and the Hiking zone as below 75% of my LT heart rate.
            """
        ),
        html.P(
            """
            My heart rate percentages skew a bit higher than for power, so for
            power, I will use 50% of LT as the hiking zone max and 75% of LT as
            the easy zone max.
            """
        ),
        html.P(
            """
            Using those insights, I define four effort zones below:
            """
        ),
        # LT based zones
        html.Table(
            style={"borderCollapse": "collapse", "margin": "1rem 0"},
            children=[
                html.Thead(html.Tr([html.Th(
                    col,
                    style={
                        "textAlign": "left",
                        "paddingRight": "2rem",
                    }
                ) for col in (
                    "Zone", "Heart Rate Range (BPM)", "Power Range (Watts)",
                    "Pace Range (min/mile)"
                )])),
                html.Tbody([html.Tr([
                    html.Td(cell, style={"paddingRight": "2rem"})
                    for cell in row
                ]) for row in ZONE_ROWS]),
            ],
        ),
        html.P(
            """
            Below is a visualization of the zones overlaid onto a year's worth
            of activity data.
            """
        ),
        html.Img(
            src="/assets/plots/effort_zone_histograms.png",
            style={"width": "100%", "height": "auto", "marginBottom": "1rem"}
        ),
        html.P(
            """
            After defining the zones, I applied the heuristics to classify
            every moment of each activity to see how much time is spent in each
            zone.

            The table below summarizes the percentage of time spent in each
            zone across my activities, as well as the total hours spent in
            each zone.
            """
        ),
        html.Table(
            style={"borderCollapse": "collapse", "margin": "1rem 0"},
            children=[
                html.Thead(html.Tr([html.Th(
                    col,
                    style={
                        "textAlign": "left",
                        "paddingRight": "2rem",
                    }
                ) for col in (
                    "Zone", "% Time Heart Rate", "% Time Power",
                    "Total Hours (HR)", "Activities Avg'd in Zone"
                )])),
                html.Tbody([html.Tr([
                    html.Td(cell, style={"paddingRight": "2rem"})
                    for cell in row
                ]) for row in ZONE_VALUE_COUNTS]),
            ],
        ),
        html.P(
            """
            Something to note is that 1 second in the hard power zone is not
            equivalent to 1 second in the hard heart rate zone.
            Power is a more immediate signal of effort, while heart rate lags
            behind changes in effort, and can remain elevated based on fitness
            level and fatigue.
            """
        ),
        html.P(
            """
            Overall, I belive this is a good reflection of my training, where I
            spend most of my time in endurance efforts around the moderate
            zone, recovering into the easy zone, and rarely doing speed
            workouts that push me into the hard effort zones.
            """
        ),
        html.P(
            """
            Going forward, I plan to use these zones with my GPX route
            completion time model by including a new effort feature to output
            multiple effort predictions.
            """
        )
    ],
)