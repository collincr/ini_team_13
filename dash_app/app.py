# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.
import math

import dash
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from dash.dependencies import Input, Output, State
from shapely.geometry import Point
import dash_bootstrap_components as dbc
import json

from image_overlay_utils import get_ca_boundary, get_nv_boundary, get_ca_isostatic_raster_image_from_file, \
    get_nv_isostatic_raster_image_from_file, get_ca_bouguer_raster_image_from_file, get_nv_bouguer_raster_image_from_file
import texts

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
        'crossorigin': 'anonymous'
    },
]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Geospatial Data Visualization for Land Gravity Surveys"
server = app.server

stations = pd.read_csv("data/ca_nvda_grav.csv").sort_values('isostatic_anom', ascending=False)
stations['station_id'] = stations['station_id'].str.strip()

empty_task2_df = pd.DataFrame(columns=['distance', 'elevation', 'isostatic_anom', 'Free_air_anom', 'Bouguer_anom_267', 'obs_grav'])
empty_task4_df = pd.DataFrame(columns=['isostatic_anom', 'station_id', 'Free_air_anom', 'Bouguer_anom_267', 'obs_grav'])
gdf = gpd.read_file("data/ca_nvda_grav.geojson")
gdf = gdf.to_crs('EPSG:2163')

with open('data/hazfaults2014_proj_normal.geojson') as json_file:
    qfault_normal_json = json.load(json_file)

with open('data/hazfaults2014_proj_thrust.geojson') as json_file:
    qfault_thrust_json = json.load(json_file)

with open('data/hazfaults2014_proj_strikeslip.geojson') as json_file:
    qfault_strikeslip_json = json.load(json_file)

with open('data/hazfaults2014_proj_unassigned.geojson') as json_file:
    qfault_unassigned_json = json.load(json_file)

mapbox_access_token = "pk.eyJ1IjoieXVxaW5ndyIsImEiOiJja2c1eDkyM2YweXE0MnBubmI5Y2xkb21kIn0.EfyVLEhdszs_Yzdz86hXSA"

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

# title
def title():
    return html.H3(
        id="title",
        children='Geospatial Data Visualization for Land Gravity Surveys',
    )


# main row
def main_row():
    return html.Div([
        html.Div([
            layer_selection_intro(),
            layer_selection_radio_group(),
            mapbox_style_selection_radio_group(),
            anomaly_selection_radio_group(),
            fault_selection_radio_group(),
            html.Button('Clear selected data', id='button-transect', style={"display": "block"}, n_clicks=0),
            main_map()
        ],
            id="main-left", className="seven columns"),
        html.Div([
            transect_intro(),
            dcc.Graph(id='transect-graph', className="transect-graph"),
            html.Hr(),
            task4_row(),
            dcc.Store(id='store'), #, storage_type='session'
        ],
            id="main-right", className="five columns"),
    ], id="main-row")


# intro
def intro_row():
    return html.Div(id="intro-text", children=dcc.Markdown(texts.intro_text))


# layer selection introduction
def layer_selection_intro():
    return html.Div(children=[
        html.Div(
            [
                html.Div(children=[
                    html.P('Main Visualization Map', className="title-with-helper"),
                    html.A(className="far fa-question-circle helper-icon", id="layer-helper"),
                ], className="title"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Introduction to the Visualization Types"),
                        dbc.ModalBody(dcc.Markdown(texts.help_text)),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="layer-helper-close", className="ml-auto")
                        ),
                    ],
                    id="layer-helper-modal",
                    centered=True,
                ),
                html.Div(dcc.Markdown(texts.layer_selection_intro_text)),
            ],
            id="layer-help"
        )
    ], className="layer-selection-intro")


# layer selection radio buttons
def layer_selection_radio_group():
    return html.Div(children=[
        html.Span("Select visualization type: ", className="label"),
        dcc.RadioItems(
            id="map-type",
            options=[
                {'label': 'Scatter Plot', 'value': 'scatterplot'},
                {'label': 'Interpolated Plot', 'value': 'interpolated'},
                {'label': 'Spatial Density Heatmap', 'value': 'heatmap'},
                {'label': 'Fault Dataset', 'value': 'fault'},
            ],
            labelStyle={"display": "inline-block"},
            value='scatterplot',
            style={'display': 'inline'},
        ),
    ], className="radio-group")


