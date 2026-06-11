import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

from google.cloud import bigquery


st.set_page_config(
    page_title="E-commerce Price Intelligence",
    layout="wide"
)

st.title("E-commerce Price Intelligence Dashboard")

PROJECT_ID = "price-intel-prod"
DATASET_ID = "price_staging"


@st.cache_data
def load_data():
    client = bigquery.Client(project=PROJECT_ID)

    query_clean = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.clean_prices`
    """

    query_ts = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.price_timeseries`
    """

    query_intelligence = f"""
    SELECT *
    FROM `{PROJECT_ID}.{DATASET_ID}.price_intelligence`
    """

    df_clean = client.query(query_clean).to_dataframe()
    df_ts = client.query(query_ts).to_dataframe()
    df_intelligence = client.query(query_intelligence).to_dataframe()

    df_clean["scraped_at"] = pd.to_datetime(df_clean["scraped_at"])
    df_ts["scraped_at"] = pd.to_datetime(df_ts["scraped_at"])

    return df_clean, df_ts, df_intelligence


df_clean, df_ts, df_intelligence = load_data()

st.sidebar.header("Filters")

selected_site = st.sidebar.multiselect(
    "Website",
    options=sorted(df_clean["site_name"].dropna().unique()),
    default=sorted(df_clean["site_name"].dropna().unique())
)

selected_category = st.sidebar.multiselect(
    "Category",
    options=sorted(df_clean["category"].dropna().unique()),
    default=sorted(df_clean["category"].dropna().unique())
)

filtered_df = df_clean[
    (df_clean["site_name"].isin(selected_site)) &
    (df_clean["category"].isin(selected_category))
].copy()

filtered_ts = df_ts[
    (df_ts["site_name"].isin(selected_site)) &
    (df_ts["category"].isin(selected_category))
].copy()

st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Observations", f"{len(filtered_df):,}")
col2.metric("Unique Products", f"{filtered_df['product_id'].nunique():,}")
col3.metric("Mean Price", f"{filtered_df['price'].mean():,.2f} MAD")
col4.metric("Median Price", f"{filtered_df['price'].median():,.2f} MAD")

st.divider()

st.subheader("Price Distribution")

fig_price_dist = px.histogram(
    filtered_df,
    x="price",
    nbins=60,
    color="site_name",
    title="Price Distribution by Website",
    labels={"price": "Price", "site_name": "Website"}
)

st.plotly_chart(fig_price_dist, use_container_width=True)

filtered_df["log_price"] = np.log1p(filtered_df["price"])

fig_log_dist = px.histogram(
    filtered_df,
    x="log_price",
    nbins=60,
    color="site_name",
    title="Log-Transformed Price Distribution",
    labels={"log_price": "log(Price + 1)", "site_name": "Website"}
)

st.plotly_chart(fig_log_dist, use_container_width=True)

st.divider()

st.subheader("Price Comparison by Website")

site_stats = filtered_df.groupby("site_name")["price"].agg(
    count="count",
    mean="mean",
    median="median",
    min="min",
    max="max",
    std="std"
).reset_index()

st.dataframe(site_stats, use_container_width=True)

fig_site_box = px.box(
    filtered_df,
    x="site_name",
    y="log_price",
    color="site_name",
    title="Log-Price Distribution by Website",
    labels={"site_name": "Website", "log_price": "log(Price + 1)"}
)

st.plotly_chart(fig_site_box, use_container_width=True)

st.divider()

st.subheader("Price Analysis by Category")

category_stats = filtered_df.groupby("category")["price"].agg(
    count="count",
    mean="mean",
    median="median",
    min="min",
    max="max",
    std="std"
).reset_index().sort_values("median", ascending=False)

st.dataframe(category_stats, use_container_width=True)

fig_category = px.bar(
    category_stats.head(15),
    x="median",
    y="category",
    orientation="h",
    title="Top Categories by Median Price",
    labels={"median": "Median Price", "category": "Category"}
)

fig_category.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(fig_category, use_container_width=True)

st.divider()

st.subheader("Time-Series Price Trends")

filtered_ts["date"] = filtered_ts["scraped_at"].dt.date

daily_trend = filtered_ts.groupby(["date", "category"])["price"].mean().reset_index()

top_categories = (
    filtered_ts["category"]
    .value_counts()
    .head(5)
    .index
)

daily_trend_top = daily_trend[daily_trend["category"].isin(top_categories)]

fig_trend = px.line(
    daily_trend_top,
    x="date",
    y="price",
    color="category",
    title="Average Daily Price Trend by Top Categories",
    labels={"date": "Date", "price": "Average Price", "category": "Category"}
)

st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

st.subheader("Most Volatile Products")

product_volatility = filtered_ts.sort_values(["product_id", "scraped_at"]).groupby(
    ["product_id", "product_name", "site_name", "category"]
).agg(
    nb_observations=("price", "count"),
    mean_price=("price", "mean"),
    std_price=("price", "std"),
    min_price=("price", "min"),
    max_price=("price", "max")
).reset_index()

product_volatility["price_range"] = (
    product_volatility["max_price"] - product_volatility["min_price"]
)

volatile_products = product_volatility[
    (product_volatility["nb_observations"] >= 3) &
    (product_volatility["std_price"] > 0) &
    (product_volatility["price_range"] > 0)
].sort_values("std_price", ascending=False)

st.dataframe(volatile_products.head(10), use_container_width=True)

selected_products = volatile_products.head(5)["product_id"]

sample_ts = filtered_ts[filtered_ts["product_id"].isin(selected_products)]

if not sample_ts.empty:
    fig_product_ts = px.line(
        sample_ts,
        x="scraped_at",
        y="price",
        color="product_name",
        markers=True,
        title="Price Evolution for Most Volatile Products",
        labels={
            "scraped_at": "Scraping Date",
            "price": "Price",
            "product_name": "Product"
        }
    )

    st.plotly_chart(fig_product_ts, use_container_width=True)
else:
    st.info("No volatile products found for the selected filters.")

st.divider()

st.subheader("Latest Product Intelligence")

st.dataframe(df_intelligence.head(50), use_container_width=True)