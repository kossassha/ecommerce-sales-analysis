from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# ---------------------------------------------------------
# БАЗОВЫЕ НАСТРОЙКИ
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "processed" / "sales_clean.csv"

st.set_page_config(
    page_title="Аналитика продаж",
    page_icon="📊",
    layout="wide",
)


# ---------------------------------------------------------
# СТИЛИ
# ---------------------------------------------------------

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1400px;
        padding-top: 4.2rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        border-right: 1px solid #2a3038;
        background: #161b22;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    .report-kicker {
        font-size: 12px;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #8b949e;
        margin-top: 8px;
        margin-bottom: 10px;
    }

    .report-title {
        font-size: 32px;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 8px;
    }

    .report-subtitle {
        color: #8b949e;
        font-size: 15px;
        margin-bottom: 24px;
    }

    .section-title {
        font-size: 20px;
        font-weight: 650;
        margin-top: 8px;
        margin-bottom: 14px;
    }

    .metric-card {
        border: 1px solid #2a3038;
        border-radius: 8px;
        padding: 16px 18px;
        background: #151a21;
        min-height: 104px;
    }

    .metric-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 8px;
    }

    .metric-value {
        font-size: 26px;
        font-weight: 700;
        line-height: 1.1;
    }

    .insight-box {
        border: 1px solid #2a3038;
        border-radius: 8px;
        padding: 16px 18px;
        background: #151a21;
        margin-top: 8px;
    }

    .small-muted {
        font-size: 13px;
        color: #8b949e;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #2a3038;
        border-radius: 8px;
        overflow: hidden;
    }

    /* ---------- САЙДБАР ---------- */

    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label {
        color: #e6edf3 !important;
    }

    /* контейнеры select / multiselect */
    [data-testid="stSidebar"] [data-baseweb="select"] > div {
        background: #0f141b !important;
        border: 1px solid #2a3038 !important;
        border-radius: 10px !important;
        box-shadow: none !important;
        min-height: 52px;
    }

    /* hover/focus */
    [data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
        border-color: #3a4552 !important;
    }

    /* крестик удаления внутри тега */
    [data-testid="stSidebar"] [data-baseweb="tag"] svg {
        fill: #aeb8c2 !important;
    }

    /* текст в input */
    [data-testid="stSidebar"] input {
        color: #e6edf3 !important;
    }

    /* date input */
    [data-testid="stSidebar"] [data-testid="stDateInput"] > div > div {
        background: #0f141b !important;
        border: 1px solid #2a3038 !important;
        border-radius: 10px !important;
    }

    /* вкладки чуть строже */
    button[data-baseweb="tab"] {
        font-weight: 500 !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# ЗАГРУЗКА ДАННЫХ
# ---------------------------------------------------------

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)

    df["order_date"] = pd.to_datetime(df["order_date"])
    df["signup_date"] = pd.to_datetime(df["signup_date"])

    return df


df = load_data()


# ---------------------------------------------------------
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ---------------------------------------------------------

def money(value):
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:,.2f} млн"
    if abs(value) >= 1_000:
        return f"${value / 1_000:,.1f} тыс."
    return f"${value:,.0f}"


def number(value):
    return f"{int(value):,}".replace(",", " ")


def percent(value):
    return f"{value:.1f}%"


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------
# БОКОВЫЕ ФИЛЬТРЫ
# ---------------------------------------------------------

st.sidebar.markdown("## Фильтры")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()

date_range = st.sidebar.date_input(
    "Период",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

categories = sorted(df["category"].dropna().unique())
channels = sorted(df["channel"].dropna().unique())
cities = sorted(df["city"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Категория",
    options=categories,
    default=categories,
    key="category_filter",
)

selected_channels = st.sidebar.multiselect(
    "Канал продаж",
    options=channels,
    default=channels,
    key="channel_filter",
)

selected_cities = st.sidebar.multiselect(
    "Город",
    options=cities,
    default=cities,
    key="city_filter",
)


filtered = df.copy()

if len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1])

    filtered = filtered[
        (filtered["order_date"] >= start_date)
        & (filtered["order_date"] <= end_date)
    ]

filtered = filtered[
    filtered["category"].isin(selected_categories)
    & filtered["channel"].isin(selected_channels)
    & filtered["city"].isin(selected_cities)
]


completed = filtered[
    filtered["status"] == "Completed"
].copy()


# ---------------------------------------------------------
# KPI
# ---------------------------------------------------------

total_revenue = completed["revenue"].sum()
total_profit = completed["profit"].sum()
total_orders = completed["order_id"].nunique()
total_customers = completed["customer_id"].nunique()

average_order_value = (
    total_revenue / total_orders
    if total_orders > 0
    else 0
)


# ---------------------------------------------------------
# ЗАГОЛОВОК
# ---------------------------------------------------------

