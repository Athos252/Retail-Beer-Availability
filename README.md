# Retail Beer Availability Analysis

## Overview
This project analyzes retail beer availability using an automated data pipeline. Python scripts collect and structure daily data, which is then analyzed in Excel and visualized in Power BI to identify product availability trends across retail locations.

---

## Business Problem
For breweries and suppliers, visibility into retail stock levels is critical for understanding distribution performance and identifying gaps in product availability.

This project was built to:
- Track product availability across stores
- Identify patterns in stock presence and gaps
- Support data-driven decisions around distribution and product performance

---

## Tools & Technologies
- Python (data extraction, automation)
- Power BI (dashboarding, data visualization)
- Excel (data structuring and analysis)
- SQL concepts (relational data, joins, aggregation)

---

## Workflow

1. **Product List Generation**
   - `listmaker.py` generates lists of product URLs to be tracked

2. **Data Collection**
   - `scraper.py` collects product and store-level availability data
   - Automatically processes multiple products using generated SKU lists

3. **Data Storage**
   - Raw data is stored in structured datasets

4. **Data Preparation**
   - Data is cleaned and organized for analysis

5. **Analysis & Visualization**
   - Excel is used for intermediate analysis
   - Power BI dashboard visualizes trends and insights

6. **Automation**
   - A batch script (`runscraper.bat`) enables the pipeline to run without manual input
   - The process is scheduled to run daily, capturing end-of-day stock as the next day's availability

---

## Project Structure
Retail-Beer-Availability/
│
├── Data/
│ ├── daily_pulls/
│ ├── import_files/
│ └── productlists/
│
├── scraper.py
├── listmaker.py
├── retail_beer_availability.pbix

---

## Key Outputs
- Automated dataset of retail beer availability
- Structured data for analysis and reporting
- Power BI dashboard highlighting:
  - Product availability trends
  - Store-level performance
  - Distribution insights

---

## Sample Insights
- Product availability varies significantly across retail locations
- Certain SKUs show inconsistent presence, indicating distribution gaps
- Daily tracking allows identification of recurring stock issues

---

## Notes
- Sample data is included for demonstration purposes
- Full datasets are excluded to keep the repository clean and lightweight
