intro_text = """
**Introduction**

This application is an interactive geospatial data visualization tool for you to discover the gravity anomaly data in California and Nevada.

Gravity is not the same everywhere on Earth, but changes with many known and measurable factors, such as tidal forces. 
A sequence of gravity corrections are applied to the original gravity reading and result in various named gravity anomalies. 
There are mainly four kinds of gravity anomalies: observed gravity anomaly, free air gravity anomaly, Bouguer gravity anomaly, and isostatic gravity anomaly. 
You can learn more about gravity anomalies from [USGS's publication here](https://pubs.usgs.gov/fs/fs-0239-95/fs-0239-95.pdf).

In this application, you can select different types of visualizations to explore the distribution of isostatic anomaly values and the metadata from the stations.
In addition, you can interact with the map to view the transect or the distribution of the data according to the instructions in each section.

Data sources: [National Centers for Environmental Information](https://www.ncei.noaa.gov/), [California’s Open Data website](https://data.ca.gov/), 
[U.S. General Services Administration](https://www.gsa.gov/), [USGS Mineral Resources Online Spatial Data](https://mrdata.usgs.gov/)

"""

transect_intro_text = """
This line chart shows how gravity and elevation vary along a line. 

You can click on any point on the scatter map, then it will show up as a point on the right in this chart.
"""

task4_intro_text = """
This bar chart shows how the gravity of one station compares to other stations that you've selected.

You can click on any point on the scatter map, or use the box select tool in the menu bar to select data to be visualized.
"""

task4_helper_text = """
If you wish to select each station individually, you can click on any point on the scatter map to highlight it in the graph below.
All the stations are sorted in descending order, and the point you've just selected is highlighted in red.

If you wish to select multiple stations at a time, you can use the box select tool in the menu bar and use your mouse to draw a rectangle on the scatter map.
All the stations are sorted in descending order.
"""

layer_selection_intro_text = """
You can select any of the four types of visualizations. To learn more about these visualization types, click the question mark icon above.

If you choose "Scatter Plot", you can click on any station on the map to view the transect and the distribution of the gravity anomaly on the right side of the page.
You can also use the box select tool in the menu bar and switch the type to "Use the box select tool" to select multiple points at a time for the "Distribution and ranking" graph.

To clear the data you have selected, click the "CLEAR SELECTED DATA" button below.
"""

help_text = """
**Scatter Plot**

The scatter plot displays all the data points in the dataset on the map according to their isostatic anomaly value. 
It is a direct way to discover all the data points and view the spacial distribution of these points.
The color of each point is defined by the isostatic anomaly value according to the colorscale.

You can click on any station on the map to view the transect and the ranking of the gravity anomaly on the right side of the page.
You can also use the "box select" from the menubar at the top of the map to select a set of stations.

---

**Density Heatmap**

In the density map, each data point in the dataset is represented as a point smoothed with a given radius of influence.
It shows the patial distribution of the stations that the datasets are collection from.
You can tell which areas that are sampled more sparsely vs. the areas that are sampled more densely from this map.
A potential application of this map is to inform viewers which areas should be prioritized for collecting new data.  

---

**Interpolated Plot**


The interpolated plot connects data points by estimating values within the gaps between stations.
This is done by doing continuous interpolation on the original dataset.
From this plot, you can get a rough idea about the gravity anomaly value of the unsampled areas.

---

**Fault Dataset**


The fault dataset layer displays the fault data on the map without any other layers. 
If you choose this type as the base layer, the extra layer of fault dataset will have no effects.

"""