st.markdown(
    """
    <div class="report-title">Продажи интернет-магазина</div>
    <div class="report-subtitle">
        Продажи, клиенты, категории, каналы и качество заказов
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# KPI-КАРТОЧКИ
# ---------------------------------------------------------

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    metric_card("Выручка", money(total_revenue))

with col2:
    metric_card("Прибыль", money(total_profit))

with col3:
    metric_card("Заказы", number(total_orders))

with col4:
    metric_card("Средний чек", money(average_order_value))

with col5:
    metric_card("Клиенты", number(total_customers))


st.write("")


# ---------------------------------------------------------
# ВКЛАДКИ
# ---------------------------------------------------------

tab_overview, tab_products, tab_customers, tab_quality, tab_data = st.tabs(
    [
        "Обзор",
        "Товары",
        "Клиенты",
        "Качество заказов",
        "Данные",
    ]
)


# =========================================================
# ОБЗОР
# =========================================================

with tab_overview:

    st.markdown(
        '<div class="section-title">Динамика выручки</div>',
        unsafe_allow_html=True,
    )

    monthly = (
        completed
        .assign(
            month=completed["order_date"]
            .dt.to_period("M")
            .astype(str)
        )
        .groupby("month", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            orders=("order_id", "nunique"),
        )
    )

    fig_month = px.line(
        monthly,
        x="month",
        y="revenue",
        markers=True,
        labels={
            "month": "Месяц",
            "revenue": "Выручка",
        },
    )

    fig_month.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title="Выручка",
        showlegend=False,
    )

    st.plotly_chart(
        fig_month,
        width="stretch",
    )


    left, right = st.columns(2)


    with left:

        st.markdown(
            '<div class="section-title">Продажи по категориям</div>',
            unsafe_allow_html=True,
        )

        category_sales = (
            completed
            .groupby("category", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                profit=("profit", "sum"),
                orders=("order_id", "nunique"),
            )
            .sort_values("revenue", ascending=False)
        )

        fig_category = px.bar(
            category_sales,
            x="category",
            y="revenue",
            labels={
                "category": "Категория",
                "revenue": "Выручка",
            },
        )

        fig_category.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title="Выручка",
            showlegend=False,
        )

        st.plotly_chart(
            fig_category,
            width="stretch",
        )


    with right:

        st.markdown(
            '<div class="section-title">Продажи по каналам</div>',
            unsafe_allow_html=True,
        )

        channel_sales = (
            completed
            .groupby("channel", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                orders=("order_id", "nunique"),
            )
            .sort_values("revenue", ascending=False)
        )

        fig_channel = px.bar(
            channel_sales,
            x="channel",
            y="revenue",
            labels={
                "channel": "Канал",
                "revenue": "Выручка",
            },
        )

        fig_channel.update_layout(
            height=390,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title="Выручка",
            showlegend=False,
        )

        st.plotly_chart(
            fig_channel,
            width="stretch",
        )


    if not category_sales.empty and not channel_sales.empty:

        top_category = category_sales.iloc[0]
        top_channel = channel_sales.iloc[0]

        st.markdown(
            f"""
            <div class="insight-box">
                <div class="metric-label">КЛЮЧЕВЫЕ НАБЛЮДЕНИЯ</div>
                <div>
                    Крупнейшая категория по выручке —
                    <b>{top_category["category"]}</b>
                    ({money(top_category["revenue"])}).
                    Лидирующий канал продаж —
                    <b>{top_channel["channel"]}</b>
                    ({money(top_channel["revenue"])}).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# =========================================================
# ТОВАРЫ
# =========================================================

with tab_products:

    st.markdown(
        '<div class="section-title">Топ-10 товаров по выручке</div>',
        unsafe_allow_html=True,
    )

    top_products = (
        completed
        .groupby("product_name", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
            quantity=("quantity", "sum"),
        )
        .sort_values("revenue", ascending=False)
        .head(10)
        .sort_values("revenue", ascending=True)
    )

    fig_products = px.bar(
        top_products,
        x="revenue",
        y="product_name",
        orientation="h",
        labels={
            "revenue": "Выручка",
            "product_name": "Товар",
        },
    )

    fig_products.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title="Выручка",
        yaxis_title=None,
        showlegend=False,
    )

    st.plotly_chart(
        fig_products,
        width="stretch",
    )


    st.markdown(
        '<div class="section-title">Категории: выручка и прибыль</div>',
        unsafe_allow_html=True,
    )

    category_profit = (
        completed
        .groupby("category", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
        )
    category_profit_display = category_profit.rename(
    columns={
        "revenue": "Выручка",
        "profit": "Прибыль",
    }
        )
    )

    fig_category_profit = px.bar(
        category_profit_display,
        x="category",
        y=["Выручка", "Прибыль"],
        barmode="group",
        labels={
            "category": "Категория",
            "value": "Сумма",
            "variable": "Показатель",
    },
)

    fig_category_profit.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=10, b=10),
    xaxis_title=None,
        yaxis_title="Сумма",
        legend_title_text="",
)
    fig_category_profit.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title="Сумма",
        legend_title_text="",
    )

    st.plotly_chart(
        fig_category_profit,
        width="stretch",
    )


