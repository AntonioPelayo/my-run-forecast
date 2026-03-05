import dash
import pandas as pd
import plotly.express as px
from dash import dcc, html
from functools import lru_cache

from utils.config import M_TO_MI_MULTIPLIER, M_TO_FT_MULTIPLIER

dash.register_page(
    __name__,
    path="/blog/training_schedule_and_habits",
    name="Training Schedule and Habits",
)


# -----------------------------------------------------------------------------
# Data loading
# -----------------------------------------------------------------------------
@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    return pd.read_csv("./data/run_summaries.csv")


def add_additional_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Dates
    df['activity_date'] = pd.to_datetime(df['activity_date'], utc=True)
    df['activity_date_pst'] = df['activity_date'].dt.tz_convert('US/Pacific')
    df['start_hour_pst'] = df['activity_date_pst'].dt.hour
    df['elapsed_time_hours'] = df['elapsed_seconds'] / 3600

    # Distance and elevation conversions
    df['distance_mi'] = df['distance'] * M_TO_MI_MULTIPLIER
    df['elevation_gain_ft'] = df['cum_elevation_gain'] * M_TO_FT_MULTIPLIER
    return df


def make_fig_start_hour(df: pd.DataFrame) -> px.scatter:
    agg = df.groupby('start_hour_pst').agg(
        total_runs=pd.NamedAgg(column='activity_path', aggfunc='count'),
        total_distance_mi=pd.NamedAgg(column='distance_mi', aggfunc='sum'),
        total_elapsed_time_hours=pd.NamedAgg(column='elapsed_time_hours', aggfunc='sum'),
        avg_distance_mi=pd.NamedAgg(column='distance_mi', aggfunc='mean'),
        avg_elapsed_time_hours=pd.NamedAgg(column='elapsed_time_hours', aggfunc='mean'),
    )
    agg[[
        'avg_distance_mi', 'avg_elapsed_time_hours', 'total_distance_mi',
        'total_elapsed_time_hours'
    ]] = agg[[
        'avg_distance_mi', 'avg_elapsed_time_hours', 'total_distance_mi',
        'total_elapsed_time_hours'
    ]].round(2)
    agg.reset_index(inplace=True)

    fig = px.scatter(
        agg, x='start_hour_pst', y='total_runs',
        range_x=[-0.5, 23.5],
        size='avg_distance_mi', color='avg_distance_mi',
        hover_data=['avg_elapsed_time_hours', 'total_distance_mi', 'total_elapsed_time_hours'],
        title="Total Runs by Start Hour (Size = Avg Distance in Miles)",
        width=800, height=400
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


def make_fig_day_of_week(df: pd.DataFrame) -> px.scatter:
    df['day_of_week'] = df['activity_date_pst'].dt.day_name()

    DOW_df = df.groupby('day_of_week').agg(
        total_runs=pd.NamedAgg(column='activity_path', aggfunc='count'),
        total_distance_mi=pd.NamedAgg(column='distance_mi', aggfunc='sum'),
        total_elapsed_time_hours=pd.NamedAgg(column='elapsed_time_hours', aggfunc='sum'),
        avg_distance_mi=pd.NamedAgg(column='distance_mi', aggfunc='mean'),
        avg_elapsed_time_hours=pd.NamedAgg(column='elapsed_time_hours', aggfunc='mean'),
    )

    DOW_df[[
        'avg_distance_mi', 'avg_elapsed_time_hours', 'total_distance_mi',
        'total_elapsed_time_hours'
    ]] = DOW_df[[
        'avg_distance_mi', 'avg_elapsed_time_hours', 'total_distance_mi',
        'total_elapsed_time_hours'
    ]].round(2)
    DOW_df.reset_index(inplace=True)

    # Sort days of week in natural order
    day_order = [
        'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
        'Saturday', 'Sunday'
    ]
    DOW_df['day_of_week'] = pd.Categorical(
        DOW_df['day_of_week'], categories=day_order, ordered=True
    )
    DOW_df.sort_values('day_of_week', inplace=True)
    fig = px.scatter(
        DOW_df, x='day_of_week', y='total_runs',
        size='avg_distance_mi', color='avg_distance_mi',
        hover_data=['avg_elapsed_time_hours', 'total_distance_mi', 'total_elapsed_time_hours'],
        title="Total Runs by Day of Week (Size = Avg Distance in Miles)",
        width=800, height=400
    )
    fig.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    return fig


def monthly_agg(df, years):
    d = df[df['activity_date_pst'].dt.year.isin(years)].copy()
    d['month'] = d['activity_date_pst'].dt.tz_localize(None).dt.to_period('M').dt.to_timestamp()

    out = (
        d.groupby('month', as_index=False).agg(
            total_runs=('activity_path', 'count'),
            total_distance_mi=('distance_mi', 'sum'),
            total_elevation_gain_ft=('elevation_gain_ft', 'sum'),
            avg_distance_mi=('distance_mi', 'mean'),
            avg_elapsed_time_hours=('elapsed_time_hours', 'mean'),
        )
    )
    out[[
        'total_distance_mi', 'total_elevation_gain_ft', 'avg_distance_mi',
        'avg_elapsed_time_hours'
    ]] = out[[
        'total_distance_mi', 'total_elevation_gain_ft', 'avg_distance_mi',
        'avg_elapsed_time_hours'
    ]].round(2)
    out['month_lbl'] = out['month'].dt.strftime('%B %Y')
    return out


def make_fig_monthly_agg_new(df: pd.DataFrame) -> px.scatter:
    m = monthly_agg(df, [2025, 2026])
    fig = px.scatter(
        m, x='month_lbl', y='total_runs',
        size='avg_distance_mi', color='avg_distance_mi',
        hover_data=['avg_elapsed_time_hours'],
        title="Total Runs by Month (Size = Avg Distance in Miles)",
        width=800, height=400
    )

    fig.add_traces(
        px.line(
            m, x='month_lbl', y='total_distance_mi', markers=True,
            hover_data=['total_elevation_gain_ft'],
        ).update_traces(
            yaxis='y2', name='Total Distance (mi)',
            line=dict(color='black', width=2, dash='dash'),
            marker=dict(color='black', size=6)
        ).data
    )

    fig.update_layout(
        xaxis_title="Month", yaxis_title="Total Runs",
        xaxis_tickangle=-45,
        yaxis2=dict(
            title="Total Distance (mi)",
            overlaying='y',
            side='right',
            showgrid=False
        ),
        margin=dict(l=0, r=210, t=40, b=0),
        coloraxis_colorbar=dict(x=1.15, xanchor='left')
    )
    return fig


def build_figures():
    raw_df = load_data()
    df = add_additional_columns(raw_df)
    df = df[df['activity_date_pst'].dt.year > 2024].copy()
    return {
        "start_hour": make_fig_start_hour(df),
        "day_of_week": make_fig_day_of_week(df),
        "monthly_agg": make_fig_monthly_agg_new(df),
    }

# -----------------------------------------------------------------------------
# Page layout
# -----------------------------------------------------------------------------
layout = html.Div(
    children=[
        html.H1("My Training Schedule and Habits"),
        html.P(
            """
            With a year of fine-detail running data, I'm curious to see about
            what time of day I go out for a run, and if there is a relationship
            with time of day and distance/time.
            """
        ),
        dcc.Graph(figure=build_figures()["start_hour"]),
        html.P(
            """
            When first getting started with running, I would go out to group
            runs for accountability and autonomy when it comes to route and
            workout structure.
            These group runs were typically in the evening, after work.
            This could account for the large number of runs starting at 6pm!
            """
        ),
        html.P(
            """
            Another natural habit to note is that the longer runs tend to be in
            the morning (8am) while the evening has runs typically under 6
            miles.
            The "lunch run" phenomenon is also greatly represented with an
            uptick in runs starting around noon (after I finish my coffee), and
            needing to be back at work around 1pm to finish tasks for the day.
            """
        ),
        dcc.Graph(figure=build_figures()["day_of_week"]),
        html.P(
            """
            I was surprised at my first glance at my runs by day of the week, I
            didn't expect to see a smooth taper in runs from Monday to Sunday.
            Mondays do seem like a natural day to sete a routine for the week,
            while the increase in Friday runs can be accounted for by the
            feeling of completing the work week and looking forward to getting
            out on the weekend.
            """
        ),
        html.P(
            """
            One personal trend I did know was that weekends are a hit or miss
            when it comes to my training, due to social plans or enjoying rest
            days.
            Saturdays are my sleep in and relax day, while Sundays could be
            seen as my "long run day" to make up for any missed runs during the
            week and hit mileage goals.
            What I've recetly noticed now that im hitting nearly 50 miles per
            week (even with steady uniform mileage) is that I have been seeing
            massive performance benefits from taking even one rest day!
            """
        ),
        dcc.Graph(figure=build_figures()["monthly_agg"]),
        html.P(
            """
            Looking at runs by month, I can clearly recall what was going on in
            each month of 2025.
            Specifically, March 2nd was my last cycling workout and I focused
            completely on running.
            In May I had backpacked in Yosemite for a week and then took quite
            a bit of time to get back into running, in June I had worked remote
            from San Diego and went surfing quite a bit with a good friend.
            """
        ),
        html.P(
            """
            Building up to November I had hit peak fitness but took a month
            long international trip, and if there's one thing I'm bad at, it's
            running on vacation.
            I didn't lose too much fitness during the trip, we stayed
            relatively active with swimming and city walking.
            """
        ),
        html.P(
            """
            Currently, I feel pretty good building and sustaining mileage in
            2026, but I am hitting time constraints.
            I might have to adopt double run days to increase mileage, but
            mostly I need to overcome laziness and do structured workouts to
            get faster and decrease time spent on runs.
            """
        ),
    ]
)