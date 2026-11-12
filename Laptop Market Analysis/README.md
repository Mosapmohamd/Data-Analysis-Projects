# Laptop Market Analysis (Python + Plotly Dash)

Analysis of a laptop specifications and prices dataset, with feature engineering and an interactive dark-theme Dash dashboard.

## Features
- Cleaning and feature engineering: RAM/weight to numbers, CPU brand and speed, GPU brand, touchscreen/IPS flags, resolution and **PPI**, storage split into HDD/SSD/Flash/Hybrid.
- `app.py` dashboard: info bar, filters (company, type, RAM, price, screen size, touchscreen), five tabs (**Overview, Price Analysis, Specifications, Manufacturers, Raw Data**) and CSV export of the filtered data.
- `dashboard_simple.py`: a smaller Dash + Bootstrap dashboard with key insights.
- `CODE_WALKTHROUGH.md`: a line-by-line explanation of the dashboard code.

## Files
`app.py` · `dashboard_simple.py` · `project note book.ipynb` · `analytical thinking.ipynb` · `laptop_data.csv` · `Updataed_laptop_data.csv` · `CODE_WALKTHROUGH.md`

## Run
```bash
pip install dash dash-bootstrap-components plotly pandas numpy
python dashboard_simple.py
python app.py
```

**Note:** `app.py` loads the data from a hard-coded Windows path (`C:\Users\DELL\Desktop\Data Analysis Task\laptop_data.csv`) and shows an empty dashboard if that path does not exist. Change it to `laptop_data.csv` to run it from this folder. `dashboard_simple.py` reads `laptop_data.csv` from the current directory.

## Author

**Mosap Abdel-Ghany**: [github.com/Mosapmohamd](https://github.com/Mosapmohamd)
