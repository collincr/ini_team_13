import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    x_bounds=(-124, -120)
    y_bounds=(37, 39)
    
    gdf = gpd.read_file("../data/geojson/calif_nev_ncei_grav.geojson")
    
    gdf_subset = gdf[(gdf["latitude"] > y_bounds[0]) &
                     (gdf["latitude"] < y_bounds[1]) &
                     (gdf["longitude"] > x_bounds[0]) &
                     (gdf["longitude"] < x_bounds[1])]
    
    gdf_subset_sorted = gdf_subset.sort_values(by="isostatic_anom",
                                               ascending=False)

    fig, ax = plt.subplots(figsize=(16, 6))
    
    ax.bar(x=np.arange(gdf_subset.shape[0]), width=0.9,
           height=gdf_subset_sorted["isostatic_anom"].values)
    
    fig.savefig("task4.png")