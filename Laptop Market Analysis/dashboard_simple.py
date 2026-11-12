# This code loads the laptop_data.csv, inspects the data, and creates a modern dashboard with key insights using Plotly Dash.
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html
import dash_bootstrap_components as dbc

# Load the data
df = pd.read_csv('laptop_data.csv', encoding='ascii')

# Clean up column names if needed
df.columns = [c.strip() for c in df.columns]

# Convert Price to numeric if not already
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Prepare some key insights
avg_price = df['Price'].mean()
top_companies = df['Company'].value_counts().head(5)
top_types = df['TypeName'].value_counts().head(5)

# Price distribution plot
fig_price = px.histogram(df, x='Price', nbins=40, title='Laptop Price Distribution', color_discrete_sequence=['#636EFA'])

# Top companies bar plot
fig_companies = px.bar(top_companies, x=top_companies.index, y=top_companies.values, title='Top 5 Companies by Count', color_discrete_sequence=['#EF553B'])

# Top types bar plot
fig_types = px.bar(top_types, x=top_types.index, y=top_types.values, title='Top 5 Laptop Types', color_discrete_sequence=['#00CC96'])

# Modern dashboard layout
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
app.layout = dbc.Container([
    html.H1('Laptop Data Insights', style={'textAlign': 'center', 'marginTop': 30}),
    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4('Average Price', className='card-title'),
                html.H2('₹' + str(int(avg_price)), className='card-text'),
            ])
        ], color='primary', inverse=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4('Top Company', className='card-title'),
                html.H2(top_companies.index[0], className='card-text'),
            ])
        ], color='info', inverse=True), width=4),
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4('Most Common Type', className='card-title'),
                html.H2(top_types.index[0], className='card-text'),
            ])
        ], color='success', inverse=True), width=4),
    ], className='mb-4'),
    dbc.Row([
        dbc.Col(dcc.Graph(figure=fig_price), width=6),
        dbc.Col(dcc.Graph(figure=fig_companies), width=3),
        dbc.Col(dcc.Graph(figure=fig_types), width=3),
    ]),
    html.Hr(),
    html.Div('Created with Julius AI', style={'textAlign': 'center', 'color': '#888', 'marginTop': 20})
], fluid=True)

# Save dashboard as HTML for download
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>Laptop Data Insights Dashboard</title>
        {%favicon%}
        {%css%}
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

# # Run the Dash app and save as HTML using dash's built-in tools
# # Instead, use dash's to_html for static export
# from dash import to_html
# with open('laptop_dashboard.html', 'w', encoding='utf-8') as f:
#     f.write(to_html(app))

# print('Dashboard created and saved as laptop_dashboard.html')