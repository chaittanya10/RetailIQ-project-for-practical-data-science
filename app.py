from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="RetailIQ | Sales Intelligence", page_icon="◈", layout="wide", initial_sidebar_state="expanded")

NAVY = "#F3F7F4"
GREEN = "#32D583"
MINT = "#00F5A0"
MUTED = "#9AA89D"
BG = "#080D0A"

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
.stApp {{ background: {BG}; color: {NAVY}; }}
[data-testid="stSidebar"] {{ background: #050806; border-right: 1px solid #1C2B20; }}
[data-testid="stSidebar"] * {{ color: #E7F4EA; }}
[data-testid="stSidebar"] [data-testid="stFileUploader"] {{ background: #101812; border: 1px solid #263A2B; border-radius: 12px; padding: 8px; }}
.block-container {{ padding-top: 2rem; padding-bottom: 2rem; max-width: 1500px; }}
.hero {{ background: linear-gradient(115deg,#050806 0%,#0D1B12 58%,#123D25 100%); border:1px solid #1F402C; padding:27px 32px; border-radius:18px; color:white; margin-bottom:22px; box-shadow:0 12px 30px rgba(0,0,0,.3); }}
.hero h1 {{ color:#F3FFF6; font-size:30px; margin:0 0 5px 0; font-weight:800; letter-spacing:-.7px; }}
.hero p {{ color:#B5CDBB; font-size:14px; margin:0; }}
.eyebrow {{ text-transform:uppercase; letter-spacing:1.7px; color:{GREEN}; font-weight:700; font-size:10px; margin-bottom:8px; }}
.metric {{ background:#101812; border:1px solid #203528; border-radius:15px; padding:18px 20px; box-shadow:0 3px 12px rgba(0,0,0,.16); min-height:116px; }}
.metric-label {{ color:#9AA89D; font-size:12px; font-weight:600; margin-bottom:10px; }}
.metric-value {{ color:#F3FFF6; font-size:27px; font-weight:800; letter-spacing:-.7px; }}
.metric-note {{ color:{GREEN}; font-size:11px; margin-top:6px; }}
.section-title {{ color:#ECFDF3; font-size:17px; font-weight:750; margin:7px 0 0 0; }}
.section-sub {{ color:#89988D; font-size:11px; margin:2px 0 6px 0; }}
.insight {{ background:#101812; border:1px solid #203528; border-radius:13px; padding:14px 16px; min-height:78px; }}
.insight-label {{ color:#9AA89D; font-size:11px; font-weight:600; }}
.insight-value {{ color:#F3FFF6; font-size:17px; font-weight:750; margin-top:4px; }}
div[data-testid="stDataFrame"] {{ border:1px solid #203528; border-radius:12px; overflow:hidden; }}
</style>
""", unsafe_allow_html=True)

REQUIRED = {"order_date", "product", "category", "region", "quantity", "unit_price"}
SAMPLE = Path(__file__).parent / "sample_sales.xlsx"

@st.cache_data(show_spinner=False)
def load_workbook(file):
    return pd.read_excel(file)

def money(value):
    return f"₹{value:,.0f}"

def chart_theme(fig, height=320):
    fig.update_layout(
        height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#B3C0B6", size=11),
        margin=dict(l=8, r=10, t=14, b=8), legend=dict(orientation="h", y=1.12, x=0),
        xaxis=dict(showgrid=False, linecolor="#26372B", tickfont=dict(color="#A9B8AD")),
        yaxis=dict(showgrid=True, gridcolor="#1C2A20", zeroline=False, tickfont=dict(color="#A9B8AD")),
    )
    return fig

st.sidebar.markdown("<div style='font-size:19px;font-weight:800;color:#F3FFF6;margin:8px 0 2px'>◈ RetailIQ</div><div style='font-size:11px;color:#9AA89D;margin-bottom:24px'>SALES INTELLIGENCE</div>", unsafe_allow_html=True)
st.sidebar.markdown("#### DATA SOURCE")
uploaded = st.sidebar.file_uploader("Upload an Excel workbook", type=["xlsx", "xls"])
st.sidebar.markdown("---")

try:
    raw = load_workbook(uploaded) if uploaded else load_workbook(SAMPLE)
except Exception as exc:
    st.error(f"Could not open the Excel file: {exc}")
    st.stop()

df = raw.copy()
df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
missing = REQUIRED - set(df.columns)
if missing:
    st.error("Required columns are missing: " + ", ".join(sorted(missing)))
    st.info("Required columns: order_date, product, category, region, quantity, unit_price. Column names with spaces are also accepted.")
    st.dataframe(raw.head(8), use_container_width=True)
    st.stop()

df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
invalid_rows = int(df[["order_date", "quantity", "unit_price"]].isna().any(axis=1).sum())
df = df.dropna(subset=["order_date", "quantity", "unit_price"])
df = df[df["quantity"] >= 0]
df["revenue"] = df["quantity"] * df["unit_price"]
if df.empty:
    st.warning("No valid rows were found. Check the date, quantity, and unit_price columns.")
    st.stop()

st.markdown("<div class='hero'><div class='eyebrow'>BUSINESS PERFORMANCE OVERVIEW</div><h1>Retail Sales Dashboard</h1><p>Explore sales performance, identify top performers, and make better business decisions.</p></div>", unsafe_allow_html=True)

st.sidebar.markdown("#### FILTERS")
region_options = sorted(df["region"].dropna().astype(str).unique())
category_options = sorted(df["category"].dropna().astype(str).unique())
selected_regions = st.sidebar.multiselect("Region", region_options, default=region_options)
selected_categories = st.sidebar.multiselect("Category", category_options, default=category_options)
date_min, date_max = df.order_date.min().date(), df.order_date.max().date()
dates = st.sidebar.date_input("Date range", value=(date_min, date_max), min_value=date_min, max_value=date_max)
if isinstance(dates, (tuple, list)) and len(dates) == 2:
    start_date, end_date = dates
else:
    start_date, end_date = date_min, date_max

filtered = df[df.region.astype(str).isin(selected_regions) & df.category.astype(str).isin(selected_categories)]
filtered = filtered[filtered.order_date.dt.date.between(start_date, end_date)]
if filtered.empty:
    st.info("No sales records match these filters. Try changing your selections.")
    st.stop()

revenue = filtered.revenue.sum()
order_count = filtered.order_id.nunique() if "order_id" in filtered.columns else len(filtered)
units = filtered.quantity.sum()
aov = revenue / order_count if order_count else 0
metrics = [("TOTAL REVENUE", money(revenue), "Sales in selected period"), ("TOTAL ORDERS", f"{order_count:,.0f}", "Unique customer orders"), ("UNITS SOLD", f"{units:,.0f}", "Total products sold"), ("AVG. ORDER VALUE", money(aov), "Revenue per order")]
cols = st.columns(4)
for col, (label, value, note) in zip(cols, metrics):
    col.markdown(f"<div class='metric'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>↗ &nbsp;{note}</div></div>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Sales performance</div><div class='section-sub'>Breakdown for the selected date range and filters</div>", unsafe_allow_html=True)
monthly = (filtered.assign(month=filtered.order_date.dt.to_period("M").dt.to_timestamp())
           .groupby("month", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique") if "order_id" in filtered.columns else ("revenue", "size")))
category_sales = filtered.groupby("category", as_index=False).revenue.sum().sort_values("revenue", ascending=False)
left, right = st.columns([1.65, 1])
with left:
    st.markdown("<div class='section-title'>Revenue over time</div><div class='section-sub'>Monthly sales trend</div>", unsafe_allow_html=True)
    fig = px.area(monthly, x="month", y="revenue", color_discrete_sequence=[GREEN])
    fig.update_traces(line=dict(width=3), fillcolor="rgba(50,213,131,0.14)", hovertemplate="%{x|%b %Y}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
    fig.update_yaxes(title=None, tickprefix="₹", tickformat="~s")
    fig.update_xaxes(title=None, tickformat="%b '%y")
    st.plotly_chart(chart_theme(fig, 345), use_container_width=True, config={"displayModeBar": False})
with right:
    st.markdown("<div class='section-title'>Sales by category</div><div class='section-sub'>Revenue contribution by product group</div>", unsafe_allow_html=True)
    fig = px.pie(category_sales, names="category", values="revenue", hole=.68, color_discrete_sequence=[GREEN, MINT, "#A3E635", "#22C55E", "#86EFAC", "#14B8A6"])
    fig.update_traces(textposition="outside", textinfo="percent", hole=0.68, marker=dict(line=dict(color="#080D0A", width=3)), hovertemplate="%{label}<br>₹%{value:,.0f} (%{percent})<extra></extra>")
    fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-.08, x=0), annotations=[dict(text=f"{money(revenue)}<br><span style='font-size:10px;color:#9AA89D'>REVENUE</span>", x=.5, y=.5, showarrow=False, font=dict(size=16, color="#F3FFF6"))])
    st.plotly_chart(chart_theme(fig, 345), use_container_width=True, config={"displayModeBar": False})

left, right = st.columns(2)
with left:
    st.markdown("<div class='section-title'>Top 10 products</div><div class='section-sub'>Products ranked by revenue</div>", unsafe_allow_html=True)
    top_products = filtered.groupby("product", as_index=False).revenue.sum().nlargest(10, "revenue").sort_values("revenue")
    fig = px.bar(top_products, x="revenue", y="product", orientation="h", color="revenue", color_continuous_scale=[[0, "#14532D"], [1, MINT]])
    fig.update_layout(coloraxis_showscale=False, yaxis=dict(showgrid=False, title=None), xaxis=dict(title=None, tickprefix="₹", tickformat="~s", showgrid=True, gridcolor="#1C2A20"))
    fig.update_traces(hovertemplate="%{y}<br>Revenue: ₹%{x:,.0f}<extra></extra>")
    st.plotly_chart(chart_theme(fig, 350), use_container_width=True, config={"displayModeBar": False})
with right:
    st.markdown("<div class='section-title'>Regional performance</div><div class='section-sub'>Revenue and orders across regions</div>", unsafe_allow_html=True)
    region_sales = filtered.groupby("region", as_index=False).agg(revenue=("revenue", "sum"), orders=("order_id", "nunique") if "order_id" in filtered.columns else ("revenue", "size"))
    fig = px.bar(region_sales, x="region", y="revenue", color="region", color_discrete_sequence=[GREEN, MINT, "#A3E635", "#22C55E", "#86EFAC"])
    fig.update_layout(showlegend=False, xaxis_title=None, yaxis_title=None, yaxis=dict(tickprefix="₹", tickformat="~s"))
    fig.update_traces(hovertemplate="%{x}<br>Revenue: ₹%{y:,.0f}<extra></extra>")
    st.plotly_chart(chart_theme(fig, 350), use_container_width=True, config={"displayModeBar": False})

st.markdown("<div class='section-title'>Business highlights</div><div class='section-sub'>Top-performing segments in the current selection</div>", unsafe_allow_html=True)
best_cat = category_sales.iloc[0]
product_totals = filtered.groupby("product").revenue.sum()
best_product = product_totals.idxmax()
best_month = monthly.loc[monthly.revenue.idxmax()]
highlights = st.columns(3)
for col, label, value in [(highlights[0], "LEADING CATEGORY", f"{best_cat.category} · {money(best_cat.revenue)}"), (highlights[1], "TOP PRODUCT", str(best_product)), (highlights[2], "BEST MONTH", f"{best_month.month:%b %Y} · {money(best_month.revenue)}")]:
    col.markdown(f"<div class='insight'><div class='insight-label'>{label}</div><div class='insight-value'>{value}</div></div>", unsafe_allow_html=True)

if invalid_rows:
    st.warning(f"{invalid_rows} rows had a missing or invalid date, quantity, or price and were excluded from the analysis.")
with st.expander("View filtered records and data quality"):
    q1, q2, q3 = st.columns(3)
    q1.metric("Rows in view", f"{len(filtered):,}")
    q2.metric("Missing cells", f"{int(filtered.isna().sum().sum()):,}")
    q3.metric("Unique products", f"{filtered['product'].nunique():,}")
    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.download_button("⬇  Download filtered CSV", filtered.to_csv(index=False).encode("utf-8-sig"), "retail_sales_filtered.csv", "text/csv")

st.markdown("<div style='text-align:center;color:#829187;font-size:11px;padding:25px 0 4px'>RETAILIQ &nbsp;·&nbsp; PRACTICAL DATA SCIENCE PROJECT</div>", unsafe_allow_html=True)
