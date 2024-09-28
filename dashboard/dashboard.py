# Michael Jonathan Halim - Streamlit Dashboard
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency
import streamlit.components.v1 as components

sns.set(style='dark')

def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule='D', on='order_purchase_timestamp').agg({
        "order_id": "nunique",
        "price": "sum"
    }).reset_index()
    daily_orders_df.rename(columns={
        "order_id": "order_count",
        "price": "revenue"
    }, inplace=True)
    return daily_orders_df

def create_bystate_df(df):
    bystate_df = df.groupby("customer_state").customer_id.nunique().reset_index()
    bystate_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bystate_df

def create_bycity_df(df):
    bycity_df = df.groupby("customer_city").customer_id.nunique().reset_index()
    bycity_df.rename(columns={"customer_id": "customer_count"}, inplace=True)
    return bycity_df

data_path = './data'
rfm = pd.read_csv('./dashboard/rfm.csv')
orders = pd.read_csv(data_path + '/orders_dataset.csv')
items = pd.read_csv(data_path + '/order_items_dataset.csv')
customers = pd.read_csv(data_path + '/customers_dataset.csv')
orders = pd.merge(orders, items, on='order_id', how='inner')

# Convert date columns
orders["order_purchase_timestamp"] = pd.to_datetime(orders["order_purchase_timestamp"])

# Filter data based on date
min_date = orders["order_purchase_timestamp"].min()
max_date = orders["order_purchase_timestamp"].max()

# Streamlit sidebar for date range filter
with st.sidebar:
    st.image("https://michaeljh.netlify.app/static/media/lingkaran.7f5f7188b86cce0f0f19.png")
    start_date, end_date = st.date_input(
        label='Rentang Waktu', min_value=min_date, max_value=max_date, value=[min_date, max_date]
    )

# Filter data for the selected date range
filtered_df = orders[(orders["order_purchase_timestamp"] >= pd.to_datetime(start_date)) & (orders["order_purchase_timestamp"] <= pd.to_datetime(end_date))]

# Create necessary DataFrames
daily_orders_df = create_daily_orders_df(filtered_df)
bystate_df = create_bystate_df(customers)
bycity_df = create_bycity_df(customers)
top_products_df = pd.read_csv('./dashboard/top_5_products.csv')
top_regions_df = pd.read_csv('./dashboard/top_10_regions.csv')

# Dashboard Header
st.header('E-Commerce Dashboard')
st.subheader('Daily Orders')

# Add a note about the interactivity
st.markdown("""
    **Note**: The date range filter is applied **only** to the "Total Orders Revenue" and "Daily Orders Plot" sections.
    Other sections display the full dataset due to the large data size.
""")

# Show total orders and revenue
col1, col2 = st.columns(2)
with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total Orders", value=total_orders)
with col2:
    total_revenue = format_currency(daily_orders_df.revenue.sum(), "USD", locale='en_US')
    st.metric("Total Revenue", value=total_revenue)

# Plot daily orders
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(daily_orders_df["order_purchase_timestamp"], daily_orders_df["order_count"], marker='o', color="#90CAF9", linewidth=2)
ax.set_xlabel("Order Date", fontsize=15)
ax.set_ylabel("Order Count", fontsize=15)
st.pyplot(fig)

# Customer Demographics
st.subheader("Customer Demographics")
col1, col2 = st.columns(2)
with col1:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="customer_count", y="customer_city", data=bycity_df.sort_values(by="customer_count", ascending=False).head(10), palette="Blues_d", ax=ax)
    ax.set_title("Number of Customers by City", fontsize=20)
    st.pyplot(fig)
with col2:
    fig, ax = plt.subplots(figsize=(20, 10))
    sns.barplot(x="customer_count", y="customer_state", data=bystate_df.sort_values(by="customer_count", ascending=False).head(10), palette="Greens_d", ax=ax)
    ax.set_title("Number of Customers by State", fontsize=20)
    st.pyplot(fig)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa kota Sao Paulo merupakan kota dengan konsumen e-commerce terbanyak dan SP merupakan state dengan konsumen e-commerce terbanyak.
