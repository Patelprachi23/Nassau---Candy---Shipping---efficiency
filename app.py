import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Nassau Candy Route Efficiency", layout="wide")
st.title("Factory-to-Customer Shipping Route Efficiency")
st.caption("Nassau Candy Distributor | Interactive descriptive analytics")

@st.cache_data
def load_data():
    d=pd.read_csv("cleaned_shipments.csv", parse_dates=["Order Date","Ship Date"])
    d["Shipping Lead Time (Days)"]=pd.to_numeric(d["Shipping Lead Time (Days)"],errors="coerce")
    return d
df=load_data()
st.warning("Data-quality alert: supplied order-to-ship intervals are unusually long. Validate the source dates before using these results for operational decisions.")
with st.sidebar:
    st.header("Filters")
    min_date=df["Order Date"].min().date(); max_date=df["Order Date"].max().date()
    date_range=st.date_input("Order date range",(min_date,max_date),min_value=min_date,max_value=max_date)
    regions=st.multiselect("Region",sorted(df["Region"].dropna().unique()),default=sorted(df["Region"].dropna().unique()))
    states=st.multiselect("State / Province",sorted(df["State/Province"].dropna().unique()))
    modes=st.multiselect("Ship mode",sorted(df["Ship Mode"].dropna().unique()),default=sorted(df["Ship Mode"].dropna().unique()))
    threshold=st.slider("Delay threshold (days)",1,1800,10)
f=df.copy()
if isinstance(date_range,tuple) and len(date_range)==2:
    f=f[(f["Order Date"].dt.date>=date_range[0])&(f["Order Date"].dt.date<=date_range[1])]
if regions: f=f[f["Region"].isin(regions)]
if states: f=f[f["State/Province"].isin(states)]
if modes: f=f[f["Ship Mode"].isin(modes)]
if f.empty:
    st.info("No records match the selected filters."); st.stop()
orders=f["Order ID"].nunique()
c1,c2,c3,c4=st.columns(4)
c1.metric("Distinct orders",f"{orders:,}")
c2.metric("Average lead time",f"{f['Shipping Lead Time (Days)'].mean():,.1f} days")
c3.metric("Median lead time",f"{f['Shipping Lead Time (Days)'].median():,.0f} days")
c4.metric("Above threshold",f"{(f['Shipping Lead Time (Days)']>threshold).mean()*100:.1f}%")
st.caption("Delay frequency is calculated as the share of available rows with lead time strictly greater than the user-selected threshold; choose a business-approved threshold for formal reporting.")
tab1,tab2,tab3,tab4=st.tabs(["Route overview","Geography","Ship mode","Order drill-down"])
with tab1:
    route=f.groupby(["Factory","State/Province","Region"]).agg(Orders=("Order ID","nunique"),Average_Lead_Time=("Shipping Lead Time (Days)","mean"),Lead_Time_SD=("Shipping Lead Time (Days)","std")).reset_index()
    lo,hi=route.Average_Lead_Time.min(),route.Average_Lead_Time.max()
    route["Efficiency_Score"]=100 if hi==lo else 100*(hi-route.Average_Lead_Time)/(hi-lo)
    st.subheader("Route leaderboard")
    st.dataframe(route.sort_values("Average_Lead_Time").round(2),use_container_width=True)
    st.plotly_chart(px.bar(route.sort_values("Average_Lead_Time"),x="Average_Lead_Time",y="State/Province",color="Factory",orientation="h",hover_data=["Orders","Efficiency_Score"],title="Average lead time by factory-to-state route"),use_container_width=True)
    left,right=st.columns(2)
    left.write("10 fastest route combinations"); left.dataframe(route.nsmallest(10,"Average_Lead_Time").round(2),use_container_width=True)
    right.write("10 slowest route combinations"); right.dataframe(route.nlargest(10,"Average_Lead_Time").round(2),use_container_width=True)
with tab2:
    geo=f.groupby(["State/Province","Region"]).agg(Orders=("Order ID","nunique"),Average_Lead_Time=("Shipping Lead Time (Days)","mean")).reset_index()
    state_codes={"Alabama":"AL","Arizona":"AZ","Arkansas":"AR","California":"CA","Colorado":"CO","Connecticut":"CT","Delaware":"DE","District of Columbia":"DC","Florida":"FL","Georgia":"GA","Idaho":"ID","Illinois":"IL","Indiana":"IN","Iowa":"IA","Kansas":"KS","Kentucky":"KY","Louisiana":"LA","Maine":"ME","Maryland":"MD","Massachusetts":"MA","Michigan":"MI","Minnesota":"MN","Mississippi":"MS","Missouri":"MO","Montana":"MT","Nebraska":"NE","Nevada":"NV","New Hampshire":"NH","New Jersey":"NJ","New Mexico":"NM","New York":"NY","North Carolina":"NC","North Dakota":"ND","Ohio":"OH","Oklahoma":"OK","Oregon":"OR","Pennsylvania":"PA","Rhode Island":"RI","South Carolina":"SC","South Dakota":"SD","Tennessee":"TN","Texas":"TX","Utah":"UT","Vermont":"VT","Virginia":"VA","Washington":"WA","West Virginia":"WV","Wisconsin":"WI","Wyoming":"WY"}
    us_geo=geo[geo["State/Province"].isin(state_codes)].copy()
    us_geo["State_Code"]=us_geo["State/Province"].map(state_codes)
    if not us_geo.empty:
        st.plotly_chart(px.choropleth(us_geo,locations="State_Code",locationmode="USA-states",scope="usa",color="Average_Lead_Time",hover_name="State/Province",hover_data=["Orders","Region"],color_continuous_scale="Reds",title="US state shipping lead-time heatmap"),use_container_width=True)
    else:
        st.info("No US state records available for the selected filters.")
    st.plotly_chart(px.treemap(geo,path=["Region","State/Province"],values="Orders",color="Average_Lead_Time",color_continuous_scale="Reds",title="Shipment volume and average lead time by all geographies"),use_container_width=True)
    st.dataframe(geo.sort_values("Average_Lead_Time",ascending=False).round(2),use_container_width=True)
with tab3:
    m=f.groupby("Ship Mode").agg(Orders=("Order ID","nunique"),Average_Lead_Time=("Shipping Lead Time (Days)","mean"),Median_Lead_Time=("Shipping Lead Time (Days)","median")).reset_index()
    st.plotly_chart(px.bar(m,x="Ship Mode",y="Average_Lead_Time",color="Ship Mode",title="Average lead time by ship mode"),use_container_width=True)
    st.dataframe(m.round(2),use_container_width=True)
    st.info("Descriptive comparison only; ship-mode differences are not causal and may reflect different order/geographic mixes.")
with tab4:
    cols=["Order ID","Order Date","Ship Date","Ship Mode","Factory","City","State/Province","Region","Product Name","Shipping Lead Time (Days)"]
    st.dataframe(f[cols].sort_values("Shipping Lead Time (Days)",ascending=False),use_container_width=True)
    st.download_button("Download filtered records",f[cols].to_csv(index=False).encode("utf-8"),"filtered_shipments.csv","text/csv")
st.subheader("Method and limitations")
st.write("Lead time = Ship Date − Order Date. Factory is inferred from Product Name using the product-to-factory mapping in the supplied technical documentation. The source does not contain actual factory dispatch coordinates, carrier, freight cost, promised delivery date or delivery date. Long intervals in the supplied dates require validation.")
