# -*- coding: utf-8 -*-

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# assume you have a "long-form" data frame
# see https://plotly.com/python/px-arguments/ for more options
stations = pd.read_csv("data/calif_nev_ncei_grav.csv")

# using px.scatter_mapbox
# fig = px.scatter_mapbox(stations, lat="latitude", lon="longitude", color="isostatic_anom", hover_name="station_id", hover_data=["isostatic_anom"], zoom=3)
# fig.update_layout(mapbox_style="open-street-map")
# fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})


# using graph_objects.Scattermapbox
# https://plotly.com/python-api-reference/generated/plotly.graph_objects.Scattermapbox.html
mapbox_access_token = "pk.eyJ1IjoieXVxaW5ndyIsImEiOiJja2c1eDkyM2YweXE0MnBubmI5Y2xkb21kIn0.EfyVLEhdszs_Yzdz86hXSA"

app.layout = html.Div(children=[
    # title
    html.H3(
        children='Geospatial Data Visualization for Land Gravity Surveys',
    ),

    # layer selection radio buttons
    html.Label('Choose different visualization'),
    dcc.RadioItems(
        id="map-type",
        options=[
            {'label': 'Heatmap', 'value': 'heatmap'},
            {'label': 'Scatter Plot', 'value': 'scatterplot'},
        ],
        value='scatterplot',
    ),

    # map
    dcc.Graph(
        id='map',
    ),

    # transect scatter plot
    dcc.Graph(
        id='transect',
        className="six columns",
    ),
])


# change the layer of the map
@app.callback(
    Output('map', 'figure'),
    [Input('map-type', 'value')])
def update_figure(value):
    if value == 'scatterplot':
        fig = go.Figure(go.Scattermapbox(
            lat=stations.latitude,
            lon=stations.longitude,
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=4,
                color=stations.isostatic_anom,
                colorscale='spectral_r',
                # cmin=0, # define the range of the colorbar
                # cmax=80, # define the range of the colorbar
                showscale=True,
            ),
            # text=[stations.isostatic_anom], # hover data, cannot add more...
            customdata=list(zip(stations.isostatic_anom, stations.station_id)),
            hovertemplate="latitude: %{lat}<br>"
                "longitude: %{lon}<br>"
                "value: %{customdata[0]}<br>"
                "station id: %{customdata[1]}",
        ))
    else:
        fig = go.Figure(go.Densitymapbox(
            lat=stations.latitude, 
            lon=stations.longitude, 
            z=stations.isostatic_anom, 
            radius=10,
            colorscale='spectral_r',
            customdata=list(zip(stations.isostatic_anom, stations.station_id)),
            hovertemplate="latitude: %{lat}<br>"
                "longitude: %{lon}<br>"
                "value: %{customdata[0]}<br>"
                "station id: %{customdata[1]}",
        ))

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
            zoom=5
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
    )
    return fig

#update the transect
@app.callback(
    Output('transect', 'figure'),
    [Input('map', 'clickData')])
def update_transect(clickData):
    fig = px.scatter(title="Transect")
    if clickData is not None:
        station = clickData['points'][0]['customdata'][0]
        fig = px.scatter(x=[1], y=[station], title="Transect")
        fig.update_layout(transition_duration=500)
    fig.update(layout=dict(title=dict(x=0.5)))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)