import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime

# Initialize the Dash app with dark theme
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server

# Set dark theme colors
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'panel': '#1E1E1E',
    'highlight': '#2A3F5F',
    'accent': '#636EFA'
}

# Load the data
try:
    df = pd.read_csv(r"C:\Users\DELL\Desktop\Data Analysis Task\laptop_data.csv")
except:
    # Fallback if path doesn't work
    df = pd.DataFrame()
df_name="Updated_laptop_data.csv"
# Data cleaning (same as notebook)
if not df.empty:
    df.drop(columns=['Unnamed: 0'], inplace=True)
    df['Ram'] = df['Ram'].str.replace('GB','').astype('int32')
    df['Weight'] = df['Weight'].str.replace('kg','').astype('float32')
    
    # Extract CPU information
    df['Cpu Brand'] = df['Cpu'].str.split().str[0]
    df['Cpu Speed'] = df['Cpu'].str.extract(r'(\d+\.\d+)GHz')[0].astype(float)
    
    # Extract GPU information
    df['Gpu Brand'] = df['Gpu'].str.split().str[0]
    
    # Extract Screen Resolution info
    df['Touchscreen'] = df['ScreenResolution'].str.contains('Touchscreen').astype(int)
    df['IPS'] = df['ScreenResolution'].str.contains('IPS').astype(int)
    df['Resolution'] = df['ScreenResolution'].str.split().str[-1]
    df['X_res'] = df['Resolution'].str.split('x').str[0].astype(int)
    df['Y_res'] = df['Resolution'].str.split('x').str[1].astype(int)
    df['PPI'] = (((df['X_res']**2 + df['Y_res']**2)**0.5)/df['Inches']).astype(float)
    
    # Extract Memory information
    df['Memory'] = df['Memory'].astype(str).replace('\.0', '', regex=True)
    df['Memory'] = df['Memory'].str.replace('GB', '')
    df['Memory'] = df['Memory'].str.replace('TB', '000')
    df['Memory'] = df['Memory'].str.split('+')
    
    df['HDD'] = 0
    df['SSD'] = 0
    df['Flash Storage'] = 0
    df['Hybrid'] = 0
    
    for i in range(len(df['Memory'])):
        for j in df['Memory'][i]:
            if 'HDD' in j:
                df['HDD'].iloc[i] = int(j.split('HDD')[0])
            elif 'SSD' in j:
                df['SSD'].iloc[i] = int(j.split('SSD')[0])
            elif 'Flash Storage' in j:
                df['Flash Storage'].iloc[i] = int(j.split('Flash Storage')[0])
            elif 'Hybrid' in j:
                df['Hybrid'].iloc[i] = int(j.split('Hybrid')[0])

