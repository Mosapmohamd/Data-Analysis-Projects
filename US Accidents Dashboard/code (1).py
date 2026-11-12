import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime
import dash_bootstrap_components as dbc

# Load and preprocess data (similar to notebook)
df = pd.read_csv(r"sampled_data_1.csv")
df_sample = df.sort_values(by='Start_Time', ascending=False).head(10000)

# Data preprocessing (from notebook) - with explicit datetime format
df_sample['Start_Time'] = pd.to_datetime(df_sample['Start_Time'], format='mixed', errors='coerce')
df_sample['End_Time'] = pd.to_datetime(df_sample['End_Time'], format='mixed', errors='coerce')
df_sample['Duration'] = (df_sample['End_Time'] - df_sample['Start_Time']).dt.total_seconds()
df_sample['Day_of_Week'] = df_sample['Start_Time'].dt.day_name()
df_sample['Month'] = df_sample['Start_Time'].dt.month
df_sample['Year'] = df_sample['Start_Time'].dt.year
df_sample['hour'] = df_sample['Start_Time'].dt.hour
df_sample['day_of_week'] = df_sample['Start_Time'].dt.dayofweek

# Time-based features
def time_of_day(hour):
    if 5 <= hour < 12:
        return "Morning"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 21:
        return "Evening"
    else:
        return "Night"

df_sample['time_of_day'] = df_sample['hour'].apply(time_of_day)
df_sample['is_weekend'] = df_sample['day_of_week'].isin([5, 6]).astype(int)

# Weather categorization
def categorize_weather(condition):
    if pd.isna(condition):
        return 'Unknown'
    condition = condition.lower()
    if 'rain' in condition or 'shower' in condition:
        return 'Rainy'
    elif 'snow' in condition or 'ice' in condition or 'sleet' in condition:
        return 'Snowy'
    elif 'fog' in condition or 'haze' in condition or 'mist' in condition:
        return 'Foggy'
    elif 'cloud' in condition:
        return 'Cloudy'
    elif 'clear' in condition or 'fair' in condition:
        return 'Clear'
    elif 'wind' in condition:
        return 'Windy'
    else:
        return 'Other'

df_sample['weather_category'] = df_sample['Weather_Condition'].apply(categorize_weather)

# Region classification
def get_region(state):
    northeast = ['CT', 'ME', 'MA', 'NH', 'RI', 'VT', 'NJ', 'NY', 'PA']
    midwest = ['IL', 'IN', 'MI', 'OH', 'WI', 'IA', 'KS', 'MN', 'MO', 'NE', 'ND', 'SD']
    south = ['DE', 'FL', 'GA', 'MD', 'NC', 'SC', 'VA', 'DC', 'WV', 'AL', 'KY', 'MS', 'TN', 'AR', 'LA', 'OK', 'TX']
    west = ['AZ', 'CO', 'ID', 'MT', 'NV', 'NM', 'UT', 'WY', 'AK', 'CA', 'HI', 'OR', 'WA']
    
    if state in northeast:
        return 'Northeast'
    elif state in midwest:
        return 'Midwest'
    elif state in south:
        return 'South'
    elif state in west:
        return 'West'
    else:
        return 'Unknown'

df_sample['region'] = df_sample['State'].apply(get_region)

# Severity categorization
def categorize_severity(severity):
    if severity == 1:
        return 'Low'
    elif severity == 2:
        return 'Medium'
    elif severity == 3:
        return 'High'
    else:
        return 'Very High'

df_sample['severity_category'] = df_sample['Severity'].apply(categorize_severity)
df_sample['weather_severity'] = df_sample['weather_category'] + '_' + df_sample['severity_category']

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
server = app.server

