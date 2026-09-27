from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed" / "sales_clean.csv"


st.set_page_config(
    page_title="E-commerce Sales Analytics",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["signup_date"] = pd.to_datetime(df["signup_date"])

    return df


df = load_data()


st.title("E-commerce Sales Analytics")

st.write(
    "Интерактивный анализ продаж интернет-магазина: "
    "выручка, прибыль, категории, товары, клиенты и каналы продаж."
)


st.sidebar.header("Filters")


min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()


date_range = st.sidebar.date_input(
    "Order date",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


categories = sorted(df["category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Category",
    options=categories,
    default=categories
)


channels = sorted(df["channel"].dropna().unique())

selected_channels = st.sidebar.multiselect(
    "Channel",
    options=channels,
    default=channels
)


cities = sorted(df["city"].dropna().unique())

selected_cities = st.sidebar.multiselect(
    "City",
    options=cities,
    default=cities
)


filtered = df.copy()


if len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered = filtered[
        (filtered["order_date"] >= start_date) &
        (filtered["order_date"] <= end_date)
    ]


filtered = filtered[
    filtered["category"].isin(selected_categories)
    & filtered["channel"].isin(selected_channels)
    & filtered["city"].isin(selected_cities)
]


completed = filtered[
    filtered["status"] == "Completed"
].copy()


total_revenue = completed["revenue"].sum()
total_profit = completed["profit"].sum()
total_orders = completed["order_id"].nunique()
total_customers = completed["customer_id"].nunique()


if total_orders > 0:
    average_order_value = total_revenue / total_orders
else:
    average_order_value = 0


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Revenue",
    f"${total_revenue:,.0f}"
)

col2.metric(
    "Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Customers",
    f"{total_customers:,}"
)

col4.metric(
    "Average Order Value",
    f"${average_order_value:,.2f}"
)

col5.metric(
    "Profit",
    f"${total_profit:,.0f}"
)


st.divider()


st.subheader("Revenue by Month")


monthly = (
    completed
    .assign(
        month=completed["order_date"].dt.to_period("M").astype(str)
    )
    .groupby("month", as_index=False)
    .agg(
        revenue=("revenue", "sum")
    )
)


fig_month = px.line(
    monthly,
    x="month",
    y="revenue",
    markers=True,
    labels={
        "month": "Month",
        "revenue": "Revenue"
    }
)


st.plotly_chart(
    fig_month,
    use_container_width=True
)


left, right = st.columns(2)


with left:

    st.subheader("Revenue by Category")

    category = (
        completed
        .groupby("category", as_index=False)
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values("revenue", ascending=False)
    )

    fig_category = px.bar(
        category,
        x="category",
        y="revenue"
    )

    st.plotly_chart(
        fig_category,
        use_container_width=True
    )


with right:

    st.subheader("Revenue by Channel")

    channel = (
        completed
        .groupby("channel", as_index=False)
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values("revenue", ascending=False)
    )

    fig_channel = px.bar(
        channel,
        x="channel",
        y="revenue"
    )

    st.plotly_chart(
        fig_channel,
        use_container_width=True
    )


st.divider()


left, right = st.columns(2)


with left:

    st.subheader("Top 10 Products")

    products = (
        completed
        .groupby("product_name", as_index=False)
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    fig_products = px.bar(
        products,
        x="revenue",
        y="product_name",
        orientation="h"
    )

    st.plotly_chart(
        fig_products,
        use_container_width=True
    )


with right:

    st.subheader("Revenue by Customer Segment")

    segments = (
        completed
        .groupby("segment", as_index=False)
        .agg(
            revenue=("revenue", "sum")
        )
        .sort_values("revenue", ascending=False)
    )

    fig_segments = px.pie(
        segments,
        names="segment",
        values="revenue"
    )

    st.plotly_chart(
        fig_segments,
        use_container_width=True
    )


st.divider()


st.subheader("Top Cities")


city = (
    completed
    .groupby("city", as_index=False)
    .agg(
        revenue=("revenue", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique")
    )
    .sort_values("revenue", ascending=False)
    .head(10)
)


st.dataframe(
    city,
    use_container_width=True,
    hide_index=True
)


st.divider()


st.subheader("Returns and Cancellations")


statuses = (
    filtered["status"]
    .value_counts()
    .reset_index()
)


statuses.columns = [
    "status",
    "orders"
]


fig_status = px.bar(
    statuses,
    x="status",
    y="orders"
)


st.plotly_chart(
    fig_status,
    use_container_width=True
)


st.divider()


st.subheader("Data Explorer")


st.dataframe(
    completed,
    use_container_width=True,
    hide_index=True
)