# fault selection radio buttons
def fault_selection_radio_group():
    return html.Div(children=[
        html.Span("Extra layers: ", className="label"),
        dcc.Checklist(
            id="display-fault",
            options=[
                {'label': 'Fault dataset', 'value': 'fault'},
            ],
            value=[],
            labelStyle={"display": "inline-block"},
            style={'display': 'inline'},
        )  
    ], className="radio-group")


# tile selection radio buttons
def mapbox_style_selection_radio_group():
    return html.Div(children=[
        html.Span('Select mapbox style: ', className="label"), 
        dcc.RadioItems(
            id="mapbox-style",
            options=[
                {"label": "Light", "value": "light"},
                {"label": "Dark", "value": "carto-darkmatter"},
                {"label": "Open Street Map", "value": "open-street-map"},
                {"label": "Satellite", "value": "satellite"},
            ],
            labelStyle={"display": "inline-block"},
            value='light',
            style={'display': 'inline'},
        ),
    ], className="radio-group")


# layer selection radio buttons
def anomaly_selection_radio_group():
    return html.Div(children=[
        html.Span("Type of gravity anomaly: ", className="label"),
        dcc.RadioItems(
            id="anomaly-type",
            options=[
                {'label': 'Isostatic Anomaly', 'value': 'isostatic'},
                {'label': 'Free Air Anomaly', 'value': 'freeair'},
                {'label': 'Bouguer Anomaly', 'value': 'bouguer'},
                {'label': 'Observed Anomaly', 'value': 'observed'}
            ],
            labelStyle={"display": "inline-block"},
            style={'display': 'inline'},
            value='isostatic',
        ),
    ], className="radio-group")


# t4
def t4_selection_radio_group():
    return html.Div(children=[
        dcc.RadioItems(
            id="t4_type",
            options=[
                {'label': 'Click each station individually', 'value': 'click'},
                {'label': 'Use the box select tool', 'value': 'box'},
            ],
            labelStyle={"display": "inline-block"},
            value='click',
        ),
    ], className="radio-group")


# the main map
def main_map():
    return dcc.Graph(
        id='map',
        config={
            'modeBarButtonsToRemove': ['lasso2d'],
            'displaylogo': False,
            'displayModeBar': True,
        }
    )


# transect intro
def transect_intro():
    return html.Div(children=[
        html.Div(children=[
            html.P('Transect', className="title-with-helper"),
        ], className="title"),
        html.Div(id="transect-intro-text", children=dcc.Markdown(texts.transect_intro_text)),
    ], id="transect-intro")


# task4
def task4_row():
    return html.Div([
        html.Div(children=[
        html.Div(
            [
                html.Div(children=[
                    html.P('Distribution and ranking of gravity anomaly values', className="title-with-helper"),
                    html.A(className="far fa-question-circle helper-icon", id="task4-helper"),
                ], className="title"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Distribution and Ranking Graph Instructions"),
                        dbc.ModalBody(dcc.Markdown(texts.task4_helper_text)),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="task4-helper-close", className="ml-auto")
                        ),
                    ],
                    id="task4-helper-modal",
                    centered=True,
                ),
                html.Div(id="task4-intro-text", children=dcc.Markdown(texts.task4_intro_text)),
            ],
            id="task4-help"
        ),
        t4_selection_radio_group(),
        dcc.Graph(id='task-4')
    ], id='task4-section')
    ])


# create the scatter plot layer
def create_scatter_plot(withFault=False, anomaly_type='isostatic'):
    marker_color = stations.isostatic_anom
    colorbar_title = "Isostatic<br>Anomaly"
    if anomaly_type == 'bouguer':
        marker_color = stations.Bouguer_anom_267
        colorbar_title = "Bouguer<br>Anomaly"
    elif anomaly_type == 'freeair':
        marker_color = stations.Free_air_anom
        colorbar_title = "Free Air<br>Anomaly"
    elif anomaly_type == 'observed':
        marker_color = stations.obs_grav
        colorbar_title = "Observed<br>Anomaly"
    
    fig = go.Figure(go.Scattermapbox(
        lat=stations.latitude,
        lon=stations.longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color=marker_color,
            colorscale='spectral_r',
            showscale=True,
            colorbar=dict(title=dict(text=colorbar_title + "<br>(mGal)", side="bottom")),
        ),
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft, stations.Free_air_anom, stations.Bouguer_anom_267, stations.obs_grav)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
                      "Latitude: %{lat}°<br>"
                      "Longitude: %{lon}°<br>"
                      "Isostatic Anomaly: %{customdata[0]} mGal<br>"
                      "Free Air Anomaly: %{customdata[3]} mGal<br>"
                      "Bouguer Anomaly: %{customdata[4]} mGal<br>"
                      "Observed Anomaly: %{customdata[5]} mGal<br>"
                      "Elevation: %{customdata[2]} ft<extra></extra>",
        name="stations",
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, qfault_normal_layer, qfault_strikeslip_layer, qfault_thrust_layer, qfault_unassigned_layer])
    else:
        fig.update_layout(mapbox_layers=[county_border_layer])
    return fig


