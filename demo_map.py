import geopandas as gpd
import pandas as pd
import folium
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib import cm




def get_max_res(bounds):
    return max((bounds[1] - bounds[0]) / 1000, 0.001)

def get_space_coords(x_bounds, y_bounds):
    xres_max = get_max_res(x_bounds)
    yres_max = get_max_res(y_bounds)
    return np.arange(y_bounds[0], y_bounds[1], yres_max), np.arange(x_bounds[0], x_bounds[1], xres_max)

def interpolate_2d(geometry, feature, x_bounds=None, y_bounds=None):
    if not x_bounds or not y_bounds:
        raise Exception("Must provide x_bounds and y_bounds")
    
    gy, gx = np.meshgrid(*get_space_coords(x_bounds, y_bounds) )
    return griddata(geometry, feature/(feature.max()-feature.min()) , (gx, gy), method="cubic")

if __name__ == "__main__":
    
    x_bounds=(-123, -121)
    y_bounds=(37, 39)
    
    gdf = gpd.read_file("data/geojson/calif_nev_ncei_grav.geojson")
    
    gdf_subset = gdf[(gdf["latitude"] > y_bounds[0]) &
                     (gdf["latitude"] < y_bounds[1]) &
                     (gdf["longitude"] > x_bounds[0]) &
                     (gdf["longitude"] < x_bounds[1])]
    
    m = folium.Map(tiles='openstreetmap', zoom_start=12, location=[37.8, -122.4])

    coord_list = list(zip(gdf_subset.geometry.x, gdf_subset.geometry.y))
    
    grid_1 = interpolate_2d(coord_list, gdf_subset["isostatic_anom"].values,
                            x_bounds=x_bounds, y_bounds=y_bounds)
    
    g = folium.raster_layers.ImageOverlay(grid_1.T[::-1], opacity=0.5,
                                          bounds=[[y_bounds[0], x_bounds[0]], [y_bounds[1], x_bounds[1]]],
                                          colormap=cm.seismic)
    g.add_to(m)
    
    for (k, row) in gdf_subset.iterrows():
        circ = folium.Circle(location=[row.geometry.y, row.geometry.x], radius=1, fill=True)
        circ.add_to(m)
        
    marker = folium.Marker(location=[37.415229, -122.06265])
    marker.add_to(m)
    
    m.save("maptest.html")



    
