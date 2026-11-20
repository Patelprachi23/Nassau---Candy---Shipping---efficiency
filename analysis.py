import pandas as pd
from pathlib import Path
SOURCE=Path("Nassau Candy Distributor.csv")
OUT=Path(".")
factory_map={
"Wonka Bar - Nutty Crunch Surprise":"Lot's O' Nuts","Wonka Bar - Fudge Mallows":"Lot's O' Nuts","Wonka Bar -Scrumdiddlyumptious":"Lot's O' Nuts",
"Wonka Bar - Milk Chocolate":"Wicked Choccy's","Wonka Bar - Triple Dazzle Caramel":"Wicked Choccy's",
"Laffy Taffy":"Sugar Shack","SweeTARTS":"Sugar Shack","Nerds":"Sugar Shack","Fun Dip":"Sugar Shack","Fizzy Lifting Drinks":"Sugar Shack",
"Everlasting Gobstopper":"Secret Factory","Lickable Wallpaper":"Secret Factory","Wonka Gum":"Secret Factory",
"Hair Toffee":"The Other Factory","Kazookles":"The Other Factory"}
df=pd.read_csv(SOURCE)
for c in ["Order Date","Ship Date"]: df[c]=pd.to_datetime(df[c],format="%d-%m-%Y",errors="coerce")
df["Shipping Lead Time (Days)"]=(df["Ship Date"]-df["Order Date"]).dt.days
df["Factory"]=df["Product Name"].map(factory_map)
df["Route (Factory → State)"]=df["Factory"]+" → "+df["State/Province"].astype(str)
df["Route (Factory → Region)"]=df["Factory"]+" → "+df["Region"].astype(str)
df.to_csv(OUT/"cleaned_shipments.csv",index=False)
route=df.groupby(["Factory","State/Province","Region"]).agg(Total_Shipments=("Order ID","nunique"),Avg_Lead_Time_Days=("Shipping Lead Time (Days)","mean"),Lead_Time_Std_Dev=("Shipping Lead Time (Days)","std")).reset_index()
mn,mx=route.Avg_Lead_Time_Days.min(),route.Avg_Lead_Time_Days.max()
route["Route_Efficiency_Score"]=100 if mn==mx else 100*(mx-route.Avg_Lead_Time_Days)/(mx-mn)
route.sort_values("Avg_Lead_Time_Days").to_csv(OUT/"route_efficiency_summary.csv",index=False)
df.groupby("Region").agg(Shipments=("Order ID","nunique"),Avg_Lead_Time_Days=("Shipping Lead Time (Days)","mean")).to_csv(OUT/"regional_summary.csv")
df.groupby("Ship Mode").agg(Shipments=("Order ID","nunique"),Avg_Lead_Time_Days=("Shipping Lead Time (Days)","mean")).to_csv(OUT/"ship_mode_summary.csv")
df.groupby("State/Province").agg(Shipments=("Order ID","nunique"),Avg_Lead_Time_Days=("Shipping Lead Time (Days)","mean")).to_csv(OUT/"state_summary.csv")
print("Rows:",len(df),"Mean lead time:",df["Shipping Lead Time (Days)"].mean())
