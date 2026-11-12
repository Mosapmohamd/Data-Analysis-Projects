# Sales Dashboard (Power BI)

A single-page Power BI report built on an e-commerce orders dataset covering Indian states and cities.

## Contents
KPI cards, bar and donut charts, a line chart, a line-and-column combo chart and a slicer, covering sales amount, profit, quantity, categories, payment modes and geography.

## Data
| File | Columns | In this repo |
|---|---|---|
| `Details.csv` | Order ID, Amount, Profit, Quantity, Category, Sub-Category, PaymentMode | ✅ |
| `Orders.csv` | Order ID, Order Date, customer name, State, City | ❌ Not included (it contains a customer-name column) |

### Data embedded in the report
`First Report.pbix` stores its imported data inside the file, **including the Orders table**. One visual, a line-and-column combo chart, plots sales amount by customer, so **first-name-only customer values are displayed in the report and stored in its data model**. The other embedded Orders columns are Order ID, Order Date, State and City. There are no surnames or contact details. The source appears to be a public sample e-commerce dataset. The raw `Orders.csv` itself is not distributed.

## How to Open
Open `First Report.pbix` in Power BI Desktop. The report opens with the data already imported. A data refresh needs both source CSVs. Only `Details.csv` is provided here, so supply your own `Orders.csv` with the columns above if you want to refresh.

## Author

**Mosap Abdel-Ghany**: [github.com/Mosapmohamd](https://github.com/Mosapmohamd)
