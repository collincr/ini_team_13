import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
from matplotlib import cm

import datashader as ds
import plotly.express as px

from PIL import Image

import pickle

### helper functions to calculate the data point to raster images
def get_max_res(bounds):
    return max((bounds[1] - bounds[0]) / 5000, 0.0002)

def get_space_coords(x_bounds, y_bounds):
    xres_max = get_max_res(x_bounds)
    yres_max = get_max_res(y_bounds)
    return np.arange(y_bounds[0], y_bounds[1], yres_max), np.arange(x_bounds[0], x_bounds[1], xres_max)

def interpolate_2d(geometry, feature, x_bounds=None, y_bounds=None):
    if not x_bounds or not y_bounds:
        raise Exception("Must provide x_bounds and y_bounds")
    
    gy, gx = np.meshgrid(*get_space_coords(x_bounds, y_bounds) )
    return griddata(geometry, feature/(feature.max()-feature.min()) , (gx, gy), method="cubic")


### get the image
def get_image():
    x_bounds=(-123, -121)
    y_bounds=(37, 39)

    gdf = gpd.read_file("data/ca_nvda_grav.geojson")

    gdf_subset = gdf[(gdf["latitude"] > y_bounds[0]) &
                    (gdf["latitude"] < y_bounds[1]) &
                    (gdf["longitude"] > x_bounds[0]) &
                    (gdf["longitude"] < x_bounds[1])]
    coord_list = list(zip(gdf_subset.geometry.x, gdf_subset.geometry.y))

    grid_1 = interpolate_2d(coord_list, gdf_subset["isostatic_anom"].values,
                            x_bounds=x_bounds, y_bounds=y_bounds)

    ## convert to colormap image
    im = Image.fromarray(np.uint8(cm.Spectral_r(grid_1)*255))
    return im

### get image directly from file
def get_ca_raster_image_from_file():
    im = Image.open(r"data/california_raster_final.png")
    return im

### get image directly from file
def get_nv_raster_image_from_file():
    im = Image.open(r"data/nevada_raster_final.png")
    return im

### get the boundary of the image
def get_boundary():
    df2 = pd.read_csv('data/ca_nvda_grav.csv')
    cvs2 = ds.Canvas(plot_width=5000, plot_height=5000)
    agg2 = cvs2.points(df2, x='longitude', y='latitude')

    coords_lat2, coords_lon2 = agg2.coords['latitude'].values, agg2.coords['longitude'].values
    coordinates2 = [[coords_lon2[0], coords_lat2[0]],
                [coords_lon2[-1], coords_lat2[0]],
                [coords_lon2[-1], coords_lat2[-1]],
                [coords_lon2[0], coords_lat2[-1]]]
    return coordinates2

### Get bounary of California state
def get_ca_boundary():
    coordinates_ca = []

    with open("data/coordinates_ca", "rb") as fp:
        coordinates_ca = pickle.load(fp)
    
    return coordinates_ca


### Get bounary of Nevada state
def get_nv_boundary():
    coordinates_nv = []

    with open("data/coordinates_nv", "rb") as fp:
        coordinates_nv = pickle.load(fp)
    
    return coordinates_nv