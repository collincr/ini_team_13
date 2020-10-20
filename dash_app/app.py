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

from image_overlay_utils import get_image, get_boundary

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

stations = pd.read_csv("data/calif_nev_ncei_grav.csv").sort_values('isostatic_anom', ascending=False)

df_task2 = pd.DataFrame(columns=['latitude', 'elevation', 'gravity'])
last_clicks = 0

df_task4 = stations
station_num = df_task4.shape[0]
remain_num = [i * 10 for i in list(range(int(station_num / 10)))]
df_task4 = df_task4.take(remain_num)

mapbox_access_token = "pk.eyJ1IjoieXVxaW5ndyIsImEiOiJja2c1eDkyM2YweXE0MnBubmI5Y2xkb21kIn0.EfyVLEhdszs_Yzdz86hXSA"

intro_text = """
**Intro**

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Amet luctus venenatis lectus magna fringilla urna porttitor rhoncus. Enim nulla aliquet porttitor lacus luctus accumsan tortor posuere. Viverra mauris in aliquam sem fringilla ut morbi tincidunt augue. Mi proin sed libero enim sed faucibus. Consequat mauris nunc congue nisi vitae suscipit tellus mauris a. Lacus vel facilisis volutpat est velit egestas dui id ornare. Elit ullamcorper dignissim cras tincidunt lobortis feugiat. Suscipit tellus mauris a diam maecenas. Ornare arcu dui vivamus arcu felis bibendum ut. Odio morbi quis commodo odio. Et malesuada fames ac turpis egestas maecenas pharetra.
"""

transect_intro_text = """
**Transect**

Some introduction to transect...
"""

task4_intro_text = """
**Distribution and ranking of gravity anomaly values**

Some introduction to task4...
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
            main_map()], 
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
    ], id="radio-group")

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
    return go.Figure(go.Scattermapbox(
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
        hovertemplate="latitude: %{lat}<br>"
            "longitude: %{lon}<br>"
            "value: %{customdata[0]}<br>"
            "station id: %{customdata[1]}<extra></extra>",
    ))

# create the density heatmap layer
def create_density_heatmap():
    return go.Figure(go.Densitymapbox(
        lat=stations.latitude, 
        lon=stations.longitude, 
        z=stations.isostatic_anom, 
        radius=10,
        colorscale='spectral_r',
        customdata=list(zip(stations.isostatic_anom, stations.station_id, stations.sea_level_elev_ft)),
        hovertemplate="latitude: %{lat}<br>"
            "longitude: %{lon}<br>"
            "value: %{customdata[0]}<br>"
            "station id: %{customdata[1]}<extra></extra>",
    ))

# create the image overlay layer
def create_image_overlay():
    fig = px.scatter_mapbox(stations[:1], lat='latitude', lon='longitude', zoom=4, opacity=1)
    fig.update_layout(mapbox_layers = [
        {
            "sourcetype": "image",
            "source": get_image(),
            "coordinates": get_boundary(),
            'opacity': 0.3
        }]
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
    layout = dict(
        autosize=True,
        title=dict(x=0.5),
        margin=dict(l=0, r=0, b=0, t=40),
        # paper_bgcolor="LightSteelBlue",
        # plot_bgcolor="#e6ecf5",
        height=300
    )

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
        # fig1.update_layout(transition_duration=500)
        # fig2.update_layout(transition_duration=500)
    elif clickData is not None:
        df_task2 = df_task2.append({'latitude': clickData['points'][0]['lat'], 'elevation': clickData['points'][0]['customdata'][2],
                         'gravity': clickData['points'][0]['customdata'][0]}, ignore_index=True)
        df_task2 = df_task2.sort_values('latitude').reset_index(drop=True)
        fig1 = px.line(df_task2, x='latitude', y='gravity', title="Transect (gravity)").update_traces(mode="lines+markers")
        fig2 = px.line(df_task2, x='latitude', y='elevation', title="Transect (elevation)").update_traces(mode="lines+markers")
        # fig1.update_layout(transition_duration=500)
        # fig2.update_layout(transition_duration=500)
    fig1.update(layout=layout)
    fig2.update(layout=layout)

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