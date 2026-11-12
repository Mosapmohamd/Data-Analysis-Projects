# Telangana Tourism Visitors Analysis (Power BI)

An analysis of domestic and foreign visitors to the districts of Telangana (India) from 2016 to 2019, answering a set of research questions with a Power BI report and a presentation.

## Workflow
1. `python code for joining csv files.py` merges the yearly files in `domestic_visitors/` and `foreign_visitors/` into `domestic_combined.csv` and `foreign_combined.csv` (pandas + glob).
2. The Power BI report answers the questions page by page: **Home Page · Question 1 · Questions 2 & 3 · Questions 4–8 · Districts Insights**.
3. Findings are summarised in `Telangana Tourism Insights PPT.pptx`.

## Files
| File | Description |
|---|---|
| `Telegana toursim Visitors Analysis.pbix` | Power BI report |
| `Telangana Tourism Insights PPT.pptx` | Insights presentation |
| `domestic_visitors/`, `foreign_visitors/` | Yearly source CSVs (2016–2019) |
| `domestic_combined.csv`, `foreign_combined.csv` | Merged datasets |
| `Additional Data.csv` | Extra data used in the report |
| `metadata.txt`, `instructions for using dataset.txt` | Column descriptions and task brief |
| `python code for joining csv files.py` | Merge script |

The research-questions PDF and the state statistical abstract PDF from the original working folder are third-party documents and are not included.

## Video Demo
[Google Drive link](https://drive.google.com/file/d/1gNfF8bkBdPjlFkEiwVAZtyI1t-Jw86uQ/view?usp=sharing)

## How to Run
```bash
pip install pandas
python "python code for joining csv files.py"
```
Then open the `.pbix` in Power BI Desktop.

## Author

**Mosap Abdel-Ghany**: [github.com/Mosapmohamd](https://github.com/Mosapmohamd)
