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
stations = pd.read_csv("data/calif_nev_ncei_grav.csv").sort_values('isostatic_anom', ascending=False)

df_task2 = pd.DataFrame(columns=['latitude', 'elevation', 'gravity'])
last_clicks = 0

df_task4 = stations
station_num = df_task4.shape[0]
remain_num = [i * 10 for i in list(range(int(station_num / 10)))]
df_task4 = df_task4.take(remain_num)

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

    html.Button('Clear transect data', id='button-transect', n_clicks=0),

    # map
    dcc.Graph(
        id='map',
    ),

    # transect scatter plot
    dcc.Graph(
        id='transect-gravity'
        #className="six columns",
    ),

    # transect scatter plot
    dcc.Graph(
        id='transect-elevation'
        #className="six columns",
    ),

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
    )
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
            customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
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
            customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
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

#update the charts
@app.callback([
    Output('transect-gravity', 'figure'),
    Output('transect-elevation', 'figure'),
    Output('task-4', 'figure')],
    [Input('map', 'clickData'),
     Input('button-transect', 'n_clicks')])
def update_charts(clickData, clicks):
    # Update transect
    global df_task2, last_clicks
    fig1 = px.line(df_task2, x='latitude', y='gravity', title="Transect (gravity)").update_traces(mode="lines+markers")
    fig2 = px.line(df_task2, x='latitude', y='elevation', title="Transect (elevation)").update_traces(mode="lines+markers")
    if clicks != last_clicks:
        last_clicks = clicks
        df_task2 = pd.DataFrame(columns=['latitude', 'elevation', 'gravity'])
        fig1 = px.line(df_task2, x='latitude', y='gravity', title="Transect (gravity)").update_traces(
            mode="lines+markers")
        fig2 = px.line(df_task2, x='latitude', y='elevation', title="Transect (elevation)").update_traces(
            mode="lines+markers")
        fig1.update_layout(transition_duration=500)
        fig2.update_layout(transition_duration=500)
    elif clickData is not None:
        df_task2 = df_task2.append({'latitude': clickData['points'][0]['lat'], 'elevation': clickData['points'][0]['customdata'][2],
                         'gravity': clickData['points'][0]['customdata'][0]}, ignore_index=True)
        df_task2 = df_task2.sort_values('latitude').reset_index(drop=True)
        fig1 = px.line(df_task2, x='latitude', y='gravity', title="Transect (gravity)").update_traces(mode="lines+markers")
        fig2 = px.line(df_task2, x='latitude', y='elevation', title="Transect (elevation)").update_traces(mode="lines+markers")
        fig1.update_layout(transition_duration=500)
        fig2.update_layout(transition_duration=500)
    fig1.update(layout=dict(title=dict(x=0.5)))
    fig2.update(layout=dict(title=dict(x=0.5)))

    # Update bar chart
    fig3 = px.bar(x=list(range(df_task4.shape[0])), y=df_task4.isostatic_anom)
    fig3.update_layout(bargap=0)

    if clickData is not None:
        index = stations.index[stations['station_id'] == clickData['points'][0]['customdata'][1]].tolist()[0]
        x_center = stations.index.get_loc(index) / (1.0 * stations.shape[0]) * df_task4.shape[0]
        fig3.update_layout(
                           shapes=[
                               dict(
                                type="rect",
                                # x-reference is assigned to the x-values
                                xref="x",
                                # y-reference is assigned to the plot paper [0,1]
                                yref="y",
                                x0=x_center - 50,
                                y0=0,
                                x1=x_center + 50,
                                y1=clickData['points'][0]['customdata'][0],
                                fillcolor="gold",
                                opacity=0.9,
                                layer="above",
                                line_width=0,
                            )]
        )


    return fig1, fig2, fig3

if __name__ == '__main__':
    app.run_server(debug=True)