# create the density heatmap layer
def create_density_heatmap(withFault=False):
    fig = go.Figure(go.Densitymapbox(
        lat=stations.latitude,
        lon=stations.longitude,
        z=stations.isostatic_anom,
        radius=10,  # default: 30
        colorscale='spectral_r',
        colorbar=dict(
            title=dict(text="Density of<br>Stations", side="bottom"),
            outlinewidth=0,
            tickmode='array',
            ticktext=['low', 'high'],
            tickvals=[1, 99],
        ),
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft, stations.Free_air_anom, stations.Bouguer_anom_267, stations.obs_grav)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
                      "Latitude: %{lat}°<br>"
                      "Longitude: %{lon}°<br>"
                      "Isostatic Anomaly: %{customdata[0]} mGal<br>"
                      "Free Air Anomaly: %{customdata[3]} mGal<br>"
                      "Bouguer Anomaly: %{customdata[4]} mGal<br>"
                      "Observed Anomaly: %{customdata[5]} mGal<br>"
                      "Elevation: %{customdata[2]} ft<extra></extra>",
        name="stations",
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, qfault_normal_layer, qfault_strikeslip_layer, qfault_thrust_layer, qfault_unassigned_layer])
    else:
        fig.update_layout(mapbox_layers=[county_border_layer])
    return fig


# create the image overlay layer
def create_image_overlay(withFault=False):
    fig = go.Figure(go.Densitymapbox(
        lat=stations[:1].latitude,
        lon=stations[:1].longitude,
        z=stations.isostatic_anom,
        colorscale='spectral_r',
        colorbar=dict(
            title=dict(text="Isostatic<br>Anomaly<br>(mGal)", side="bottom"),
            outlinewidth=0,
        ),
        opacity=0,
        hoverinfo='skip',
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, qfault_normal_layer, qfault_strikeslip_layer, qfault_thrust_layer, qfault_unassigned_layer, ca_raster_layer, nv_raster_layer])
    else:
        fig.update_layout(mapbox_layers=[county_border_layer, ca_raster_layer, nv_raster_layer])
    return fig

# create the image overlay layer for bouguer anomoly
def create_image_overlay_bouguer(withFault=False):
    fig = go.Figure(go.Densitymapbox(
        lat=stations[:1].latitude,
        lon=stations[:1].longitude,
        z=stations.Bouguer_anom_267,
        colorscale='spectral_r',
        colorbar=dict(
            title=dict(text="Bouguer<br>Anomaly<br>(mGal)", side="bottom"),
            outlinewidth=0,
        ),
        opacity=0,
        hoverinfo='skip',
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, qfault_normal_layer, qfault_strikeslip_layer, qfault_thrust_layer, qfault_unassigned_layer, ca_bouguer_raster_layer, nv_bouguer_raster_layer])
    else:
        fig.update_layout(mapbox_layers=[county_border_layer, ca_bouguer_raster_layer, nv_bouguer_raster_layer])
    return fig

def create_fault_dataset():
    fig = go.Figure(go.Densitymapbox(
        lat=stations[:1].latitude,
        lon=stations[:1].longitude,
        opacity=0,
        showscale=False,
        hoverinfo='skip',
    ))
    fig.update_layout(mapbox_layers=[county_border_layer, qfault_normal_layer, qfault_strikeslip_layer, qfault_thrust_layer, qfault_unassigned_layer])
    return fig


# main layout of the application
app.layout = html.Div(children=[
    title(),
    html.Hr(),
    intro_row(),
    html.Hr(),
    main_row(),
])


