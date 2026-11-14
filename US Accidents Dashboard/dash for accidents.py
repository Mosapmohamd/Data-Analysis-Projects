import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px
import pandas as pd
import numpy as np
import logging
from functools import lru_cache
import warnings

# Suppress specific warnings
warnings.filterwarnings("ignore", category=FutureWarning, 
                       message="When grouping with a length-1 list-like")

# --------------------------
# Configuration
# --------------------------
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modern color theme
COLORS = {
    "background": "#f8fafc",
    "text": "#1e293b",
    "primary": "#3b82f6",
    "secondary": "#64748b",
    "accent": "#6366f1",
    "success": "#10b981",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "card": "#ffffff",
    "border": "#e2e8f0"
}

# --------------------------
# Initialize app with modern layout
# --------------------------
app = dash.Dash(__name__, external_stylesheets=[
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap"
])
app.title = "🚦 Modern Traffic Accident Dashboard"
server = app.server

# Custom CSS for modern look
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            :root {
                --primary: #3b82f6;
                --primary-light: #93c5fd;
                --text: #1e293b;
                --text-light: #64748b;
                --bg: #f8fafc;
                --card: #ffffff;
                --border: #e2e8f0;
            }
            body {
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 0;
                background-color: var(--bg);
                color: var(--text);
            }
            .header {
                background: linear-gradient(135deg, var(--primary) 0%, #6366f1 100%);
                color: white;
                padding: 1.5rem 2rem;
                border-radius: 0 0 12px 12px;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
                margin-bottom: 2rem;
            }
            .card {
                background: var(--card);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border);
                height: 100%;
            }
            .filter-card {
                background: var(--card);
                border-radius: 12px;
                padding: 1.5rem;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border: 1px solid var(--border);
                margin-bottom: 1.5rem;
            }
            .metric-card {
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                padding: 1.5rem;
                border-radius: 12px;
                background: var(--card);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                border-left: 4px solid var(--primary);
            }
            .metric-value {
                font-size: 2rem;
                font-weight: 600;
                color: var(--primary);
                margin: 0.5rem 0;
            }
            .metric-title {
                font-size: 0.875rem;
                color: var(--text-light);
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .dropdown {
                width: 100%;
            }
            .range-slider {
                width: 100%;
                margin-top: 1rem;
            }
            .btn {
                background: var(--primary);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s;
                margin-right: 0.5rem;
            }
            .btn:hover {
                background: #2563eb;
                transform: translateY(-1px);
            }
            .btn-secondary {
                background: var(--secondary);
            }
            .btn-secondary:hover {
                background: #475569;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(12, 1fr);
                gap: 1.5rem;
                width: 100%;
                max-width: 1400px;
                margin: 0 auto;
                padding: 0 1.5rem;
            }
            .col-3 {
                grid-column: span 3;
            }
            .col-4 {
                grid-column: span 4;
            }
            .col-6 {
                grid-column: span 6;
            }
            .col-9 {
                grid-column: span 9;
            }
            .col-12 {
                grid-column: span 12;
            }
            .chart-container {
                height: 100%;
                width: 100%;
            }
            .tabs {
                display: flex;
                border-bottom: 1px solid var(--border);
                margin-bottom: 1.5rem;
            }
            .tab {
                padding: 0.75rem 1.5rem;
                cursor: pointer;
                border-bottom: 2px solid transparent;
                font-weight: 500;
                color: var(--text-light);
            }
            .tab.active {
                color: var(--primary);
                border-bottom: 2px solid var(--primary);
            }
            @media (max-width: 1200px) {
                .grid {
                    grid-template-columns: repeat(1, 1fr);
                }
                .col-3, .col-4, .col-6, .col-9 {
                    grid-column: span 1;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# --------------------------
# Data Loading & Processing
# --------------------------
@lru_cache(maxsize=32)
def load_data(path):
    try:
        df = pd.read_csv(path)
        
        # Validate required columns
        required_cols = ['Start_Time', 'Severity', 'Weather_Condition', 'State']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
            
        return df
    except Exception as e:
        logger.error(f"Error loading data: {e}")
        return pd.DataFrame()

def parse_datetime(series):
    """Parse datetime series with multiple format attempts"""
    datetime_formats = [
        '%Y-%m-%d %H:%M:%S',    # 2023-01-01 12:34:56
        '%m/%d/%Y %H:%M:%S',    # 01/01/2023 12:34:56
        '%Y-%m-%dT%H:%M:%S',     # ISO format
        '%Y-%m-%d %H:%M:%S.%f',  # With milliseconds
        '%Y-%m-%d %H:%M',        # Without seconds
        '%m/%d/%Y %H:%M'         # Without seconds
    ]

    for fmt in datetime_formats:
        try:
            parsed = pd.to_datetime(series, format=fmt, errors='raise')
            logger.info(f"Successfully parsed datetime with format: {fmt}")
            return parsed
        except ValueError:
            continue
    
    # If none of the formats worked, fall back to coerce
    logger.warning("Could not determine datetime format, using fallback parsing")
    return pd.to_datetime(series, errors='coerce')

def preprocess_data(df):
    """Clean and preprocess the accident data"""
    if df.empty:
        return df
    
    # Make copy to avoid SettingWithCopyWarning
    df = df.copy()
    
    # Convert and validate datetime columns
    for col in ['Start_Time', 'End_Time']:
        if col in df.columns:
            df[col] = parse_datetime(df[col])
            if df[col].isnull().all():
                raise ValueError(f"Column {col} could not be converted to datetime")
    
    # Calculate duration in minutes
    df['Duration'] = (df['End_Time'] - df['Start_Time']).dt.total_seconds() / 60
    
    # Extract temporal features
    df['hour'] = df['Start_Time'].dt.hour
    df['day_of_week'] = df['Start_Time'].dt.dayofweek
    df['month'] = df['Start_Time'].dt.month
    df['year'] = df['Start_Time'].dt.year
    
    # Time of day categorization
    def time_of_day(h):
        if pd.isna(h): return 'Unknown'
        if 5 <= h < 12: return 'Morning'
        if 12 <= h < 17: return 'Afternoon'
        if 17 <= h < 21: return 'Evening'
        return 'Night'
    
    df['time_of_day'] = df['hour'].apply(time_of_day)
    
    # Weather categorization
    def categorize_weather(cond):
        if pd.isna(cond): return 'Unknown'
        c = str(cond).lower()
        if 'rain' in c or 'shower' in c: return 'Rainy'
        if 'snow' in c or 'ice' in c or 'sleet' in c: return 'Snowy'
        if 'fog' in c or 'haze' in c or 'mist' in c: return 'Foggy'
        if 'cloud' in c: return 'Cloudy'
        if 'clear' in c or 'fair' in c: return 'Clear'
        if 'wind' in c: return 'Windy'
        return 'Other'
    
    df['weather_category'] = df['Weather_Condition'].apply(categorize_weather)
    
    # Region mapping
    def get_region(state):
        northeast = ['CT','ME','MA','NH','RI','VT','NJ','NY','PA']
        midwest = ['IL','IN','MI','OH','WI','IA','KS','MN','MO','NE','ND','SD']
        south = ['DE','FL','GA','MD','NC','SC','VA','DC','WV','AL','KY','MS','TN','AR','LA','OK','TX']
        west = ['AZ','CO','ID','MT','NV','NM','UT','WY','AK','CA','HI','OR','WA']
        
        if state in northeast: return 'Northeast'
        if state in midwest: return 'Midwest'
        if state in south: return 'South'
        if state in west: return 'West'
        return 'Unknown'
    
    df['region'] = df['State'].apply(get_region)
    
    # Road features - handle missing columns gracefully
    road_features = ['Amenity','Bump','Crossing','Give_Way','Junction',
                    'No_Exit','Railway','Roundabout','Station','Stop',
                    'Traffic_Calming','Traffic_Signal','Turning_Loop']
    
    for f in road_features:
        col_name = f'has_{f.lower()}'
        if f in df.columns:
            df[col_name] = df[f].fillna(0).astype(int)
        else:
            df[col_name] = 0
    
    # Handle missing coordinates
    for coord in ['Start_Lat', 'Start_Lng']:
        if coord in df.columns:
            df[coord] = pd.to_numeric(df[coord], errors='coerce')
        else:
            df[coord] = np.nan
    
    return df

# Load and preprocess data
try:
    raw_df = load_data("sampled_data_1.csv")
    df = preprocess_data(raw_df.sort_values(by='Start_Time', ascending=False).head(10000))
    
    # Set default filter values based on actual data
    DEFAULT_SEVERITY = [int(df['Severity'].min()), int(df['Severity'].max())]
    DEFAULT_WEATHER = ['Clear', 'Cloudy', 'Rainy']
    DEFAULT_TIMES = ['Morning', 'Afternoon', 'Evening', 'Night']
    
except Exception as e:
    logger.error(f"Data loading error: {e}")
    df = pd.DataFrame()
    DEFAULT_SEVERITY = [1, 4]
    DEFAULT_WEATHER = []
    DEFAULT_TIMES = []

# --------------------------
# Modern App Layout
# --------------------------
app.layout = html.Div([
    # Header
    html.Div([
        html.Div([
            html.H1("Traffic Accident Analysis", className="col-12", style={
                'color': 'white',
                'marginBottom': '0.5rem',
                'fontWeight': '600'
            }),
            html.P("Interactive dashboard for analyzing traffic accident patterns", style={
                'color': 'rgba(255, 255, 255, 0.9)',
                'marginBottom': '0',
                'fontSize': '1.1rem'
            })
        ], className="grid")
    ], className="header"),
    
    # Main content grid
    html.Div([
        # Filters sidebar
        html.Div([
            html.Div([
                html.H3("Filters", style={
                    'marginTop': '0',
                    'color': COLORS['text']
                }),
                
                # Severity filter
                html.Div([
                    html.Label("Accident Severity", style={
                        'display': 'block',
                        'marginBottom': '0.5rem',
                        'fontWeight': '500',
                        'color': COLORS['text']
                    }),
                    dcc.RangeSlider(
                        id='severity-slider',
                        min=1,
                        max=4,
                        step=1,
                        marks={i: str(i) for i in range(1, 5)},
                        value=DEFAULT_SEVERITY,
                        className="range-slider"
                    )
                ], className="filter-card"),
                
                # Weather filter
                html.Div([
                    html.Label("Weather Conditions", style={
                        'display': 'block',
                        'marginBottom': '0.5rem',
                        'fontWeight': '500',
                        'color': COLORS['text']
                    }),
                    dcc.Dropdown(
                        id='weather-dropdown',
                        options=[{'label': w, 'value': w} for w in sorted(df['weather_category'].unique())],
                        value=DEFAULT_WEATHER,
                        multi=True,
                        className="dropdown"
                    )
                ], className="filter-card"),
                
                # Time of day filter
                html.Div([
                    html.Label("Time of Day", style={
                        'display': 'block',
                        'marginBottom': '0.5rem',
                        'fontWeight': '500',
                        'color': COLORS['text']
                    }),
                    dcc.Dropdown(
                        id='time-dropdown',
                        options=[{'label': t, 'value': t} for t in ['Morning', 'Afternoon', 'Evening', 'Night', 'Unknown']],
                        value=DEFAULT_TIMES,
                        multi=True,
                        className="dropdown"
                    )
                ], className="filter-card"),
                
                # Action buttons
                html.Div([
                    html.Button("Reset Filters", id="reset-btn", className="btn btn-secondary"),
                    html.Button("Download Data", id="download-btn", className="btn"),
                    dcc.Download(id="download-dataframe-csv")
                ], style={'marginTop': '1rem'})
            ], className="card")
        ], className="col-3"),
        
        # Main content area
        html.Div([
            dcc.Tabs([
                dcc.Tab(label="Overview", children=[
                    # Metrics cards
                    html.Div([
                        html.Div(id='total-accidents', className="metric-card"),
                        html.Div(id='avg-severity', className="metric-card"),
                        html.Div(id='avg-duration', className="metric-card"),
                        html.Div(id='top-weather', className="metric-card")
                    ], className="grid", style={'marginBottom': '1.5rem', 'gridTemplateColumns': 'repeat(4, 1fr)'}),
                    
                    # First row of charts
                    html.Div([
                        html.Div([
                            dcc.Graph(id='severity-chart', className="chart-container")
                        ], className="card"),
                        html.Div([
                            dcc.Graph(id='time-of-day-chart', className="chart-container")
                        ], className="card")
                    ], className="grid", style={'gridTemplateColumns': 'repeat(2, 1fr)'}),
                    
                    # Second row of charts
                    html.Div([
                        html.Div([
                            dcc.Graph(id='weather-chart', className="chart-container")
                        ], className="card"),
                        html.Div([
                            dcc.Graph(id='region-chart', className="chart-container")
                        ], className="card")
                    ], className="grid", style={'gridTemplateColumns': 'repeat(2, 1fr)'}),
                    
                    # Third row
                    html.Div([
                        html.Div([
                            dcc.Graph(id='duration-chart', className="chart-container")
                        ], className="card"),
                        html.Div([
                            dcc.Graph(id='road-features-chart', className="chart-container")
                        ], className="card")
                    ], className="grid", style={'gridTemplateColumns': 'repeat(2, 1fr)'}),
                    
                    # Map
                    html.Div([
                        dcc.Graph(id='geo-map', className="chart-container")
                    ], className="card", style={'marginTop': '1.5rem'})
                ]),
                
                dcc.Tab(label="Raw Data", children=[
                    html.Div([
                        dash_table.DataTable(
                            id='data-table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                            page_size=15,
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'padding': '10px',
                                'textAlign': 'left',
                                'border': '1px solid #e2e8f0'
                            },
                            style_header={
                                'backgroundColor': COLORS['primary'],
                                'color': 'white',
                                'fontWeight': 'bold'
                            }
                        )
                    ], className="card")
                ])
            ])
        ], className="col-9")
    ], className="grid", style={'marginTop': '1.5rem'})
])

# --------------------------
# Callbacks
# --------------------------
@app.callback(
    [Output('severity-chart', 'figure'),
     Output('time-of-day-chart', 'figure'),
     Output('weather-chart', 'figure'),
     Output('region-chart', 'figure'),
     Output('duration-chart', 'figure'),
     Output('road-features-chart', 'figure'),
     Output('geo-map', 'figure'),
     Output('total-accidents', 'children'),
     Output('avg-severity', 'children'),
     Output('avg-duration', 'children'),
     Output('top-weather', 'children')],
    [Input('severity-slider', 'value'),
     Input('weather-dropdown', 'value'),
     Input('time-dropdown', 'value'),
     Input('reset-btn', 'n_clicks')]
)
def update_dashboard(severity_range, weather_conditions, time_of_day, reset_clicks):
    ctx = dash.callback_context
    
    # Handle reset button
    if ctx.triggered and ctx.triggered[0]['prop_id'] == 'reset-btn.n_clicks':
        severity_range = DEFAULT_SEVERITY
        weather_conditions = DEFAULT_WEATHER
        time_of_day = DEFAULT_TIMES
    
    # Apply filters
    try:
        filtered = df[
            (df['Severity'] >= severity_range[0]) & 
            (df['Severity'] <= severity_range[1]) &
            (df['weather_category'].isin(weather_conditions)) &
            (df['time_of_day'].isin(time_of_day))
        ]
    except Exception as e:
        logger.error(f"Filtering error: {e}")
        filtered = df.copy()
    
    # Calculate metrics
    total_acc = len(filtered)
    avg_sev = filtered['Severity'].mean() if total_acc > 0 else 0
    avg_dur = filtered['Duration'].mean() if total_acc > 0 else 0
    top_weather = filtered['weather_category'].mode()[0] if total_acc > 0 else "N/A"
    
    # Create charts
    # 1. Severity pie chart
    severity_fig = px.pie(
        filtered['Severity'].value_counts().reset_index(),
        names='Severity',
        values='count',
        title="Accident Severity Distribution",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    severity_fig.update_traces(textinfo='percent+label')
    severity_fig.update_layout(margin=dict(t=40, b=20))
    
    # 2. Time of day bar chart
    time_fig = px.bar(
        filtered['time_of_day'].value_counts().reset_index(),
        x='time_of_day',
        y='count',
        title="Accidents by Time of Day",
        labels={'time_of_day': 'Time of Day', 'count': 'Number of Accidents'},
        color='time_of_day',
        color_discrete_sequence=px.colors.sequential.Blues
    )
    time_fig.update_layout(showlegend=False, margin=dict(t=40, b=20))
    
    # 3. Weather bar chart
    weather_fig = px.bar(
        filtered['weather_category'].value_counts().reset_index(),
        x='weather_category',
        y='count',
        title="Accidents by Weather Condition",
        labels={'weather_category': 'Weather Condition', 'count': 'Number of Accidents'},
        color='weather_category',
        color_discrete_sequence=px.colors.sequential.Greens
    )
    weather_fig.update_layout(showlegend=False, margin=dict(t=40, b=20))
    
    # 4. Region bar chart
    region_fig = px.bar(
        filtered['region'].value_counts().reset_index(),
        x='region',
        y='count',
        title="Accidents by Region",
        labels={'region': 'Region', 'count': 'Number of Accidents'},
        color='region',
        color_discrete_sequence=px.colors.sequential.Oranges
    )
    region_fig.update_layout(showlegend=False, margin=dict(t=40, b=20))
    
    # 5. Duration histogram
    duration_fig = px.histogram(
        filtered,
        x='Duration',
        nbins=30,
        title="Accident Duration Distribution (minutes)",
        labels={'Duration': 'Duration (minutes)'},
        color_discrete_sequence=[COLORS['primary']]
    )
    duration_fig.update_layout(margin=dict(t=40, b=20))
    
    # 6. Road features
    road_features = ['Amenity','Bump','Crossing','Give_Way','Junction',
                    'No_Exit','Railway','Roundabout','Station','Stop',
                    'Traffic_Calming','Traffic_Signal','Turning_Loop']
    road_counts = {f: filtered[f'has_{f.lower()}'].sum() for f in road_features}
    road_fig = px.bar(
        x=list(road_counts.keys()),
        y=list(road_counts.values()),
        title="Road Features at Accident Sites",
        labels={'x': 'Road Feature', 'y': 'Count'},
        color=list(road_counts.keys()),
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    road_fig.update_layout(showlegend=False, margin=dict(t=40, b=20), xaxis_tickangle=-45)
    
    # 7. Geographic map
    geo_fig = px.density_mapbox(
        filtered.dropna(subset=['Start_Lat', 'Start_Lng']),
        lat='Start_Lat',
        lon='Start_Lng',
        radius=7,
        zoom=3,
        hover_data=['Severity', 'weather_category', 'time_of_day'],
        title="Geographic Distribution of Accidents",
        mapbox_style="stamen-terrain",
        color_continuous_scale=px.colors.sequential.Bluered,
        opacity=0.7
    )
    geo_fig.update_layout(margin=dict(t=40, b=20, l=0, r=0))
    
    # Create metric cards
    def create_metric_card(title, value, unit=""):
        return [
            html.Div(title, className="metric-title"),
            html.Div(f"{value}{unit}", className="metric-value")
        ]
    
    total_accidents = create_metric_card("Total Accidents", total_acc)
    avg_severity_card = create_metric_card("Avg. Severity", f"{avg_sev:.2f}", "/4")
    avg_duration_card = create_metric_card("Avg. Duration", f"{avg_dur:.1f}", " min")
    top_weather_card = create_metric_card("Most Common Weather", top_weather)
    
    return (
        severity_fig, time_fig, weather_fig, region_fig, 
        duration_fig, road_fig, geo_fig,
        total_accidents, avg_severity_card, avg_duration_card, top_weather_card
    )

@app.callback(
    Output("download-dataframe-csv", "data"),
    [Input("download-btn", "n_clicks")],
    [State('severity-slider', 'value'),
     State('weather-dropdown', 'value'),
     State('time-dropdown', 'value')],
    prevent_initial_call=True
)
def download_csv(n_clicks, severity_range, weather_conditions, time_of_day):
    filtered = df[
        (df['Severity'] >= severity_range[0]) & 
        (df['Severity'] <= severity_range[1]) &
        (df['weather_category'].isin(weather_conditions)) &
        (df['time_of_day'].isin(time_of_day))
    ]
    return dcc.send_data_frame(filtered.to_csv, "filtered_accidents.csv")

# --------------------------
# Run the app
# --------------------------
if __name__ == '__main__':
    app.run_server(debug=True)