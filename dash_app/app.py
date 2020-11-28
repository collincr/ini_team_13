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
import dash_bootstrap_components as dbc
import json

from image_overlay_utils import get_ca_boundary, get_nv_boundary, get_ca_raster_image_from_file, \
    get_nv_raster_image_from_file
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

df_task2 = pd.DataFrame(columns=['distance', 'elevation', 'gravity'])
gdf = gpd.read_file("data/ca_nvda_grav.geojson")
gdf = gdf.to_crs('EPSG:2163')
origin = []
distance = 0
last_clicks = 0

df_task4 = pd.DataFrame(columns=['isostatic_anom', 'station_id'])
station_num = df_task4.shape[0]
remain_num = [i * 10 for i in list(range(int(station_num / 10)))]
df_task4 = df_task4.take(remain_num)

with open('data/cafault.geojson') as json_file:
    cafault_json = json.load(json_file)

with open('data/nvfault.geojson') as json_file:
    nvfault_json = json.load(json_file)

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
    "source": get_ca_raster_image_from_file(),
    "coordinates": get_ca_boundary(),
    'opacity': 0.3
}

nv_raster_layer = {
    "sourcetype": "image",
    "source": get_nv_raster_image_from_file(),
    "coordinates": get_nv_boundary(),
    'opacity': 0.3
}

ca_fault_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "grey",
    "opacity": 0.8,
    "source": cafault_json,
}

nv_fault_layer = {
    "sourcetype": "geojson",
    "sourcelayer": "fault",
    "type": "line",
    "color": "grey",
    "opacity": 0.8,
    "source": nvfault_json,
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
            fault_selection_radio_group(),
            html.Button('Clear selected data', id='button-transect', style={"display": "block"}, n_clicks=0),
            main_map()
        ],
            id="main-left", className="seven columns"),
        html.Div([
            transect_intro(),
            dcc.Graph(id='transect-gravity', className="transect-graph"),
            html.Hr(),
            task4_row()
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
                    html.P('Select visualization type', className="title-with-helper"),
                    html.A(className="far fa-question-circle helper-icon", id="layer-helper"),
                ], className="title"),
                dbc.Modal(
                    [
                        dbc.ModalHeader("Visualization Type Instructions"),
                        dbc.ModalBody(dcc.Markdown(texts.help_text)),
                        dbc.ModalFooter(
                            dbc.Button("Close", id="close-centered", className="ml-auto")
                        ),
                    ],
                    id="modal-centered",
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
        dcc.RadioItems(
            id="map-type",
            options=[
                {'label': 'Scatter Plot', 'value': 'scatterplot'},
                {'label': 'Spatial Density Heatmap', 'value': 'heatmap'},
                {'label': 'Interpolated Plot', 'value': 'interpolated'},
                {'label': 'Fault Dataset', 'value': 'fault'},
            ],
            labelStyle={"display": "inline-block"},
            value='scatterplot',
        ),
    ], className="radio-group")