""")

# Top 5 Products
st.subheader("Top 5 Products by Review Count with Average Rating 5.0")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(y='product_category_name', x='review_count', data=top_products_df, palette='coolwarm')
ax.set_title("Top 5 Products by Review Count with Average Rating 5.0", fontsize=20)
st.pyplot(fig)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa papelaria merupakan produk dengan peminat terbanyak beserta rating terbaik sebesar 5.0, membuat produk papelaria menjadi best product yang dijual di e-commerce. Hal ini bisa menjadi potensi untuk membuat dan menjual produk-produk yang serupa dengan papelaria untuk meningkatkan revenue.
""")

# Top 10 Regions
st.subheader("Top 10 Regions by Total Sales")
fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(x='customer_city', y='total_sales', data=top_regions_df, palette='coolwarm')
ax.set_title("Top 10 Regions by Total Sales", fontsize=20)
st.pyplot(fig)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa seluruh customer dengan pengeluaran terbanyak terdapat di kota Rio de Janeiro.
""")

# RFM Analysis
st.subheader("Best Customers Based on RFM")

def truncate_customer_id(customer_id, max_length=8):
    return customer_id if len(customer_id) <= max_length else customer_id[:max_length] + '...'

rfm['customer_unique_id_truncated'] = rfm['customer_unique_id'].apply(truncate_customer_id)
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))
colors = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]

# Recency barplot
sns.barplot(x="recency", y="customer_unique_id_truncated", 
            data=rfm.sort_values(by="recency", ascending=True).head(5), 
            palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency (days)", loc="center", fontsize=18)
ax[0].tick_params(axis ='y', labelsize=15)

# Frequency barplot
sns.barplot(x="frequency", y="customer_unique_id_truncated", 
            data=rfm.sort_values(by="frequency", ascending=False).head(5), 
            palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=18)
ax[1].tick_params(axis='y', labelsize=15)

# Monetary barplot
sns.barplot(x="monetary", y="customer_unique_id_truncated", 
            data=rfm.sort_values(by="monetary", ascending=False).head(5), 
            palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=18)
ax[2].tick_params(axis='y', labelsize=15)

plt.suptitle("Best Customer Based on RFM Parameters (customer_unique_id)", fontsize=20)
plt.tight_layout()
st.pyplot(fig)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa dengan menggunakan RFM Analysis, kita dapat mengidentifikasi pelanggan 
    yang menjadi top spender (pengeluaran terbesar) dan top order (frekuensi transaksi tertinggi), memberikan peluang bagi
    bisnis untuk menargetkan mereka dengan strategi pemasaran yang lebih efektif.
""")

# Segment customers based on spending
st.subheader("Customer Spending Group")
bins = [0, 100, 500, 1000, float('inf')]
labels = ['Low Spender', 'Medium Spender', 'High Spender', 'Very High Spender']
rfm['spending_group'] = pd.cut(rfm['monetary'], bins=bins, labels=labels)

# Plot customer spending groups
fig, ax = plt.subplots(figsize=(12, 8))
sns.countplot(x='spending_group', data=rfm, palette="Set2", ax=ax)
ax.set_title('Clustering Pelanggan Berdasarkan Pengeluaran (Monetary)', fontsize=20)
ax.set_xlabel('Spending Group', fontsize=15)
ax.set_ylabel('Jumlah Pelanggan', fontsize=15)
st.pyplot(fig)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa kebanyakan pelanggan e-commerce termasuk pada very high spender, artinya kebanyakan customer mengeluarkan banyak uang untuk bertransaksi membeli produk secara online.
""")

# Display Folium Map
st.subheader("Customer Locations from Top Sales")
map_file = './top_sales_customer_locations.html'
with open(map_file, 'r', encoding='utf-8') as f:
    map_html = f.read()
components.html(map_html, height=500)
st.markdown("""
    **Insight**: Dapat disimpulkan bahwa seluruh customer dengan pengeluaran terbanyak tersebar di daerah Brasil, membuat Brasil menjadi pasar potensial untuk meningkatkan penjualan.
""")

st.caption('© Michael Jonathan Halim 2024')
