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

    fig, ax = plt.subplots()
    
    ax.scatter(gdf_subset["longitude"], gdf_subset["latitude"],
               c=gdf_subset["isostatic_anom"], s=2)
    
    ax.set_aspect("equal")
    
    fig.savefig("task1.png")