# App layout with dark theme
app.layout = html.Div(style={'backgroundColor': colors['background'], 'color': colors['text']}, children=[
    # Header with logo and title
    html.Div([
        html.Img(src='https://cdn-icons-png.flaticon.com/512/2115/2115955.png', 
                style={'height': '60px', 'margin-right': '20px'}),
        html.H1("Laptop Market Analysis Dashboard", 
               style={'display': 'inline', 'verticalAlign': 'middle'}),
    ], style={'padding': '20px', 'borderBottom': f'1px solid {colors["highlight"]}'}),
    
    # Info bar with stats
    html.Div(id='info-bar', style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'padding': '15px',
        'backgroundColor': colors['panel'],
        'borderRadius': '5px',
        'margin': '10px'
    }),
    
    # Main content area
    html.Div([
        # Left sidebar with filters
        html.Div([
            html.H3("Filters", style={'borderBottom': f'1px solid {colors["highlight"]}', 'paddingBottom': '10px'}),
            
            html.Label("Company:"),
            dcc.Dropdown(
                id='company-filter',
                options=[{'label': i, 'value': i} for i in (df['Company'].unique() if not df.empty else [])],
                multi=True,
                placeholder="Select companies..."
            ),
            
            html.Br(),
            html.Label("Laptop Type:"),
            dcc.Dropdown(
                id='type-filter',
                options=[{'label': i, 'value': i} for i in (df['TypeName'].unique() if not df.empty else [])],
                multi=True,
                placeholder="Select types..."
            ),
            
            html.Br(),
            html.Label("RAM (GB):"),
            dcc.RangeSlider(
                id='ram-slider',
                min=0,
                max=64,
                step=4,
                value=[0, 64],
                marks={i: str(i) for i in range(0, 65, 8)}
            ),
            
            html.Br(),
            html.Label("Price Range:"),
            dcc.RangeSlider(
                id='price-slider',
                min=0,
                max=df['Price'].max() if not df.empty else 100000,
                step=10000,
                value=[0, df['Price'].max() if not df.empty else 100000],
                marks={i: f'₹{i//1000}k' for i in range(0, int(df['Price'].max() if not df.empty else 100000)+1, 50000)}
            ),
            
            html.Br(),
            html.Label("Screen Size (inches):"),
            dcc.RangeSlider(
                id='inches-slider',
                min=df['Inches'].min() if not df.empty else 10,
                max=df['Inches'].max() if not df.empty else 20,
                step=0.1,
                value=[df['Inches'].min() if not df.empty else 10, df['Inches'].max() if not df.empty else 20],
                marks={i: str(i) for i in range(10, 21, 2)}
            ),
            
            html.Br(),
            html.Label("Touchscreen:"),
            dcc.RadioItems(
                id='touchscreen-filter',
                options=[
                    {'label': 'All', 'value': 'all'},
                    {'label': 'Yes', 'value': 'yes'},
                    {'label': 'No', 'value': 'no'}
                ],
                value='all',
                labelStyle={'display': 'inline-block', 'marginRight': '10px'}
            ),
            
            html.Br(),
            html.Button('Reset Filters', id='reset-filters', n_clicks=0, 
                       style={'width': '100%', 'backgroundColor': colors['accent']})
            
        ], className='three columns', style={
            'backgroundColor': colors['panel'],
            'padding': '20px',
            'borderRadius': '5px',
            'margin': '10px'
        }),
        
        # Main content area with tabs
        html.Div([
            dcc.Tabs(id='tabs', value='tab-overview', children=[
                dcc.Tab(label='Overview', value='tab-overview', style={'backgroundColor': colors['panel']}),
                dcc.Tab(label='Price Analysis', value='tab-price', style={'backgroundColor': colors['panel']}),
                dcc.Tab(label='Specifications', value='tab-specs', style={'backgroundColor': colors['panel']}),
                dcc.Tab(label='Manufacturers', value='tab-manufacturers', style={'backgroundColor': colors['panel']}),
                dcc.Tab(label='Raw Data', value='tab-data', style={'backgroundColor': colors['panel']})
            ], colors={
                'border': colors['highlight'],
                'primary': colors['accent'],
                'background': colors['panel']
            }),
            
            html.Div(id='tabs-content', style={'padding': '20px'})
        ], className='nine columns')
    ], className='row')
])

# Callback for info bar
@app.callback(
    Output('info-bar', 'children'),
    [Input('company-filter', 'value'),
     Input('type-filter', 'value'),
     Input('ram-slider', 'value'),
     Input('price-slider', 'value'),
     Input('inches-slider', 'value'),
     Input('touchscreen-filter', 'value')]
)
def update_info_bar(companies, types, ram_range, price_range, inches_range, touchscreen):
    filtered_df = df.copy()
    
    # Apply filters
    if companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(companies)]
    if types:
        filtered_df = filtered_df[filtered_df['TypeName'].isin(types)]
    
    filtered_df = filtered_df[
        (filtered_df['Ram'] >= ram_range[0]) & 
        (filtered_df['Ram'] <= ram_range[1]) &
        (filtered_df['Price'] >= price_range[0]) & 
        (filtered_df['Price'] <= price_range[1]) &
        (filtered_df['Inches'] >= inches_range[0]) & 
        (filtered_df['Inches'] <= inches_range[1])
    ]
    
    if touchscreen == 'yes':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 1]
    elif touchscreen == 'no':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 0]
    
    # Calculate stats
    avg_price = f"₹{filtered_df['Price'].mean():,.0f}" if not filtered_df.empty else "N/A"
    min_price = f"₹{filtered_df['Price'].min():,.0f}" if not filtered_df.empty else "N/A"
    max_price = f"₹{filtered_df['Price'].max():,.0f}" if not filtered_df.empty else "N/A"
    count = len(filtered_df)
    avg_ram = f"{filtered_df['Ram'].mean():.1f} GB" if not filtered_df.empty else "N/A"
    
    return [
        html.Div([
            html.H5("Laptops", style={'color': colors['accent']}),
            html.H3(count)
        ], style={'textAlign': 'center'}),
        
        html.Div([
            html.H5("Avg Price", style={'color': colors['accent']}),
            html.H3(avg_price)
        ], style={'textAlign': 'center'}),
        
        html.Div([
            html.H5("Price Range", style={'color': colors['accent']}),
            html.H3(f"{min_price} - {max_price}")
        ], style={'textAlign': 'center'}),
        
        html.Div([
            html.H5("Avg RAM", style={'color': colors['accent']}),
            html.H3(avg_ram)
        ], style={'textAlign': 'center'}),
        
        html.Div([
            html.H5("Last Updated", style={'color': colors['accent']}),
            html.H3(datetime.now().strftime("%Y-%m-%d"))
        ], style={'textAlign': 'center'})
    ]

