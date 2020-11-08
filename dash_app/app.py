# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

from image_overlay_utils import get_ca_boundary, get_nv_boundary, get_ca_raster_image_from_file, get_nv_raster_image_from_file

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Geospatial Data Visualization for Land Gravity Surveys"

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

mapbox_access_token = "pk.eyJ1IjoieXVxaW5ndyIsImEiOiJja2c1eDkyM2YweXE0MnBubmI5Y2xkb21kIn0.EfyVLEhdszs_Yzdz86hXSA"

intro_text = """
**Introduction**

This application is an interactive geospacial data visualization tool for you to discover the gravity anomaly data in California and Nevada.

Gravity is not the same everywhere on Earth, but changes with many known and measurable factors, such as tidal forces. 
A sequence of gravity corrections are applied to the original gravity reading and result in various named gravity anomalies. 
There are mainly four kinds of gravity anomalies: observed gravity anomaly, free air gravity anomaly, Bouguer gravity anomaly, and isostatic gravity anomaly. 
You can learn more about gravity anomalies from [USGS's publication here](https://pubs.usgs.gov/fs/fs-0239-95/fs-0239-95.pdf).

In this application, you can select different types of visualizations to explore the distribution of isostatic anomaly values and the metadata from the stations.
In addition, you can interact with the map to view the transect or the distribution of the data according to the instrutions in each section.

"""

transect_intro_text = """
**Transect**

These two charts show how gravity and elevation vary along a line. You can select any points on the map and clear the data by clicking the "CLEAR TRANSECT
DATA" button.
"""

task4_intro_text = """
**Distribution and ranking of gravity anomaly values**

Here you can select multiple stations on the map, and see how one station compares to all the others.

Click one station on the map to highlight it in the graph below.

"""


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
            intro(),
            html.Hr(),
            layer_selection_radio_group(),

            # tile_selection_radio_group(),
            main_map()
        ],
            id="main-left", className="eight columns"),
        html.Div([
            transect_intro(),
            dcc.Graph(id='transect-gravity', className="transect-graph"),
            dcc.Graph(id='transect-elevation', className="transect-graph")],
            id="main-right", className="four columns"),
    ], id="main-row")


# intro
def intro():
    return html.Div(id="intro-text", children=dcc.Markdown(intro_text))


# layer selection radio buttons
def layer_selection_radio_group():
    return html.Div(children=[
        html.P('Select visualization type', className="title"),
        dcc.RadioItems(
            id="map-type",
            options=[
                {'label': 'Scatter Plot', 'value': 'scatterplot'},
                {'label': 'Density Heatmap', 'value': 'heatmap'},
                {'label': 'Interpolated Plot', 'value': 'interpolated'},
            ],
            labelStyle={"display": "inline-block"},
            value='scatterplot',
        ),
    ], className="radio-group")


# t4
def t4_selection_radio_group():
    return html.Div(children=[
        html.P('How you want to select stations:', className="title"),
        dcc.RadioItems(
            id="t4_type",
            options=[
                {'label': 'click each station on map', 'value': 0},
                {'label': 'select box', 'value': 1},
            ],
            labelStyle={"display": "inline-block"},
            value=0,
        ),
    ], className="radio-group")

# tile selection radio buttons (not in use now)
def tile_selection_radio_group():
    return html.Div(children=[
        html.P('Select tile type', className="title"),
        dcc.RadioItems(
            id="tile-type",
            options=[
                {"label": "default", "value": "light"},
                {"label": "open street map", "value": "open-street-map"},
                {"label": "satellite", "value": "satellite"},
                {"label": "dark", "value": "carto-darkmatter"},
            ],
            labelStyle={"display": "inline-block"},
            value='light',
        ),
    ], className="radio-group")


# the main map
def main_map():
    return dcc.Graph(
        id='map',
    )


# transect intro
def transect_intro():
    return html.Div(children=[
        html.Div(id="transect-intro-text", children=dcc.Markdown(transect_intro_text)),
        html.Button('Clear transect data', id='button-transect', n_clicks=0),
    ], id="transect-intro")


