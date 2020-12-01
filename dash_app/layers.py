import json
from image_overlay_utils import get_ca_boundary, get_nv_boundary, get_ca_isostatic_raster_image_from_file, \
    get_nv_isostatic_raster_image_from_file, get_ca_bouguer_raster_image_from_file, get_nv_bouguer_raster_image_from_file, \
    get_ca_freeair_raster_image_from_file, get_nv_freeair_raster_image_from_file, get_ca_observed_raster_image_from_file, get_nv_observed_raster_image_from_file
    
with open('data/hazfaults2014_proj_normal.geojson') as json_file:
    qfault_normal_json = json.load(json_file)

with open('data/hazfaults2014_proj_thrust.geojson') as json_file:
    qfault_thrust_json = json.load(json_file)

with open('data/hazfaults2014_proj_strikeslip.geojson') as json_file:
    qfault_strikeslip_json = json.load(json_file)

with open('data/hazfaults2014_proj_unassigned.geojson') as json_file:
    qfault_unassigned_json = json.load(json_file)

county_border_layer = {
    "sourcetype": "vector",
    "sourcelayer": "County",
    "type": "line",
    "opacity": 0.1,
    "color": "grey",
    "source": [
        "https://gis-server.data.census.gov/arcgis/rest/services/Hosted/VT_2019_050_00_PY_D1/VectorTileServer/tile/{z}/{y}/{x}.pbf"
    ]
}

ca_raster_layer = {
    "sourcetype": "image",
    "source": get_ca_isostatic_raster_image_from_file(),
    "coordinates": get_ca_boundary(),
    'opacity': 0.3
}

nv_raster_layer = {
    "sourcetype": "image",
    "source": get_nv_isostatic_raster_image_from_file(),
    "coordinates": get_nv_boundary(),
    'opacity': 0.3
}

ca_bouguer_raster_layer = {
    "sourcetype": "image",
    "source": get_ca_bouguer_raster_image_from_file(),
    "coordinates": get_ca_boundary(),
    'opacity': 0.3
}

nv_bouguer_raster_layer = {
    "sourcetype": "image",
    "source": get_nv_bouguer_raster_image_from_file(),
    "coordinates": get_nv_boundary(),
    'opacity': 0.3
}

ca_freeair_raster_layer = {
    "sourcetype": "image",
    "source": get_ca_freeair_raster_image_from_file(),
    "coordinates": get_ca_boundary(),
    'opacity': 0.3
}

nv_freeair_raster_layer = {
    "sourcetype": "image",
    "source": get_nv_freeair_raster_image_from_file(),
    "coordinates": get_nv_boundary(),
    'opacity': 0.3
}

ca_observed_raster_layer = {
    "sourcetype": "image",
    "source": get_ca_observed_raster_image_from_file(),
    "coordinates": get_ca_boundary(),
    'opacity': 0.3
}

nv_observed_raster_layer = {
    "sourcetype": "image",
    "source": get_nv_observed_raster_image_from_file(),
    "coordinates": get_nv_boundary(),
    'opacity': 0.3
}

qfault_normal_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "blue",
    "opacity": 0.8,
    "source": qfault_normal_json,
}

qfault_thrust_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "yellow",
    "opacity": 0.8,
    "source": qfault_thrust_json,
}

qfault_strikeslip_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "red",
    "opacity": 0.8,
    "source": qfault_strikeslip_json,
}

qfault_unassigned_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "green",
    "opacity": 0.8,
    "source": qfault_unassigned_json,
}
