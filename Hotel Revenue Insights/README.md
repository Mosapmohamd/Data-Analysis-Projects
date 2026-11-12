# Hotel Revenue Insights: Hospitality Domain (Power BI)

A Power BI dashboard analysing bookings and revenue for the fictional **AtliQ Grands** hotel chain (properties in Delhi, Mumbai and other cities).

## What's Inside
- **Dashboard** and **Dashboard 2** pages: KPI cards, booking-platform and room-class breakdowns, trend lines, slicers for city, room type and period.
- KPI drill pages: **Revenue, ADR, RevPAR, DSRN, DBRN, DURN, Realisation %**, plus tooltip pages for Revenue, RevPAR, DSRN, Occupancy, ADR and Realisation.

## Data Model (star schema)
| File | Grain |
|---|---|
| `fact_bookings.csv` | One row per booking: dates, guests, room category, platform, rating, status, revenue generated/realised |
| `fact_aggregated_bookings.csv` | Successful bookings vs capacity per property, room and date |
| `dim_hotels.csv` | Property id, name, category, city |
| `dim_rooms.csv` | Room id and class |
| `dim_date.csv` | Calendar attributes |

## Files
`Revenue Insights-Hotels.pbix` (report) · `Revenue Insights-Hotels.pdf` (PDF export of the report) · the CSVs above.

## How to Open
Open the `.pbix` in Power BI Desktop. To refresh, point the data source to the CSVs in this folder. The icon images from the original working folder are embedded in the report and are not shipped separately.

## Author

**Mosap Abdel-Ghany**: [github.com/Mosapmohamd](https://github.com/Mosapmohamd)
