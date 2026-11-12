# **Professional Training Session: Laptop Data Analysis Dashboard Code Walkthrough**

## **Introduction**
Welcome to this professional training session! Today, we'll break down every part of the **Laptop Data Analysis Dashboard** built with **Dash and Plotly**. This dashboard is designed to analyze laptop specifications, pricing trends, and market distribution with an advanced dark theme.

---

# **1. Dashboard Structure Overview**
The dashboard consists of:
- **Header** (Title & Logo)
- **Info Bar** (Key Statistics)
- **Filters Panel** (Interactive Controls)
- **Main Content Area** (Visualizations & Data Table)

---

# **2. Code Breakdown (Line-by-Line Explanation)**

## **2.1. Importing Libraries**
```python
import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from datetime import datetime
```
- **`dash`**: Framework for building web applications.
- **`dcc` (Dash Core Components)**: Interactive components like dropdowns, sliders, and graphs.
- **`html` (Dash HTML Components)**: HTML elements for layout.
- **`dash_table`**: For displaying data in a table format.
- **`pandas`**: Data manipulation and analysis.
- **`plotly.express` & `plotly.graph_objects`**: For interactive visualizations.
- **`numpy`**: Numerical computations.
- **`os` & `datetime`**: For file handling and timestamps.

---

## **2.2. Initializing the Dash App**
```python
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server
```
- **`app = dash.Dash()`**: Creates the Dash application.
- **`external_stylesheets`**: Adds default CSS styling.
- **`server = app.server`**: Required for deployment (e.g., on Heroku).

---

## **2.3. Dark Theme Color Scheme**
```python
colors = {
    'background': '#111111',
    'text': '#7FDBFF',
    'panel': '#1E1E1E',
    'highlight': '#2A3F5F',
    'accent': '#636EFA'
}
```
- Defines a **dark theme** with:
  - Dark background (`#111111`)
  - Light blue text (`#7FDBFF`)
  - Darker panels (`#1E1E1E`)
  - Highlight color (`#2A3F5F`)
  - Accent color (`#636EFA`)

---

## **2.4. Loading & Cleaning Data**
```python
try:
    df = pd.read_csv(r"C:\Users\DELL\Desktop\Data Analysis Task\laptop_data.csv")
except:
    df = pd.DataFrame()
```
- **`pd.read_csv()`**: Loads the laptop dataset.
- **`except`**: Fallback if the file path is invalid.

### **Data Cleaning Steps**
```python
if not df.empty:
    df.drop(columns=['Unnamed: 0'], inplace=True)
    df['Ram'] = df['Ram'].str.replace('GB','').astype('int32')
    df['Weight'] = df['Weight'].str.replace('kg','').astype('float32')
```
- **`drop()`**: Removes unnecessary column `Unnamed: 0`.
- **`str.replace()`**: Cleans `Ram` (removes "GB") and `Weight` (removes "kg").
- **`astype()`**: Converts to proper data types (`int32` for RAM, `float32` for Weight).

### **Feature Engineering**
```python
# Extract CPU Brand & Speed
df['Cpu Brand'] = df['Cpu'].str.split().str[0]
df['Cpu Speed'] = df['Cpu'].str.extract(r'(\d+\.\d+)GHz')[0].astype(float)

# Extract GPU Brand
df['Gpu Brand'] = df['Gpu'].str.split().str[0]

# Screen Resolution Features
df['Touchscreen'] = df['ScreenResolution'].str.contains('Touchscreen').astype(int)
df['IPS'] = df['ScreenResolution'].str.contains('IPS').astype(int)
df['Resolution'] = df['ScreenResolution'].str.split().str[-1]
df['X_res'] = df['Resolution'].str.split('x').str[0].astype(int)
df['Y_res'] = df['Resolution'].str.split('x').str[1].astype(int)
df['PPI'] = (((df['X_res']**2 + df['Y_res']**2)**0.5)/df['Inches']).astype(float)

# Memory Breakdown (HDD, SSD, Flash Storage, Hybrid)
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
```
- **CPU & GPU Extraction**: Splits text to get brand and speed.
- **Screen Features**: Detects `Touchscreen`, `IPS`, and calculates `PPI` (Pixels Per Inch).
- **Memory Breakdown**: Separates `HDD`, `SSD`, `Flash Storage`, and `Hybrid` storage.

---

## **2.5. Dashboard Layout**
### **Header Section**
```python
html.Div([
    html.Img(src='https://cdn-icons-png.flaticon.com/512/2115/2115955.png', 
            style={'height': '60px', 'margin-right': '20px'}),
    html.H1("Laptop Market Analysis Dashboard", 
           style={'display': 'inline', 'verticalAlign': 'middle'})
], style={'padding': '20px', 'borderBottom': f'1px solid {colors["highlight"]}'})
```
- **`html.Img()`**: Displays a laptop icon.
- **`html.H1()`**: Dashboard title.
- **`style`**: Custom CSS for alignment and borders.

