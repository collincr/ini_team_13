import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


fname = "data/calif/calif.ast"

# ASCII_data "CALIF ASCII data format"
fmt = ["station_id 1 8 char 0",
       "latitude_deg 10 11 short 0",
       "latitude_min 12 15 short 2",
       "longitude_deg 16 19 short 0",
       "longitude_min 20 23 short 2",
       "sea_level_elev_ft 24 29 long 1",
       "obs_grav 30 36 long 2",
       "accuracy_code 37 40 char 0",
       "Free_air_anom 41 46 long 2",
       "Bouguer_anom_simp 47 52 long 2",
       "terr_corr_inner 53 57 long 2",
       "terr_corr_total 58 62 long 2",
       "Hammer_zone 63 63 char 0",
       "Bouguer_anom_267 64 69 long 2",
       "isostatic_anom 70 75 long 2",
       "IGSN71_conv_factor 76 80 char 0"]

dtypes = []

f = open(fname, "r+")
data_content = f.readlines()
f.close()


allrows = []
for lineno, line in enumerate(data_content):
    row = []
    for fmtcol in fmt:
        colname, start_col, end_col, dtype, num = fmtcol.split()
        
        # from one-indexing to zero-indexing,=
        start_col, end_col = int(start_col)-1, int(end_col)
        num_decimal = int(num)
        
        if dtype == "char":
            item = line[start_col:end_col]
            if lineno == 0:
                dtypes.append((colname))
        
        elif num_decimal > 0:
            end_col -= num_decimal
            new_end_col = end_col + num_decimal
            stritem = line[start_col:end_col].strip()
            neg = False
            if stritem:
                if stritem[0] == "-":
                    neg = True
                    if len(stritem) == 1:
                        whole = 0
                    else:
                        whole = float(stritem[1:])
                else:
                    whole = float(stritem)
            else:
                whole = 0
            frac = float(line[end_col:new_end_col]) / (10**num_decimal)
            item = whole + frac
            if lineno == 0:
                dtypes.append((colname))
        else:
            whole = float(line[start_col:end_col])
            if line[start_col] == "-":
                whole = float(line[start_col+1:end_col])
            item = float(whole)
            if lineno == 0:
                dtypes.append((colname))
            
        row.append(item)
    allrows.append(row)
    
allrows_df = pd.DataFrame(allrows, columns=dtypes)

# 60 minutes per degree of latitude/longitude
# Converting Latitude/Longitude to decimal degrees
allrows_df["latitude"] = (allrows_df["latitude_deg"] +
                          allrows_df["latitude_min"] / 60)
allrows_df["longitude"] = -1*( allrows_df["longitude_deg"] +
                               allrows_df["longitude_min"] / 60)

df = allrows_df.drop(columns=["latitude_deg", "latitude_min",
                              "longitude_deg", "longitude_min"])

# Converting to a georeferenced data object and saving as geojson
geom = [Point(x, y) for (x, y) in df[["longitude", "latitude"]].values]
gdf = gpd.GeoDataFrame(df, geometry=geom, crs="epsg:4326")
gdf.to_file("data/geojson/calif_nev_ncei_grav.geojson", driver="GeoJSON")

# Very basic scatter plot of the data
fig, ax = plt.subplots(figsize=(12,12))
ax.scatter(df["longitude"], df["latitude"], c=df["isostatic_anom"], s=0.8)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.set_aspect("equal")

# Save to file
fig.savefig("figures/canv_data.png")