# fault selection radio buttons
def fault_selection_radio_group():
    return html.Div(children=[
        html.Span("Extra layers: "),
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


# t4
def t4_selection_radio_group():
    return html.Div(children=[
        dcc.RadioItems(
            id="t4_type",
            options=[
                {'label': 'Click each station individually', 'value': 0},
                {'label': 'Use the box select tool', 'value': 1},
            ],
            labelStyle={"display": "inline-block"},
            value=0,
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
            # html.A(className="far fa-question-circle helper-icon", id="transect-helper"),
            # dbc.Tooltip(
            #     dbc.PopoverBody(dcc.Markdown("something that you want to put in the tooltip")),
            #     target="transect-helper",
            #     placement="right",
            # ),
        ], className="title"),
        html.Div(id="transect-intro-text", children=dcc.Markdown(texts.transect_intro_text)),
    ], id="transect-intro")


# task4
def task4_row():
    return html.Div([
        html.Div(children=[
            html.P('Distribution and ranking of gravity anomaly values', className="title-with-helper"),
            html.A(className="far fa-question-circle helper-icon", id="task4-helper"),
            dbc.Tooltip(
                dbc.PopoverBody(dcc.Markdown(texts.task4_helper_text)),
                target="task4-helper",
                placement="top",
            ),
        ], className="title"),
        html.Div(id="task4-intro-text", children=dcc.Markdown(texts.task4_intro_text)),
        t4_selection_radio_group(),
        dcc.Graph(
            id='task-4',
            figure={
                'data': [{
                    'x': list(range(df_task4.shape[0])),
                    'y': df_task4.isostatic_anom,
                    'type': 'bar'
                }],
                'layout': {
                    'bargap': 0
                }
            }
        )], id='task4-section')


# create the scatter plot layer
def create_scatter_plot(withFault=False):
    fig = go.Figure(go.Scattermapbox(
        lat=stations.latitude,
        lon=stations.longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=5,
            color=stations.isostatic_anom,
            colorscale='spectral_r',
            showscale=True,
            colorbar=dict(title=dict(text="Isostatic<br>Anomaly<br>(mGal)", side="bottom")),
        ),
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
                      "Latitude: %{lat}°<br>"
                      "Longitude: %{lon}°<br>"
                      "Isostatic Anomaly: %{customdata[0]} mGal<br>"
                      "Elevation: %{customdata[2]} ft<extra></extra>",
        name="stations",
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, ca_fault_layer, nv_fault_layer])
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
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
                      "Latitude: %{lat}°<br>"
                      "Longitude: %{lon}°<br>"
                      "Isostatic Anomaly: %{customdata[0]} mGal<br>"
                      "Elevation: %{customdata[2]} ft<extra></extra>",
        name="stations",
    ))
    if (withFault):
        fig.update_layout(mapbox_layers=[county_border_layer, ca_fault_layer, nv_fault_layer])
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
        fig.update_layout(mapbox_layers=[county_border_layer, ca_fault_layer, nv_fault_layer, ca_raster_layer, nv_raster_layer])
    else:
        fig.update_layout(mapbox_layers=[county_border_layer, ca_raster_layer, nv_raster_layer])
    return fig

def create_fault_dataset():
    fig = go.Figure(go.Densitymapbox(
        lat=stations[:1].latitude,
        lon=stations[:1].longitude,
        opacity=0,
        showscale=False,
        hoverinfo='skip',
    ))
    fig.update_layout(mapbox_layers=[county_border_layer, ca_fault_layer, nv_fault_layer])
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
    [Input('map-type', 'value')],
    [Input('display-fault', 'value')])