# change the layer of the map
@app.callback(
    Output('map', 'figure'),
    [Input('map-type', 'value'),
     Input('display-fault', 'value'),
     Input('anomaly-type', 'value'),
     Input('mapbox-style', 'value')])
def update_figure(value, fault_checklist, anomaly_type, mapbox_style):
    with_fault = False
    if (fault_checklist == ['fault']):
        with_fault= True
    if value == 'scatterplot':
        fig = create_scatter_plot(with_fault, anomaly_type)
    elif value == 'heatmap':
        fig = create_density_heatmap(with_fault)
    elif value =='interpolated':
        fig = create_image_overlay(with_fault)
    elif value =='interpolated_bouguer':
        fig = create_image_overlay_bouguer(with_fault)
    else:
        fig = create_fault_dataset()

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
            style=mapbox_style,
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=37.415229,
                lon=-122.06265
            ),
            pitch=0,
            zoom=5,
            uirevision=True,
        ),
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        height=700,
    )
    return fig

# update the charts
@app.callback(
    [Output('transect-graph', 'figure'),
     Output('task-4', 'figure'),
     Output('store', 'data')],
    [Input('map', 'clickData'),
     Input('map', 'selectedData'),
     Input('button-transect', 'n_clicks'),
     Input('t4_type', 'value'),
     Input('anomaly-type', 'value')],
    State('store', 'data')
)
def update_charts(clickData, selected_data, clicks, task4_type, anomaly_type, data):
    # read the data from the store
    empty_task2 = empty_task2_df.to_json(date_format='iso', orient='split')
    empty_task4 = empty_task4_df.to_json(date_format='iso', orient='split')
    data = data or {'last_clicks': 0, 'origin_x': 0, 'origin_y': 0, 'distance': 0, 'task2_df': empty_task2, 'task4_df': empty_task4, 'task4_box_df': empty_task4}
    last_clicks = data['last_clicks']
    origin = Point(data['origin_x'], data['origin_y'])
    distance = data['distance']
    df_task2 = pd.read_json(data['task2_df'], orient='split')
    df_task4 = pd.read_json(data['task4_df'], orient='split')
    df_task4_box = pd.read_json(data['task4_box_df'], orient='split')

    anomaly_data = df_task2.isostatic_anom
    anomaly_name = 'Isostatic Anomaly'
    anomaly_column_name = 'isostatic_anom'
    if anomaly_type == 'bouguer':
        anomaly_data = df_task2.Bouguer_anom_267
        anomaly_name = 'Bouguer Anomaly'
        anomaly_column_name = 'Bouguer_anom_267'
    elif anomaly_type == 'freeair':
        anomaly_data = df_task2.Free_air_anom
        anomaly_name = 'Free Air Anomaly'
        anomaly_column_name = 'Free_air_anom'
    elif anomaly_type == 'observed':
        anomaly_data = df_task2.obs_grav
        anomaly_name = 'Observed Anomaly'
        anomaly_column_name = 'obs_grav'

    layout = dict(
        autosize=True,
        title=dict(x=0.5),
        margin=dict(l=0, r=0, b=0, t=40),
        xaxis_title=" Distance (m)",
        height=300
    )

    bar_layout = dict(
        height=300,
        bargap=0.1,
        xaxis_type="category",
        xaxis_title="Station ID",
        yaxis_title=anomaly_name + " (mGal)",
        title=dict(text="Distribution and Ranking", x=0.5),
    )

    transect_fig = make_subplots(specs=[[{"secondary_y": True}]])

    task4_fig = px.bar()

    if clicks != last_clicks:
        last_clicks = clicks
        df_task2 = empty_task2_df
        df_task4 = empty_task4_df
        df_task4_box = empty_task4_df
        origin = Point(0, 0)
        distance = 0
        clickData = None
        selected_data = None
        data['last_clicks'] = clicks

    elif clickData:
        station_id = clickData['points'][0]['customdata'][1]
        index = stations.index[stations.station_id == station_id].tolist()[0]
        station = gdf.loc[index]
        # print(str(station.station_id) + ": " + str(station.geometry))
        if origin == Point(0, 0):
            origin = station.geometry

        if task4_type == 'click':
            # update task2
            distance += origin.distance(station.geometry)
            custom_data = clickData['points'][0]['customdata']
            df_task2 = df_task2.append({'distance': distance, 'elevation': custom_data[2],
                                        'isostatic_anom': custom_data[0], 'Free_air_anom': custom_data[3],
                                        'Bouguer_anom_267': custom_data[4], 'obs_grav': custom_data[5]}, ignore_index=True)
            df_task2 = df_task2.sort_values('distance').reset_index(drop=True)

            origin = station.geometry

            # update task4
            station_id = str(clickData['points'][0]['customdata'][1])

            if station_id not in df_task4['station_id'].tolist():
                df_task4 = df_task4.append({'isostatic_anom': custom_data[0], 'station_id': station_id, 'Free_air_anom': custom_data[3], 
                'Bouguer_anom_267': custom_data[4], 'obs_grav': custom_data[5]}, ignore_index=True)
            df_task4 = df_task4.sort_values(anomaly_column_name, ascending=False)
            df_task4 = df_task4.reset_index(drop=True)

            colors = [px.colors.qualitative.Plotly[0], ] * len(df_task4['station_id'])
            to_be_change_color = df_task4[df_task4['station_id'] == station_id].index.item()
            colors[to_be_change_color] = px.colors.qualitative.Plotly[1]

            task4_fig = px.bar(df_task4, x='station_id', y=anomaly_column_name, color="station_id", color_discrete_sequence=colors)

    # Add traces
    transect_fig.add_trace(
        go.Scatter(x=df_task2.distance, y=anomaly_data, name=anomaly_name),
        secondary_y=False,
    )

    transect_fig.add_trace(
        go.Scatter(x=df_task2.distance, y=df_task2.elevation, name="Elevation"),
        secondary_y=True,
    )

    transect_fig.update(layout=layout)
    transect_fig.update(layout=dict(title=dict(text="Transect",x=0.5)))

    # Set x-axis title
    transect_fig.update_xaxes(title_text="Distance (m)")

    # Set y-axes titles
    transect_fig.update_yaxes(title_text=anomaly_name + " (mGal)", secondary_y=False)
    transect_fig.update_yaxes(title_text="Elevation (ft)", secondary_y=True)

    if task4_type == 'box':
        if not selected_data:
            task4_fig = px.bar()
        if selected_data and selected_data['points']:
            for point in selected_data['points']:
                df_task4_box = df_task4_box.append(
                    {'isostatic_anom': point['customdata'][0], 'station_id': point['customdata'][1], 
                    'Free_air_anom': point['customdata'][3], 'Bouguer_anom_267': point['customdata'][4], 'obs_grav': custom_data[5]}, ignore_index=True)

            # Update bar chart
            df_task4_box = df_task4_box.drop_duplicates()
            df_task4_box = df_task4_box.sort_values(anomaly_column_name, ascending=False)
            df_task4_box = df_task4_box.reset_index(drop=True)
            task4_fig = px.bar(df_task4_box, x='station_id', y=anomaly_column_name)
            task4_fig.update_layout(bargap=0)

            if clickData:
                colors = [px.colors.qualitative.Plotly[0], ] * len(df_task4_box['station_id'])
                station_id = clickData['points'][0]['customdata'][1]

                if station_id in df_task4_box['station_id'].tolist():
                    to_be_change_color = df_task4_box[df_task4_box['station_id'] == station_id].index.item()
                    colors[to_be_change_color] = px.colors.qualitative.Plotly[1]

                    task4_fig = px.bar(df_task4_box, x='station_id', y=anomaly_column_name, color="station_id", color_discrete_sequence=colors)

    task4_fig.update(layout=layout)
    task4_fig.update(layout=bar_layout)

    # update the stored data
    data['origin_x'] = origin.x
    data['origin_y'] = origin.y
    data['distance'] = distance
    data['task2_df'] = df_task2.to_json(date_format='iso', orient='split')
    data['task4_df'] = df_task4.to_json(date_format='iso', orient='split')
    data['task4_box_df'] = df_task4_box.to_json(date_format='iso', orient='split')

    return transect_fig, task4_fig, data


@app.callback(
    Output("layer-helper-modal", "is_open"),
    [Input("layer-helper", "n_clicks"), Input("layer-helper-close", "n_clicks")],
    [State("layer-helper-modal", "is_open")],
)
def toggle_layer_helper_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("task4-helper-modal", "is_open"),
    [Input("task4-helper", "n_clicks"), Input("task4-helper-close", "n_clicks")],
    [State("task4-helper-modal", "is_open")],
)
def toggle_task4_helper_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
