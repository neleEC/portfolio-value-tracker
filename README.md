# Portfolio Value Tracker

A simple GitHub Actions–powered bot that automatically scrapes market data and commits updated time-series data to the repository.

---

## Repository Structure

- **portfolio.xlsx** – Input file containing your portfolio holdings.
- **main.py** – Main Python script that performs scraping and calculations.
- **time_series.pkl** – Output file storing the current portfolio values (automatically updated to keep track of the historical).
- **.github/workflows/automatic_run.yml** – GitHub Actions workflow file controlling automatic execution.

---

##  Input File: `portfolio.xlsx`

The Excel file must contain the following columns:

| Column | Description |
|---|---|
| **ISIN** |    The 12-character ISIN code of each security |
| **q**    |    Quantity held                               |
| **TYPE** | `  "ETF"` or `"EQUITY"`                        |


---

## What the Script Does at the scheduled time

- You can set the execution time by editing the `schedule` block in - **.github/workflows/automatic_run.yml**
- Manual execution is also possible using the **workflow_dispatch** trigger.
- When executed the script:

1. Reads `portfolio.xlsx`  
2. Scrapes current prices for ETFs and equities from justETF.com  (this can be edited to scrape additional information) 
3. Retains the 'quantity' held (from portfolio.xlsx), and the current price (webscrapped from justEtf) of each position 
4. Updates `time_series.pkl` with new prices and quantities
5. Automatically commits the updated file back to the repository

---

##Output

- **time_series.pkl** – A pandas DataFrame containing historical prices and quantities for all holdings.

---

## Notes

- Ensure `portfolio.xlsx` is up-to-date; any changes to quantities will be reflected in the next run.
- Ensure to set up the time of execution of the code `.github/workflows/automatic_run.yml`, at the moment it is set on manual execution with the **workflow_dispatch** trigger.