# Callback for reset filters button
@app.callback(
    [Output('company-filter', 'value'),
     Output('type-filter', 'value'),
     Output('ram-slider', 'value'),
     Output('price-slider', 'value'),
     Output('inches-slider', 'value'),
     Output('touchscreen-filter', 'value')],
    [Input('reset-filters', 'n_clicks')]
)
def reset_filters(n_clicks):
    return [None, None, [0, 64], [0, df['Price'].max() if not df.empty else 100000], 
            [df['Inches'].min() if not df.empty else 10, df['Inches'].max() if not df.empty else 20], 'all']

# Callback for tabs content
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('company-filter', 'value'),
     Input('type-filter', 'value'),
     Input('ram-slider', 'value'),
     Input('price-slider', 'value'),
     Input('inches-slider', 'value'),
     Input('touchscreen-filter', 'value')]
)
def render_tab_content(tab, companies, types, ram_range, price_range, inches_range, touchscreen):
    filtered_df = df.copy()
    
    # Apply filters
    if companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(companies)]
    if types:
        filtered_df = filtered_df[filtered_df['TypeName'].isin(types)]
    
    filtered_df = filtered_df[
        (filtered_df['Ram'] >= ram_range[0]) & 
        (filtered_df['Ram'] <= ram_range[1]) &
        (filtered_df['Price'] >= price_range[0]) & 
        (filtered_df['Price'] <= price_range[1]) &
        (filtered_df['Inches'] >= inches_range[0]) & 
        (filtered_df['Inches'] <= inches_range[1])
    ]
    
    if touchscreen == 'yes':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 1]
    elif touchscreen == 'no':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 0]
    
    if tab == 'tab-overview':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.pie(filtered_df, names='Company', title='Market Share by Company',
                                    color_discrete_sequence=px.colors.qualitative.Dark24)
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text'],
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                    )
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(
                        figure=px.pie(filtered_df, names='TypeName', title='Distribution by Laptop Type',
                                    color_discrete_sequence=px.colors.qualitative.Dark24)
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text'],
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                dcc.Graph(
                    figure=px.scatter(filtered_df, x='Inches', y='Price', color='Company',
                                    size='Ram', hover_data=['TypeName', 'Ram', 'Weight'],
                                    title='Price vs Screen Size (Colored by Company, Sized by RAM)',
                                    labels={'Inches': 'Screen Size (inches)', 'Price': 'Price (₹)'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text']
                    )
                )
            ]),
            
            html.Div([
                dcc.Graph(
                    figure=px.box(filtered_df, x='Company', y='PPI', color='Company',
                                title='Pixel Density (PPI) by Manufacturer',
                                labels={'PPI': 'Pixels Per Inch'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text'],
                        xaxis_title="",
                        showlegend=False
                    )
                )
            ])
        ])
    
    elif tab == 'tab-price':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(filtered_df, x='Price', nbins=30, 
                                          title='Price Distribution',
                                          color_discrete_sequence=[colors['accent']])
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text']
                        )
                    )
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(
                        figure=px.box(filtered_df, y='Price', color_discrete_sequence=[colors['accent']],
                                    title='Price Distribution (Box Plot)')
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text'],
                            showlegend=False
                        )
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                dcc.Graph(
                    figure=px.box(filtered_df, x='Company', y='Price', color='Company',
                                title='Price Distribution by Manufacturer',
                                labels={'Price': 'Price (₹)'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text'],
                        xaxis_title=""
                    )
                )
            ]),
            
            html.Div([
                dcc.Graph(
                    figure=px.box(filtered_df, x='TypeName', y='Price', color='TypeName',
                                title='Price Distribution by Laptop Type',
                                labels={'Price': 'Price (₹)'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text'],
                        xaxis_title="",
                        showlegend=False
                    )
                )
            ])
        ])
    
    elif tab == 'tab-specs':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(filtered_df, x='Ram', nbins=15,
                                          title='RAM Distribution',
                                          color_discrete_sequence=[colors['accent']])
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text']
                        )
                    )
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(filtered_df, x='Weight', nbins=20,
                                          title='Weight Distribution',
                                          color_discrete_sequence=[colors['accent']])
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text']
                        )
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.histogram(filtered_df, x='Inches', nbins=15,
                                          title='Screen Size Distribution',
                                          color_discrete_sequence=[colors['accent']])
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text']
                        )
                    )
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(
                        figure=px.scatter(filtered_df, x='Ram', y='Price', trendline='ols',
                                        title='RAM vs Price with Trendline',
                                        labels={'Ram': 'RAM (GB)', 'Price': 'Price (₹)'},
                                        color='Company')
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text']
                        )
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                dcc.Graph(
                    figure=px.scatter(filtered_df, x='Weight', y='Price', color='TypeName',
                                    title='Weight vs Price by Laptop Type',
                                    labels={'Weight': 'Weight (kg)', 'Price': 'Price (₹)'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text']
                    )
                )
            ])
        ])
    
    elif tab == 'tab-manufacturers':
        return html.Div([
            html.Div([
                html.Div([
                    dcc.Graph(
                        figure=px.bar(filtered_df['Company'].value_counts().reset_index(), 
                                     x='index', y='Company',
                                     title='Number of Models by Manufacturer',
                                     labels={'index': 'Manufacturer', 'Company': 'Count'},
                                     color='index',
                                     color_discrete_sequence=px.colors.qualitative.Dark24)
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text'],
                            xaxis_title="",
                            showlegend=False
                        )
                    )
                ], className='six columns'),
                
                html.Div([
                    dcc.Graph(
                        figure=px.bar(filtered_df.groupby('Company')['Price'].mean().reset_index(), 
                                     x='Company', y='Price',
                                     title='Average Price by Manufacturer',
                                     color='Company',
                                     color_discrete_sequence=px.colors.qualitative.Dark24)
                        .update_layout(
                            plot_bgcolor=colors['panel'],
                            paper_bgcolor=colors['panel'],
                            font_color=colors['text'],
                            xaxis_title="",
                            showlegend=False
                        )
                    )
                ], className='six columns')
            ], className='row'),
            
            html.Div([
                dcc.Graph(
                    figure=px.sunburst(filtered_df, path=['Company', 'TypeName'], 
                                      title='Laptop Types by Manufacturer',
                                      color_discrete_sequence=px.colors.qualitative.Dark24)
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text']
                    )
                )
            ]),
            
            html.Div([
                dcc.Graph(
                    figure=px.box(filtered_df, x='Company', y='Ram', color='Company',
                                title='RAM Distribution by Manufacturer',
                                labels={'Ram': 'RAM (GB)'})
                    .update_layout(
                        plot_bgcolor=colors['panel'],
                        paper_bgcolor=colors['panel'],
                        font_color=colors['text'],
                        xaxis_title="",
                        showlegend=False
                    )
                )
            ])
        ])
    
    elif tab == 'tab-data':
        return html.Div([
            html.H4('Filtered Data', style={'textAlign': 'center'}),
            dash_table.DataTable(
                id='datatable',
                columns=[{"name": i, "id": i} for i in filtered_df.columns],
                data=filtered_df.to_dict('records'),
                page_size=15,
                style_table={'overflowX': 'auto'},
                style_header={
                    'backgroundColor': colors['highlight'],
                    'color': colors['text'],
                    'fontWeight': 'bold'
                },
                style_cell={
                    'backgroundColor': colors['panel'],
                    'color': colors['text'],
                    'border': f'1px solid {colors["highlight"]}'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': '#222222'
                    }
                ],
                filter_action="native",
                sort_action="native",
                sort_mode="multi"
            ),
            
            html.Div([
                html.Button("Download CSV", id="btn_csv", style={'marginRight': '10px'}),
                dcc.Download(id="download-dataframe-csv")
            ], style={'marginTop': '20px'})
        ])

# Callback for downloading data
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    [State('company-filter', 'value'),
     State('type-filter', 'value'),
     State('ram-slider', 'value'),
     State('price-slider', 'value'),
     State('inches-slider', 'value'),
     State('touchscreen-filter', 'value')],
    prevent_initial_call=True
)
def download_data(n_clicks, companies, types, ram_range, price_range, inches_range, touchscreen):
    filtered_df = df.copy()
    
    # Apply filters
    if companies:
        filtered_df = filtered_df[filtered_df['Company'].isin(companies)]
    if types:
        filtered_df = filtered_df[filtered_df['TypeName'].isin(types)]
    
    filtered_df = filtered_df[
        (filtered_df['Ram'] >= ram_range[0]) & 
        (filtered_df['Ram'] <= ram_range[1]) &
        (filtered_df['Price'] >= price_range[0]) & 
        (filtered_df['Price'] <= price_range[1]) &
        (filtered_df['Inches'] >= inches_range[0]) & 
        (filtered_df['Inches'] <= inches_range[1])
    ]
    
    if touchscreen == 'yes':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 1]
    elif touchscreen == 'no':
        filtered_df = filtered_df[filtered_df['Touchscreen'] == 0]
    
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_laptops.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=7050)