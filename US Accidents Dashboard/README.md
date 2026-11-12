# US Accidents Dashboard (Plotly Dash)

Exploratory analysis of a sample of US road-accident records (Severity, Start_Time, location, weather and road-feature columns), plus an interactive dark-theme **Dash** dashboard.

## Files
| File | Description |
|---|---|
| `app.py` | Main Dash app "Accidents Dashboard". Tabs: **Overview, Time Analysis, Weather Analysis, Map, Data**. Runs on port 7050 |
| `dash for accidents.py` | Alternative version ("Traffic Accident Analysis") |
| `code (1).py` | Alternative Bootstrap version ("US Accidents Analysis Dashboard", port 8051) |
| `Acciedents.ipynb`, `app.ipynb` | Data exploration, feature engineering and a RandomForest severity model |
| `sampled_data_1.csv` | Sampled accident records used by the app (~3.7 MB) |
| `weather_incidents.csv` | Weather-related subset |
| `severity_predictor.joblib` | Saved model from the notebook work |

## Run
```bash
pip install dash plotly pandas numpy scikit-learn joblib
python app.py          # http://127.0.0.1:7050
```
`app.py` reads `sampled_data_1.csv` from the current working directory, so run it from this folder.

## Author

**Mosap Abdel-Ghany**: [github.com/Mosapmohamd](https://github.com/Mosapmohamd)