# task4
def task4_row():
    return html.Div([
        html.Div(id="task4-intro-text", children=dcc.Markdown(task4_intro_text)),
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
def create_scatter_plot():
    fig = go.Figure(go.Scattermapbox(
        lat=stations.latitude,
        lon=stations.longitude,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=4,
            color=stations.isostatic_anom,
            colorscale='spectral_r',
            showscale=True,
        ),
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
            "Latitude: %{lat}<br>"
            "Longitude: %{lon}<br>"
            "Isostatic Anomaly: %{customdata[0]}<extra></extra>",
        name="stations",
    ))
    fig.update_layout(mapbox_layers = [
        {
            "sourcetype": "vector",
            "sourcelayer": "County",
            "type": "line",
            "opacity": 0.1,
            "color": "grey",
            "source": [
                "https://gis-server.data.census.gov/arcgis/rest/services/Hosted/VT_2019_050_00_PY_D1/VectorTileServer/tile/{z}/{y}/{x}.pbf"
            ]
        }],
    )
    return fig


# create the density heatmap layer
def create_density_heatmap():
    fig = go.Figure(go.Densitymapbox(
        lat=stations.latitude, 
        lon=stations.longitude, 
        z=stations.isostatic_anom, 
        radius=10,
        colorscale='spectral_r',
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        hovertemplate="Station ID: %{customdata[1]}<br>"
            "Latitude: %{lat}<br>"
            "Longitude: %{lon}<br>"
            "Isostatic Anomaly: %{customdata[0]}<extra></extra>",
        name="stations",
    ))
    fig.update_layout(mapbox_layers = [
        {
            "sourcetype": "vector",
            "sourcelayer": "County",
            "type": "line",
            "opacity": 0.1,
            "color": "grey",
            "source": [
                "https://gis-server.data.census.gov/arcgis/rest/services/Hosted/VT_2019_050_00_PY_D1/VectorTileServer/tile/{z}/{y}/{x}.pbf"
            ]
        }],
    )
    return fig


# create the image overlay layer
def create_image_overlay():
    fig = go.Figure(go.Scattermapbox(
        # uncomment below to show the dots in the map
        # lat=stations.latitude,
        # lon=stations.longitude,
        # mode='markers',
        # marker=go.scattermapbox.Marker(
        #     size=4,
        #     color=stations.isostatic_anom,
        #     colorscale='spectral_r',
        #     showscale=True,
        # ),
        # customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        # hovertemplate="Latitude: %{lat}<br>"
        #     "Longitude: %{lon}<br>"
        #     "Value: %{customdata[0]}<br>"
        #     "Station ID: %{customdata[1]}<extra></extra>",
        # name="Stations",
    ))
    fig.update_layout(mapbox_layers=[
        {
            "sourcetype": "image",
            "source": get_ca_raster_image_from_file(),
            "coordinates": get_ca_boundary(),
            'opacity': 0.3
        },
        {
            "sourcetype": "image",
            "source": get_nv_raster_image_from_file(),
            "coordinates": get_nv_boundary(),
            'opacity': 0.3
        },
        {
            "sourcetype": "vector",
            "sourcelayer": "County",
            "type": "line",
            "opacity": 0.1,
            "color": "grey",
            "source": [
                "https://gis-server.data.census.gov/arcgis/rest/services/Hosted/VT_2019_050_00_PY_D1/VectorTileServer/tile/{z}/{y}/{x}.pbf"
            ]
        }],
        # showlegend=True, # let users choose whether to show the dots or not
    )
    return fig


# main layout of the application
app.layout = html.Div(children=[
    title(),
    html.Hr(),
    main_row(),
    task4_row(),
])


# change the layer of the map
@app.callback(
    Output('map', 'figure'),
    [Input('map-type', 'value')])
def update_figure(value):
    if value == 'scatterplot':
        fig = create_scatter_plot()
    elif value == 'heatmap':
        fig = create_density_heatmap()
    else:
        fig = create_image_overlay()

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
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
    )
    return fig


# update the charts
@app.callback([
    Output('transect-gravity', 'figure'),
    Output('transect-elevation', 'figure'),
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
        bargap=0.1,
        xaxis_type="category"
    )

    global df_task2, df_task4, last_clicks, origin, distance
    fig1 = px.line(df_task2, x='distance', y='gravity', title="Transect (gravity)").update_traces(mode="lines+markers")
    fig2 = px.line(df_task2, x='distance', y='elevation', title="Transect (elevation)").update_traces(
        mode="lines+markers")
    if task4_type is 0:
        fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='t4')
    elif task4_type is 1:
        df_task4 = stations

    if clicks != last_clicks:
        last_clicks = clicks
        df_task2 = pd.DataFrame(columns=['distance', 'elevation', 'gravity'])
        fig1 = px.line(df_task2, x='distance', y='gravity', title="Transect (gravity)").update_traces(
            mode="lines+markers")
        fig2 = px.line(df_task2, x='distance', y='elevation', title="Transect (elevation)").update_traces(
            mode="lines+markers")
        origin = []
        distance = 0

        if task4_type is 0:
            df_task4 = pd.DataFrame(columns=['isostatic_anom', 'station_id'])
            fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='t4')

    elif clickData:
        station_id = clickData['points'][0]['customdata'][1]
        index = stations.index[stations.station_id == station_id].tolist()[0]
        station = gdf.loc[index]
        if not origin:
            origin = station.geometry
        distance += origin.distance(station.geometry)
        df_task2 = df_task2.append({'distance': distance, 'elevation': clickData['points'][0]['customdata'][2],
                                    'gravity': clickData['points'][0]['customdata'][0]}, ignore_index=True)
        df_task2 = df_task2.sort_values('distance').reset_index(drop=True)
        fig1 = px.line(df_task2, x='distance', y='gravity', title="Transect (gravity)").update_traces(
            mode="lines+markers")
        fig2 = px.line(df_task2, x='distance', y='elevation', title="Transect (elevation)").update_traces(
            mode="lines+markers")
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
            colors[ to_be_change_color ]  = "crimson"

            fig3 = px.bar(df_task4, x='station_id', y='isostatic_anom', title='t4',color="station_id", color_discrete_sequence=colors) #color_discrete_map=m)

    fig1.update(layout=layout)
    fig2.update(layout=layout)

    if task4_type is 1:
        if not selected_data:
            fig3 = px.bar(x=['a'], y=['a'])
            return fig1, fig2, fig3

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

    fig3.update(layout=bar_layout)

    return fig1, fig2, fig3


if __name__ == '__main__':
    app.run_server(host='0.0.0.0', debug=True)