def update_figure(value, fault_checklist):
    with_fault = False
    if (fault_checklist == ['fault']):
        with_fault= True
    if value == 'scatterplot':
        fig = create_scatter_plot(with_fault)
    elif value == 'heatmap':
        fig = create_density_heatmap(with_fault)
    elif value =='interpolated':
        fig = create_image_overlay(with_fault)
    else:
        fig = create_fault_dataset()

    fig.update_layout(
        hovermode='closest',
        mapbox=dict(
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
@app.callback([
    Output('transect-gravity', 'figure'),
    Output('task-4', 'figure')],
    [Input('map', 'clickData'),
     Input('map', 'selectedData'),
     Input('button-transect', 'n_clicks'),
     Input('t4_type', 'value')
     ])
def update_charts(clickData, selected_data, clicks, value):
    # 0 : click, 1 : select box
    task4_type = value

    # global cur_task4_type
    # # 0 : click, 1 : select box
    # if cur_task4_type != value:
    #     clicks = 0
    # task4_type = value

    layout = dict(
        autosize=True,
        title=dict(x=0.5),
        margin=dict(l=0, r=0, b=0, t=40),
        xaxis_title=" distance (m)",
        # paper_bgcolor="LightSteelBlue",
        # plot_bgcolor="#e6ecf5",
        height=300
    )

    bar_layout = dict(
        height=300,
        bargap=0.1,
        xaxis_type="category",
        xaxis_title="Station ID",
        yaxis_title="Isostatic Anomaly (mGal)"
    )

    global df_task2, df_task4, last_clicks, origin, distance
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    if task4_type is 0:
        fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='Distribution and ranking')
    elif task4_type is 1:
        df_task4 = stations

    if clicks != last_clicks:
        last_clicks = clicks
        df_task2 = pd.DataFrame(columns=['distance', 'elevation', 'gravity'])
        origin = []
        distance = 0

        if task4_type is 0:
            df_task4 = pd.DataFrame(columns=['isostatic_anom', 'station_id'])
            fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='Distribution and ranking')

    elif clickData:
        station_id = clickData['points'][0]['customdata'][1]
        index = stations.index[stations.station_id == station_id].tolist()[0]
        station = gdf.loc[index]
        # print(str(station.station_id) + ": " + str(station.geometry))
        if not origin:
            origin = station.geometry
        distance += origin.distance(station.geometry)
        df_task2 = df_task2.append({'distance': distance, 'elevation': clickData['points'][0]['customdata'][2],
                                    'gravity': clickData['points'][0]['customdata'][0]}, ignore_index=True)
        df_task2 = df_task2.sort_values('distance').reset_index(drop=True)

        origin = station.geometry

        if task4_type is 0:
            station_id = str(clickData['points'][0]['customdata'][1])
            iso = clickData['points'][0]['customdata'][0]

            if station_id not in df_task4['station_id'].tolist():
                df_task4 = df_task4.append({'isostatic_anom': iso, 'station_id': station_id}, ignore_index=True)
            df_task4 = df_task4.sort_values('isostatic_anom', ascending=False)
            df_task4 = df_task4.reset_index(drop=True)

            colors = ["blue", ] * len(df_task4['station_id'])
            to_be_change_color = df_task4[df_task4['station_id'] == station_id].index.item()
            colors[to_be_change_color] = "crimson"

            fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='Distribution and ranking',
                          color="station_id", color_discrete_sequence=colors)  # color_discrete_map=m)

    # Add traces
    fig.add_trace(
        go.Scatter(x=df_task2.distance, y=df_task2.gravity, name="gravity"),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df_task2.distance, y=df_task2.elevation, name="elevation"),
        secondary_y=True,
    )

    fig.update(layout=layout)
    fig.update(layout=dict(title=dict(text="Transect",x=0.5)))

    # Set x-axis title
    fig.update_xaxes(title_text="Distance (m)")

    # Set y-axes titles
    fig.update_yaxes(title_text="Isostatic Anomaly (mGal)", secondary_y=False)
    fig.update_yaxes(title_text="Elevation (ft)", secondary_y=True)

    if task4_type is 1:
        if not selected_data:
            fig3 = px.bar(x=['a'], y=['a'])
            return fig, fig3

        df_task4 = stations
        if selected_data and selected_data['points']:
            df_task4 = pd.DataFrame(columns=['isostatic_anom', 'station_id'])
            for point in selected_data['points']:
                df_task4 = df_task4.append(
                    {'isostatic_anom': point['customdata'][0], 'station_id': point['customdata'][1]}, ignore_index=True)

        # Update bar chart
        df_task4 = df_task4.sort_values('isostatic_anom', ascending=False)
        df_task4 = df_task4.reset_index(drop=True)
        fig3 = px.bar(x=list(range(df_task4.shape[0])), y=df_task4.isostatic_anom)
        fig3.update_layout(bargap=0)

        if clickData:
            colors = ["blue", ] * len(df_task4['station_id'])
            station_id = clickData['points'][0]['customdata'][1]

            if station_id in df_task4['station_id'].tolist():
                to_be_change_color = df_task4[df_task4['station_id'] == station_id].index.item()
                colors[to_be_change_color] = "crimson"

                fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='t4', color="station_id",
                              color_discrete_sequence=colors)  # color_discrete_map=m)

    fig3.update(layout=layout)
    fig3.update(layout=bar_layout)

    return fig, fig3


@app.callback(
    Output("modal-centered", "is_open"),
    [Input("layer-helper", "n_clicks"), Input("close-centered", "n_clicks")],
    [State("modal-centered", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
