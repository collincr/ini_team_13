intro_text = """
**Introduction**

This application is an interactive geospatial data visualization tool for you to explore gravity anomaly data in California and Nevada.

Gravity is not the same everywhere on Earth. Geologists are interested in gravity because it tells us about the density of rocks underground. 
Higher gravity values are found over rocks that are denser, and lower gravity values are found over rocks that are less dense. Variations in gravity help geologists locate faults, mineral or petroleum resources, and groundwater reservoirs.

To use gravity data, geologists look at the “**gravity anomaly**”, which is the result of removing the effects of several known factors, such as tides and the rotation of the Earth, from the original gravity data. 
There are several different types of gravity anomaly, depending on how the original data were processed:
* The **observed gravity anomaly** is the result of correcting only for Earth rotation latitude, tidal effects, and instrument fluctuations.
* The **free air anomaly** has been further corrected for the elevation difference between sea level and the station.
* The **Bouguer anomaly** has been further corrected for the mass between sea level and the station.
* The **isostatic anomaly** has been further corrected for the effect of low density in the Earth’s crust beneath high mountains.

To read more about gravity data, you can read [USGS's publication here](https://pubs.usgs.gov/fs/fs-0239-95/fs-0239-95.pdf).

The datasets are sourced from: [National Centers for Environmental Information](https://www.ncei.noaa.gov/), [California’s Open Data website](https://data.ca.gov/), 
[U.S. General Services Administration](https://www.gsa.gov/), [USGS Mineral Resources Online Spatial Data](https://mrdata.usgs.gov/)

"""

transect_intro_text = """
This line chart shows how gravity and elevation vary along a line. 

You can digitize a line on the map by clicking any point on the scatter plot, 
and you can see how the gravity and elevation changes in terms of the distance from the starting point (the first selected point).
"""

task4_intro_text = """
This bar chart shows how the gravity of one station compares to other selected stations.

You can click on the scatter map, or use the box select tool in the menu bar to select data.
To learn more about how to use this visualization tool, click the question mark icon above.
"""

task4_helper_text = """
**Click each station individually**

If you wish to select each station individually, you can click on any point on the scatter map to highlight it in the graph below.
All the stations are sorted in descending order, and the point you've just selected is highlighted in red.

**Use the box select tool**

If you wish to select multiple stations at a time, you can use the box select tool in the menu bar and use your mouse to draw a rectangle on the scatter map.
All the stations are sorted in descending order. (Note: The transect graph will not be updated if you choose box select type)

"""

layer_selection_intro_text = """
You can select any of the different types of visualizations to view on the map. To learn more about these visualization types and how to use the map, click the question mark icon above.

If you choose "Scatter Plot", you can interact with the map by clicking the stations or using the box select tool in the menu bar 
to visualize the transect and ranking of the selected data on the right side of the page.
To clear the data you have selected, click the "CLEAR SELECTED DATA" button below.
"""

layer_selection_helper_text = """
**Scatter Plot**

The scatter plot displays all the data points in the dataset on the map according to their isostatic anomaly value. 
It is a direct way to discover all the data points and view the spacial distribution of these points.
The color of each point is defined by the isostatic anomaly value according to the colorscale.

(Tips on usage - You can click on any station on the map to view the transect and the ranking of the gravity anomaly on the right side of the page.
You can also use the "box select" from the menu bar at the top of the map to select a set of stations. 
To toggle show metadata when hovering over the points, you can click the rightmost button from the menu bar.)

**Interpolated Plot**

The interpolated plot connects data points by estimating values within the gaps between stations.
This is done by doing continuous interpolation on the original dataset.
From this plot, you can get a rough idea about the gravity anomaly value of the unsampled areas.

**Spatial Density Heatmap**

The spatial density map shows the spatial distribution of the stations that the datasets are collection from.
You can tell which areas that are sampled more sparsely and the areas that are sampled more densely from this map.
A potential application of this map is to inform viewers which areas should be prioritized for collecting new data.  

**Extra Layer - Quaternary Faults**

The quaternary faults layer displays the fault data referenced from [NSHM 2014 Fault Sources](https://www.usgs.gov/natural-hazards/earthquake-hazards/science/2014-united-states-lower-48-seismic-hazard-long-term?qt-science_center_objects=0#qt-science_center_objects) on the map.
It shows the normal fault, the thrust fault, the strike-slip fault, and some unassigned faults in different colors.
You can make the faults as an extra layer to other visualization types by using the checkbox for "Extra layers".
To learn more about faults, you can visit [USGS's Faults page](https://www.usgs.gov/natural-hazards/earthquake-hazards/faults).

(Tips on usage - If you want to view the faults data without other layers, you can switch to "Scatter Plot" type and click the "Stations" on the legend above the map to toggle the display of the scatter points.
Although you can also click on the legends for the faults, it will not have effects on the map due to framework limitations.)

"""
