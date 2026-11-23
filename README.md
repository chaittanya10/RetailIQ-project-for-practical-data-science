# RetailIQ — Retail Sales Intelligence Dashboard

RetailIQ is an interactive dashboard for exploring retail sales data from an Excel workbook. It is built with Python, Streamlit, pandas, and Plotly.

## Dashboard preview

![RetailIQ sales dashboard](screenshots/Screenshot%202026-11-23%20124439.png)

## Features

- KPI summary for total revenue, orders, units sold, and average order value
- Monthly revenue trend
- Revenue breakdown by category, product, and region
- Interactive date, region, and category filters
- Data preview and data-quality indicators
- Download of filtered records as a CSV file
- Dark black-and-green dashboard theme

## Sample data

The project includes `sample_sales.xlsx`, a practice workbook with 300 sample sales records. It covers 10 products, 4 categories, and 4 regions from November 2025 to October 2026.

The sample data is for demonstration and learning. It does not represent actual business transactions.

## Requirements

- Python 3.10 or later
- Streamlit
- pandas
- Plotly
- openpyxl

## Run the dashboard

Open a terminal in the project folder and install the required packages:

```powershell
py -m pip install streamlit pandas plotly openpyxl
```

Start the app:

```powershell
py -m streamlit run app.py
```

The dashboard will open in your browser. Keep the terminal window open while using it. Press `Ctrl+C` in the terminal to stop the app.

## Use your own Excel workbook

Use the **Upload an Excel workbook** control in the sidebar to select an `.xlsx` or `.xls` file.

The workbook must include these columns:

| Column | Description |
|---|---|
| `order_date` | Date of the order |
| `product` | Product name |
| `category` | Product category |
| `region` | Sales region |
| `quantity` | Number of units sold |
| `unit_price` | Price per unit |

The `order_id` column is optional. When present, the dashboard uses it to count distinct orders. Column names with spaces are accepted; for example, `Order Date` is recognized as `order_date`.

Revenue is calculated as:

```text
Revenue = Quantity × Unit Price
```

Rows with invalid dates, quantities, or prices are excluded from the analysis. Negative quantities are also excluded.

## Repository contents

```text
RetailIQ/
├── app.py
├── sample_sales.xlsx
├── presentation.pptx
└── screenshots/
```

## Project question

Which products, categories, regions, and months contribute most to sales revenue?