### **Info Bar (Real-time Stats)**
```python
html.Div(id='info-bar', style={
    'display': 'flex',
    'justifyContent': 'space-around',
    'padding': '15px',
    'backgroundColor': colors['panel'],
    'borderRadius': '5px',
    'margin': '10px'
})
```
- Shows **laptop count, avg price, price range, avg RAM, last updated**.
- Uses **flexbox** for responsive layout.

### **Filters Panel (Left Sidebar)**
```python
html.Div([
    html.H3("Filters"),
    html.Label("Company:"),
    dcc.Dropdown(id='company-filter', options=[...], multi=True),
    html.Label("Laptop Type:"),
    dcc.Dropdown(id='type-filter', options=[...], multi=True),
    html.Label("RAM (GB):"),
    dcc.RangeSlider(id='ram-slider', min=0, max=64, step=4, value=[0, 64]),
    html.Label("Price Range:"),
    dcc.RangeSlider(id='price-slider', min=0, max=df['Price'].max(), step=10000),
    html.Label("Screen Size (inches):"),
    dcc.RangeSlider(id='inches-slider', min=10, max=20, step=0.1),
    html.Label("Touchscreen:"),
    dcc.RadioItems(id='touchscreen-filter', options=[...]),
    html.Button('Reset Filters', id='reset-filters')
], className='three columns')
```
- **Dropdowns**: For `Company` and `Type`.
- **Sliders**: For `RAM`, `Price`, and `Screen Size`.
- **Radio Buttons**: For `Touchscreen` filter.
- **Reset Button**: Clears all filters.

### **Main Content Area (Tabs)**
```python
dcc.Tabs(id='tabs', value='tab-overview', children=[
    dcc.Tab(label='Overview', value='tab-overview'),
    dcc.Tab(label='Price Analysis', value='tab-price'),
    dcc.Tab(label='Specifications', value='tab-specs'),
    dcc.Tab(label='Manufacturers', value='tab-manufacturers'),
    dcc.Tab(label='Raw Data', value='tab-data')
]),
html.Div(id='tabs-content')
```
- **5 Tabs**:
  1. **Overview** (Market share, scatter plots)
  2. **Price Analysis** (Histograms, box plots)
  3. **Specifications** (RAM, Weight, PPI trends)
  4. **Manufacturers** (Brand comparisons)
  5. **Raw Data** (Filterable table)

---

## **2.6. Callbacks (Interactive Logic)**
### **Info Bar Update**
```python
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
    filtered_df = apply_filters(df, companies, types, ram_range, price_range, inches_range, touchscreen)
    avg_price = f"₹{filtered_df['Price'].mean():,.0f}"
    return [
        html.Div([html.H5("Laptops"), html.H3(len(filtered_df))]),
        html.Div([html.H5("Avg Price"), html.H3(avg_price)])
    ]
```
- Updates stats when filters change.
- Uses **`apply_filters()`** (a helper function) to filter data.

### **Reset Filters**
```python
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
    return [None, None, [0, 64], [0, df['Price'].max()], [10, 20], 'all']
```
- Resets all filters to default values.

### **Tab Content Rendering**
```python
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
    filtered_df = apply_filters(df, companies, types, ram_range, price_range, inches_range, touchscreen)
    
    if tab == 'tab-overview':
        return overview_tab(filtered_df)
    elif tab == 'tab-price':
        return price_tab(filtered_df)
    elif tab == 'tab-specs':
        return specs_tab(filtered_df)
    elif tab == 'tab-manufacturers':
        return manufacturers_tab(filtered_df)
    elif tab == 'tab-data':
        return data_tab(filtered_df)
```
- Dynamically renders content based on **selected tab** and **filters**.

### **Download Data**
```python
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
    filtered_df = apply_filters(df, companies, types, ram_range, price_range, inches_range, touchscreen)
    return dcc.send_data_frame(filtered_df.to_csv, "filtered_laptops.csv")
```
- Exports filtered data as **CSV**.

---

# **3. Key Takeaways**
1. **Dash Components**:
   - `dcc.Graph` → Interactive charts.
   - `dcc.Dropdown` → Filter selection.
   - `dcc.RangeSlider` → Numeric range filters.
   - `dash_table.DataTable` → Display raw data.

2. **Callbacks**:
   - Connect UI elements (`Input`) to outputs (`Output`).
   - Use `State` to access values without triggering updates.

3. **Styling**:
   - Dark theme (`background`, `text`, `panel` colors).
   - Flexbox for responsive layouts.

4. **Data Processing**:
   - Clean and transform raw data.
   - Extract features (CPU, GPU, PPI, Memory).

---

# **4. Next Steps**
- **Deploy** the app (Heroku, AWS, or Dash Enterprise).
- **Add more visualizations** (e.g., correlation heatmap).
- **Improve performance** (caching, async loading).

---

# **Final Thoughts**
This dashboard is **fully interactive** and **production-ready**. It provides deep insights into laptop pricing, specifications, and market trends.  

Would you like a **live demo** or **additional customization**? 🚀