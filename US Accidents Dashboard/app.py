# app.py
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
import os

# ---------- config ----------
CSV_PATH = os.path.join(os.getcwd(), "sampled_data_1.csv")  # change if needed
PORT = 7050

# ---------- dark theme ----------
colors = {
    "background": "#0f0f0f",
    "panel": "#151515",
    "text": "#DCEFFB",
    "accent": "#636EFA",
    "highlight": "#2A3F5F"
}

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

# ---------- load data ----------
def load_and_preprocess(path):
    try:
        df = pd.read_csv(path)
    except Exception:
        # fallback empty frame with expected columns
        cols = ['ID', 'Source', 'Severity', 'Start_Time', 'End_Time', 'Start_Lat',
                'Start_Lng', 'End_Lat', 'End_Lng', 'Distance(mi)', 'Description',
                'Street', 'City', 'County', 'State', 'Zipcode', 'Country', 'Timezone',
                'Airport_Code', 'Weather_Timestamp', 'Temperature(F)', 'Wind_Chill(F)',
                'Humidity(%)', 'Pressure(in)', 'Visibility(mi)', 'Wind_Direction',
                'Wind_Speed(mph)', 'Precipitation(in)', 'Weather_Condition', 'Amenity',
                'Bump', 'Crossing', 'Give_Way', 'Junction', 'No_Exit', 'Railway',
                'Roundabout', 'Station', 'Stop', 'Traffic_Calming', 'Traffic_Signal',
                'Turning_Loop', 'Sunrise_Sunset', 'Civil_Twilight', 'Nautical_Twilight',
                'Astronomical_Twilight']
        return pd.DataFrame(columns=cols)

    # strip column names
    df.columns = [c.strip() for c in df.columns]

    # Parse datetimes
    for c in ["Start_Time", "End_Time", "Weather_Timestamp"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce")

    # numeric conversions
    num_cols = ["Distance(mi)", "Temperature(F)", "Wind_Speed(mph)", "Visibility(mi)", "Humidity(%)", "Pressure(in)"]
    for c in num_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # boolean flag normalization: convert truthy values to 1
    bool_cols = ['Amenity', 'Bump', 'Crossing', 'Give_Way', 'Junction', 'No_Exit', 'Railway',
                 'Roundabout', 'Station', 'Stop', 'Traffic_Calming', 'Traffic_Signal', 'Turning_Loop']
    for c in bool_cols:
        if c in df.columns:
            # handle strings like 'True','False' or 0/1
            df[c] = df[c].replace({True: 1, False: 0, "True": 1, "False": 0}).fillna(0).astype(int)

    # create helper columns
    if "Start_Time" in df.columns:
        df["date"] = df["Start_Time"].dt.date
        df["hour"] = df["Start_Time"].dt.hour
        df["month"] = df["Start_Time"].dt.to_period("M").astype(str)
    else:
        df["date"] = pd.NaT
        df["hour"] = np.nan
        df["month"] = np.nan

    # severity normalization to string for plotting if numeric
    if "Severity" in df.columns:
        df["Severity_str"] = df["Severity"].astype(str)
    else:
        df["Severity_str"] = "N/A"

    # trim Weather_Condition text
    if "Weather_Condition" in df.columns:
        df["Weather_Condition"] = df["Weather_Condition"].astype(str).str.strip().replace({"nan": None})

    # keep a small sample column for map sampling performance
    df["_map_sample_flag"] = False
    try:
        if "Start_Lat" in df.columns and "Start_Lng" in df.columns:
            # mark a sample of up to 2000 for map rendering
            sample_n = min(2000, len(df))
            if sample_n > 0:
                df.loc[df.sample(n=sample_n, random_state=1).index, "_map_sample_flag"] = True
    except Exception:
        pass

    return df

df = load_and_preprocess(CSV_PATH)

# ---------- small helpers ----------
def options_from(series):
    if series is None:
        return []
    vals = sorted(pd.Series(series).dropna().unique())
    return [{"label": str(v), "value": v} for v in vals]

def safe_update_layout(fig):
    try:
        return fig.update_layout(plot_bgcolor=colors["panel"], paper_bgcolor=colors["panel"], font_color=colors["text"])
    except Exception:
        return fig

# ---------- app ----------
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# ---------- layout ----------
app.layout = html.Div(style={"backgroundColor": colors["background"], "color": colors["text"], "minHeight": "100vh"}, children=[
    html.Div([
        html.Img(src="https://cdn-icons-png.flaticon.com/512/1946/1946429.png", style={"height": "48px", "marginRight": "12px"}),
        html.H1("Accidents Dashboard", style={"display": "inline-block", "verticalAlign": "middle"})
    ], style={"padding": "14px", "borderBottom": f"1px solid {colors['highlight']}", "marginBottom": "8px"}),

    # info bar (KPIs)
    html.Div(id="info-bar", style={"display": "flex", "gap": "12px", "padding": "12px", "backgroundColor": colors["panel"], "borderRadius": "6px", "margin": "10px"}),

    # main row
    html.Div([
        # filters column
        html.Div([
            html.H3("Filters", style={"borderBottom": f"1px solid {colors['highlight']}", "paddingBottom": "8px"}),

            html.Label("Date range"),
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=(df["Start_Time"].min().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None),
                max_date_allowed=(df["Start_Time"].max().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None),
                start_date=(df["Start_Time"].min().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None),
                end_date=(df["Start_Time"].max().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None),
                display_format="YYYY-MM-DD",
                style={"width": "100%"}
            ),

            html.Br(), html.Br(),

            html.Label("State"),
            dcc.Dropdown(id="state-filter", options=options_from(df.get("State")), multi=True, placeholder="State"),

            html.Br(),
            html.Label("City"),
            dcc.Dropdown(id="city-filter", options=options_from(df.get("City")), multi=True, placeholder="City"),

            html.Br(),
            html.Label("Severity"),
            dcc.Dropdown(id="severity-filter", options=options_from(df.get("Severity")), multi=True, placeholder="Severity"),

            html.Br(),
            html.Label("Weather Condition"),
            dcc.Dropdown(id="weather-filter", options=options_from(df.get("Weather_Condition")), multi=True, placeholder="Weather"),

            html.Br(),
            html.Label("Distance (mi)"),
            dcc.RangeSlider(
                id="distance-slider",
                min=float(df["Distance(mi)"].min()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 0.0,
                max=float(df["Distance(mi)"].max()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 100.0,
                step=0.1,
                value=[
                    float(df["Distance(mi)"].min()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 0.0,
                    float(df["Distance(mi)"].max()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 100.0
                ],
                tooltip={"placement": "bottom"}
            ),

            html.Br(),
            html.Label("Boolean flags"),
            dcc.Checklist(
                id="bool-flags",
                options=[{"label": c, "value": c} for c in ['Amenity', 'Bump', 'Crossing', 'Traffic_Signal'] if c in df.columns],
                value=[],
                labelStyle={"display": "block"}
            ),

            html.Br(),
            html.Button("Reset filters", id="reset-filters", n_clicks=0, style={"width": "100%", "backgroundColor": colors["accent"], "color": "#fff"})
        ], className="three columns", style={"padding": "14px", "backgroundColor": colors["panel"], "borderRadius": "6px", "margin": "10px"}),

        # main content
        html.Div([
            dcc.Tabs(id="tabs", value="overview", children=[
                dcc.Tab(label="Overview", value="overview", style={"backgroundColor": colors["panel"]}),
                dcc.Tab(label="Time Analysis", value="time", style={"backgroundColor": colors["panel"]}),
                dcc.Tab(label="Weather Analysis", value="weather", style={"backgroundColor": colors["panel"]}),
                dcc.Tab(label="Map", value="map", style={"backgroundColor": colors["panel"]}),
                dcc.Tab(label="Data", value="data", style={"backgroundColor": colors["panel"]}),
            ], colors={"border": colors["highlight"], "primary": colors["accent"], "background": colors["panel"]}),

            html.Div(id="tabs-content", style={"padding": "14px"})
        ], className="nine columns")
    ], className="row")
])

# ---------- filtering logic ----------
def apply_filters(dframe, state_vals, city_vals, severity_vals, weather_vals, start_date, end_date, distance_range, bool_flags):
    dff = dframe.copy()
    if state_vals:
        dff = dff[dff["State"].isin(state_vals)]
    if city_vals:
        dff = dff[dff["City"].isin(city_vals)]
    if severity_vals:
        dff = dff[dff["Severity"].isin(severity_vals)]
    if weather_vals:
        dff = dff[dff["Weather_Condition"].isin(weather_vals)]
    if start_date and end_date and "Start_Time" in dff.columns:
        s = pd.to_datetime(start_date)
        e = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        dff = dff[(dff["Start_Time"] >= s) & (dff["Start_Time"] <= e)]
    if distance_range and "Distance(mi)" in dff.columns:
        dff = dff[(dff["Distance(mi)"] >= distance_range[0]) & (dff["Distance(mi)"] <= distance_range[1])]
    if bool_flags:
        for f in bool_flags:
            if f in dff.columns:
                dff = dff[dff[f] == 1]
    return dff

# ---------- KPIs ----------
@app.callback(
    Output("info-bar", "children"),
    [Input("state-filter", "value"),
     Input("city-filter", "value"),
     Input("severity-filter", "value"),
     Input("weather-filter", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("distance-slider", "value"),
     Input("bool-flags", "value")]
)
def update_kpis(states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags):
    dff = apply_filters(df, states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags)
    total = len(dff)
    most_common_sev = dff["Severity"].mode().iloc[0] if ("Severity" in dff.columns and not dff["Severity"].dropna().empty) else "N/A"
    avg_distance = f"{dff['Distance(mi)'].mean():.2f} mi" if "Distance(mi)" in dff.columns and not dff.empty else "N/A"
    avg_temp = f"{dff['Temperature(F)'].mean():.1f} F" if "Temperature(F)" in dff.columns and not dff.empty else "N/A"

    return [
        html.Div([html.H5("Total accidents", style={"color": colors["accent"]}), html.H3(total)], style={"textAlign": "center", "flex": "1"}),
        html.Div([html.H5("Top severity", style={"color": colors["accent"]}), html.H3(most_common_sev)], style={"textAlign": "center", "flex": "1"}),
        html.Div([html.H5("Avg distance", style={"color": colors["accent"]}), html.H3(avg_distance)], style={"textAlign": "center", "flex": "1"}),
        html.Div([html.H5("Avg temp", style={"color": colors["accent"]}), html.H3(avg_temp)], style={"textAlign": "center", "flex": "1"}),
        html.Div([html.H5("Last updated", style={"color": colors["accent"]}), html.H3(datetime.now().strftime("%Y-%m-%d"))], style={"textAlign": "center", "flex": "1"})
    ]

# ---------- reset filters ----------
@app.callback(
    [Output("state-filter", "value"),
     Output("city-filter", "value"),
     Output("severity-filter", "value"),
     Output("weather-filter", "value"),
     Output("date-range", "start_date"),
     Output("date-range", "end_date"),
     Output("distance-slider", "value"),
     Output("bool-flags", "value")],
    Input("reset-filters", "n_clicks")
)
def reset_filters(n):
    start = df["Start_Time"].min().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None
    end = df["Start_Time"].max().date() if "Start_Time" in df.columns and not df["Start_Time"].isna().all() else None
    dist_min = float(df["Distance(mi)"].min()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 0.0
    dist_max = float(df["Distance(mi)"].max()) if "Distance(mi)" in df.columns and not df["Distance(mi)"].isna().all() else 100.0
    return [None, None, None, None, start, end, [dist_min, dist_max], []]

# ---------- tabs rendering ----------
@app.callback(
    Output("tabs-content", "children"),
    [Input("tabs", "value"),
     Input("state-filter", "value"),
     Input("city-filter", "value"),
     Input("severity-filter", "value"),
     Input("weather-filter", "value"),
     Input("date-range", "start_date"),
     Input("date-range", "end_date"),
     Input("distance-slider", "value"),
     Input("bool-flags", "value")]
)
def render_tab(tab, states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags):
    dff = apply_filters(df, states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags)

    # Overview tab
    if tab == "overview":
        # pie: severity
        if "Severity" in dff.columns:
            sev_counts = dff["Severity"].value_counts().reset_index()
            sev_counts.columns = ["Severity", "count"]
            fig_sev = px.pie(sev_counts, names="Severity", values="count", title="Accidents by Severity")
            fig_sev = safe_update_layout(fig_sev)
        else:
            fig_sev = {}

        # bar: state (top 20)
        if "State" in dff.columns:
            st_counts = dff["State"].value_counts().reset_index().head(20)
            st_counts.columns = ["State", "count"]
            fig_state = px.bar(st_counts, x="State", y="count", title="Accidents by State (top 20)")
            fig_state = safe_update_layout(fig_state)
        else:
            fig_state = {}

        # top weather
        if "Weather_Condition" in dff.columns:
            w_counts = dff["Weather_Condition"].value_counts().reset_index().head(20)
            w_counts.columns = ["Weather", "count"]
            fig_weather = px.bar(w_counts, x="Weather", y="count", title="Top Weather Conditions")
            fig_weather = safe_update_layout(fig_weather)
        else:
            fig_weather = {}

        return html.Div([
            html.Div([
                html.Div(dcc.Graph(figure=fig_sev) if fig_sev else html.Div("No severity data", style={"color": colors["text"]}), className="six columns"),
                html.Div(dcc.Graph(figure=fig_state) if fig_state else html.Div("No state data", style={"color": colors["text"]}), className="six columns"),
            ], className="row"),
            html.Div(dcc.Graph(figure=fig_weather) if fig_weather else html.Div("No weather data", style={"color": colors["text"]}))
        ])

    # Time analysis tab
    if tab == "time":
        if "date" in dff.columns and not dff["date"].isna().all():
            ts = dff.groupby("date").size().reset_index(name="count")
            fig_ts = px.line(ts, x="date", y="count", title="Accidents over Time")
            fig_ts = safe_update_layout(fig_ts)
        else:
            fig_ts = {}

        if "hour" in dff.columns and "Severity_str" in dff.columns:
            # heatmap hour vs severity counts
            heat = dff.groupby(["hour", "Severity_str"]).size().reset_index(name="count")
            if not heat.empty:
                heat_pivot = heat.pivot(index="Severity_str", columns="hour", values="count").fillna(0)
                fig_hour = px.imshow(heat_pivot, aspect="auto", labels=dict(x="Hour of day", y="Severity", color="count"), title="Hour vs Severity heatmap")
                fig_hour = safe_update_layout(fig_hour)
            else:
                fig_hour = {}
        else:
            fig_hour = {}

        return html.Div([
            dcc.Graph(figure=fig_ts) if fig_ts else html.Div("No time series data", style={"color": colors["text"]}),
            dcc.Graph(figure=fig_hour) if fig_hour else html.Div("No hourly heatmap data", style={"color": colors["text"]})
        ])

    # Weather analysis tab
    if tab == "weather":
        figs = []
        if "Severity" in dff.columns and "Temperature(F)" in dff.columns:
            fig_temp = px.box(dff, x="Severity_str", y="Temperature(F)", title="Temperature by Severity")
            figs.append(safe_update_layout(fig_temp))
        if "Severity" in dff.columns and "Visibility(mi)" in dff.columns:
            fig_vis = px.box(dff, x="Severity_str", y="Visibility(mi)", title="Visibility by Severity")
            figs.append(safe_update_layout(fig_vis))
        if "Temperature(F)" in dff.columns and "Visibility(mi)" in dff.columns:
            fig_scatter = px.scatter(dff, x="Temperature(F)", y="Visibility(mi)", title="Temperature vs Visibility", trendline="ols")
            figs.append(safe_update_layout(fig_scatter))

        if not figs:
            return html.Div("No weather data available", style={"color": colors["text"]})

        return html.Div([dcc.Graph(figure=f) for f in figs])

    # Map tab
    if tab == "map":
        if "Start_Lat" in dff.columns and "Start_Lng" in dff.columns:
            map_df = dff[dff["_map_sample_flag"] == True] if "_map_sample_flag" in dff.columns and dff["_map_sample_flag"].any() else dff
            # choose hover fields if present
            hovercols = [c for c in ["Start_Time", "City", "State", "Weather_Condition", "Description"] if c in map_df.columns]
            fig_map = px.scatter_mapbox(
                map_df,
                lat="Start_Lat",
                lon="Start_Lng",
                color="Severity_str" if "Severity_str" in map_df.columns else None,
                hover_data=hovercols if hovercols else None,
                zoom=3,
                height=700,
                title="Accident Locations"
            )
            fig_map.update_layout(mapbox_style="open-street-map")
            fig_map = safe_update_layout(fig_map)
            return dcc.Graph(figure=fig_map)
        return html.Div("No location data available", style={"color": colors["text"]})

    # Data tab
    if tab == "data":
        table = dash_table.DataTable(
            id="datatable",
            columns=[{"name": i, "id": i} for i in dff.columns],
            data=dff.to_dict("records"),
            page_size=15,
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": colors["highlight"], "color": colors["text"], "fontWeight": "bold"},
            style_cell={"backgroundColor": colors["panel"], "color": colors["text"], "border": f"1px solid {colors['highlight']}"},
            filter_action="native",
            sort_action="native",
            sort_mode="multi"
        )
        return html.Div([
            html.H4("Filtered data", style={"textAlign": "center"}),
            table,
            html.Div([html.Button("Download CSV", id="btn_csv"), dcc.Download(id="download-dataframe-csv")], style={"marginTop": "12px"})
        ])

    return html.Div("Tab not found", style={"color": colors["text"]})

# ---------- download callback ----------
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    [State("state-filter", "value"),
     State("city-filter", "value"),
     State("severity-filter", "value"),
     State("weather-filter", "value"),
     State("date-range", "start_date"),
     State("date-range", "end_date"),
     State("distance-slider", "value"),
     State("bool-flags", "value")],
    prevent_initial_call=True
)
def download_filtered(n_clicks, states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags):
    dff = apply_filters(df, states, cities, severities, weathers, start_date, end_date, distance_range, bool_flags)
    return dcc.send_data_frame(dff.to_csv, "filtered_accidents.csv", index=False)

# ---------- run ----------
if __name__ == "__main__":
    app.run(debug=True, port=PORT)
