import streamlit as st
import plotly.express as px
import pandas as pd
import os
import plotly.figure_factory as ff
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="SuperStore!!!", page_icon=":bar_chart:", layout="wide")

st.title("📊 Sample Superstore EDA")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xls"])

if fl is not None:
    df = pd.read_csv(fl, encoding="ISO-8859-1")
else:
    st.write("Please upload a file to proceed.")
    st.stop()

df["Order Date"] = pd.to_datetime(df["Order Date"], format='%d-%m-%Y', errors='coerce')


col1, col2 = st.columns((2))

startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))
with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

with st.expander("Preview Data"):
    st.subheader("Complete Data")
    st.write(df)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Data", data=csv, file_name="CompleteData.csv", mime="text/csv",
                       help='Click here to download the complete data as CSV file')

st.sidebar.header("Choose your filter:")

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
state = []
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

if not df2.empty:
    state = st.sidebar.multiselect("Pick the State", df2["State"].unique())

if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df[df["Region"].isin(region) & df["State"].isin(state) & df["City"].isin(city)]

category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

col3, col4 = st.columns(2)
with col3:
    st.subheader("Category wise Sales")
    fig = px.bar(category_df, x="Category", y="Sales", text=category_df["Sales"].apply(lambda x: f"${x:,.2f}"), template="seaborn")
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df)
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_df)
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as CSV file')

filtered_df["month_year"] = filtered_df["Order Date"].dt.strftime("%Y-%b")
st.subheader('Time Series Analysis')
linechart = pd.DataFrame(filtered_df.groupby("month_year")["Sales"].sum().reset_index())
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)
with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='txt/csv')

st.subheader("Hierarchical view of Sales using Treemap")
fig3 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"],
                  color="Sub-Category")
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(text=filtered_df["Segment"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(text=filtered_df["Category"], textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df.sample(n=10)
    df_sample_display = df_sample[["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample_display, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year)

data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title="Relationship between Sales and Profits using Scatter Plot.",
    title_font=dict(size=20),
    xaxis=dict(title="Sales", title_font=dict(size=19)),
)
st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2])
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
