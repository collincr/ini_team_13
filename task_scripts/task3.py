import geopandas as gpd
import pandas as pd
import numpy as np
from scipy import spatial
import matplotlib.pyplot as plt


if __name__ == "__main__":
    
    x_bounds=(-124, -120)
    y_bounds=(37, 39)
    
    gdf = gpd.read_file("../data/geojson/calif_nev_ncei_grav.geojson")
    
    gdf_subset = gdf[(gdf["latitude"] > y_bounds[0]) &
                     (gdf["latitude"] < y_bounds[1]) &
                     (gdf["longitude"] > x_bounds[0]) &
                     (gdf["longitude"] < x_bounds[1])]
    
    tree = spatial.KDTree(gdf_subset[["longitude", "latitude"]].values)
    num_neighbors = [len(tree.query_ball_point(row[["longitude", "latitude"]].values, r=0.1)) for ix, row in gdf_subset.iterrows()]

    fig, ax = plt.subplots()
    
    ax.scatter(gdf_subset["longitude"], gdf_subset["latitude"],
               c=num_neighbors, s=2)
    
    ax.set_aspect("equal")
    
    fig.savefig("task3.png")