# =========================================================
# КЛИЕНТЫ
# =========================================================

with tab_customers:

    left, right = st.columns(2)


    with left:

        st.markdown(
            '<div class="section-title">Сегменты клиентов</div>',
            unsafe_allow_html=True,
        )

        segment_sales = (
            completed
            .groupby("segment", as_index=False)
            .agg(
                revenue=("revenue", "sum"),
                customers=("customer_id", "nunique"),
            )
            .sort_values("revenue", ascending=True)
        )

        fig_segments = px.bar(
            segment_sales,
            x="revenue",
            y="segment",
            orientation="h",
            labels={
                "segment": "Сегмент",
                "revenue": "Выручка",
            },
        )

        fig_segments.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Выручка",
            yaxis_title=None,
            showlegend=False,
        )

        st.plotly_chart(
            fig_segments,
            width="stretch",
        )


    with right:

        st.markdown(
            '<div class="section-title">Количество клиентов по сегментам</div>',
            unsafe_allow_html=True,
        )

        customer_segments = (
            completed[
                ["customer_id", "segment"]
            ]
            .drop_duplicates()
            .groupby("segment", as_index=False)
            .agg(
                customers=("customer_id", "nunique")
            )
            .sort_values("customers", ascending=True)
        )

        fig_customer_segments = px.bar(
            customer_segments,
            x="customers",
            y="segment",
            orientation="h",
            labels={
                "customers": "Клиенты",
                "segment": "Сегмент",
            },
        )

        fig_customer_segments.update_layout(
            height=360,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title="Клиенты",
            yaxis_title=None,
            showlegend=False,
        )

        st.plotly_chart(
            fig_customer_segments,
            width="stretch",
        )


    st.markdown(
        '<div class="section-title">География продаж</div>',
        unsafe_allow_html=True,
    )

    city = (
        completed
        .groupby("city", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            orders=("order_id", "nunique"),
            customers=("customer_id", "nunique"),
        )
        .sort_values("revenue", ascending=False)
        .head(10)
    )

    city["avg_check"] = (
        city["revenue"] / city["orders"]
    )

    city_display = city.copy()

    city_display["revenue"] = (
        city_display["revenue"]
        .map(lambda x: f"${x:,.0f}")
    )

    city_display["avg_check"] = (
        city_display["avg_check"]
        .map(lambda x: f"${x:,.0f}")
    )

    city_display = city_display.rename(
        columns={
            "city": "Город",
            "revenue": "Выручка",
            "orders": "Заказы",
            "customers": "Клиенты",
            "avg_check": "Средний чек",
        }
    )

    st.dataframe(
        city_display,
        width="stretch",
        hide_index=True,
    )


# =========================================================
# КАЧЕСТВО ЗАКАЗОВ
# =========================================================

with tab_quality:

    order_level = (
        filtered[
            ["order_id", "status"]
        ]
        .drop_duplicates()
    )

    status_counts = (
        order_level["status"]
        .value_counts()
    )

    completed_orders = int(
        status_counts.get("Completed", 0)
    )

    cancelled_orders = int(
        status_counts.get("Cancelled", 0)
    )

    returned_orders = int(
        status_counts.get("Returned", 0)
    )

    all_orders = len(order_level)

    cancel_rate = (
        cancelled_orders / all_orders * 100
        if all_orders > 0
        else 0
    )

    return_rate = (
        returned_orders / all_orders * 100
        if all_orders > 0
        else 0
    )


    q1, q2, q3, q4 = st.columns(4)

    with q1:
        metric_card(
            "Завершено",
            number(completed_orders),
        )

    with q2:
        metric_card(
            "Отменено",
            number(cancelled_orders),
        )

    with q3:
        metric_card(
            "Доля отмен",
            percent(cancel_rate),
        )

    with q4:
        metric_card(
            "Доля возвратов",
            percent(return_rate),
        )


    st.write("")

    status_table = pd.DataFrame(
        {
            "Статус": [
                "Завершено",
                "Отменено",
                "Возвращено",
            ],
            "Заказы": [
                completed_orders,
                cancelled_orders,
                returned_orders,
            ],
        }
    )

    status_table["Доля"] = (
        status_table["Заказы"]
        / status_table["Заказы"].sum()
        * 100
    )

    status_table["Доля"] = (
        status_table["Доля"]
        .map(lambda x: f"{x:.1f}%")
    )

    st.markdown(
        '<div class="section-title">Структура заказов</div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        status_table,
        width="stretch",
        hide_index=True,
    )


# =========================================================
# ДАННЫЕ
# =========================================================

with tab_data:

    st.markdown(
        '<div class="section-title">Данные</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="small-muted">
            Строк: {number(len(filtered))}
            · Столбцов: {filtered.shape[1]}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.write("")

    csv = filtered.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="Скачать CSV",
        data=csv,
        file_name="filtered_sales.csv",
        mime="text/csv",
    )

    st.write("")

    st.dataframe(
        filtered,
        width="stretch",
        hide_index=True,
    )