# Define app layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("US Accidents Analysis Dashboard", className="text-center mb-4"), width=12)
    ]),
    
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader("Filters", className="bg-primary text-white"),
                dbc.CardBody([
                    html.Label("Select Severity Level:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='severity-dropdown',
                        options=[{'label': f'Severity {i}', 'value': i} for i in sorted(df_sample['Severity'].unique())],
                        value=[1, 2, 3, 4],
                        multi=True,
                        className="mb-3"
                    ),
                    
                    html.Label("Select Time of Day:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='time-dropdown',
                        options=[{'label': i, 'value': i} for i in df_sample['time_of_day'].unique()],
                        value=df_sample['time_of_day'].unique(),
                        multi=True,
                        className="mb-3"
                    ),
                    
                    html.Label("Select Weather Condition:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='weather-dropdown',
                        options=[{'label': i, 'value': i} for i in df_sample['weather_category'].unique()],
                        value=df_sample['weather_category'].unique(),
                        multi=True,
                        className="mb-3"
                    ),
                    
                    html.Label("Select Region:", className="font-weight-bold"),
                    dcc.Dropdown(
                        id='region-dropdown',
                        options=[{'label': i, 'value': i} for i in df_sample['region'].unique()],
                        value=df_sample['region'].unique(),
                        multi=True,
                        className="mb-3"
                    ),
                    
                    html.Label("Select Year Range:", className="font-weight-bold"),
                    dcc.RangeSlider(
                        id='year-slider',
                        min=df_sample['Year'].min(),
                        max=df_sample['Year'].max(),
                        step=1,
                        value=[df_sample['Year'].min(), df_sample['Year'].max()],
                        marks={str(year): str(year) for year in df_sample['Year'].unique()},
                        className="mb-3"
                    )
                ])
            ], className="mb-4")
        ], md=3),
        
        dbc.Col([
            dbc.Row([
                dbc.Col(dcc.Graph(id='accidents-by-hour'), md=6),
                dbc.Col(dcc.Graph(id='accidents-by-weather'), md=6)
            ]),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id='severity-by-region'), md=6),
                dbc.Col(dcc.Graph(id='accidents-by-month'), md=6)
            ]),
            
            dbc.Row([
                dbc.Col(dcc.Graph(id='accidents-map'), md=12)
            ]),
            
            dbc.Row([
                dbc.Col(dash_table.DataTable(
                    id='data-table',
                    columns=[{"name": i, "id": i} for i in ['Start_Time', 'City', 'State', 'Severity', 'weather_category']],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'height': 'auto',
                        'minWidth': '100px', 'maxWidth': '180px',
                        'whiteSpace': 'normal',
                        'textAlign': 'left'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    }
                ), md=12)
            ])
        ], md=9)
    ])
], fluid=True)

# Callbacks for interactivity
@app.callback(
    [Output('accidents-by-hour', 'figure'),
     Output('accidents-by-weather', 'figure'),
     Output('severity-by-region', 'figure'),
     Output('accidents-by-month', 'figure'),
     Output('accidents-map', 'figure'),
     Output('data-table', 'data')],
    [Input('severity-dropdown', 'value'),
     Input('time-dropdown', 'value'),
     Input('weather-dropdown', 'value'),
     Input('region-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_dashboard(severity, time_of_day, weather, region, year_range):
    # Filter data based on selections
    filtered_df = df_sample[
        (df_sample['Severity'].isin(severity)) &
        (df_sample['time_of_day'].isin(time_of_day)) &
        (df_sample['weather_category'].isin(weather)) &
        (df_sample['region'].isin(region)) &
        (df_sample['Year'] >= year_range[0]) &
        (df_sample['Year'] <= year_range[1])
    ]
    
    # Accidents by hour
    hour_counts = filtered_df['hour'].value_counts().sort_index()
    fig_hour = px.bar(
        hour_counts, 
        x=hour_counts.index, 
        y=hour_counts.values,
        title='Accidents by Hour of Day',
        labels={'x': 'Hour', 'y': 'Number of Accidents'},
        color_discrete_sequence=['#636EFA']
    )
    fig_hour.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Accidents by weather
    weather_counts = filtered_df['weather_category'].value_counts()
    fig_weather = px.pie(
        weather_counts, 
        values=weather_counts.values, 
        names=weather_counts.index,
        title='Accidents by Weather Condition',
        hole=0.3
    )
    fig_weather.update_traces(textposition='inside', textinfo='percent+label')
    fig_weather.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Severity by region
    fig_severity = px.box(
        filtered_df, 
        x='region', 
        y='Severity',
        title='Accident Severity by Region',
        color='region',
        labels={'Severity': 'Severity Level', 'region': 'Region'}
    )
    fig_severity.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Accidents by month
    month_counts = filtered_df.groupby(['Year', 'Month']).size().reset_index(name='Count')
    fig_month = px.line(
        month_counts, 
        x='Month', 
        y='Count', 
        color='Year',
        title='Accidents by Month and Year',
        labels={'Month': 'Month', 'Count': 'Number of Accidents'}
    )
    fig_month.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Accidents map
    map_data = filtered_df.groupby(['State']).size().reset_index(name='Count')
    fig_map = px.choropleth(
        map_data,
        locations='State',
        locationmode='USA-states',
        color='Count',
        scope='usa',
        title='Accidents by State',
        color_continuous_scale='Blues'
    )
    fig_map.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    
    # Prepare table data
    table_data = filtered_df[['Start_Time', 'City', 'State', 'Severity', 'weather_category']].sort_values('Start_Time', ascending=False)
    table_data['Start_Time'] = table_data['Start_Time'].dt.strftime('%Y-%m-%d %H:%M')
    
    return fig_hour, fig_weather, fig_severity, fig_month, fig_map, table_data.to_dict('records')

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8051, use_reloader=False)