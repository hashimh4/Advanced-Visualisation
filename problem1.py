import panel as pn
import pygmt
import param
import pandas as pd

# Load a panel template
pn.config.template = "fast"

# Import the bounding box data
bounding_boxes = pd.read_csv("country-boundingboxes.csv", encoding="latin1")

# Set the index and create a dictonary with pandas
bounding_boxes.set_index('country', inplace=True)
boxes = bounding_boxes.to_dict(orient='index')

# Define the map regions (West, East, South and North) for the world and each continent
# continents = {
#     "World": [-180, 180, -80, 85],
#     "Europe": [-28, 53, 34, 71],
#     "Asia": [25, 192, -13, 82],
#     "Africa": [-25, 64, -40, 42],
#     "North America": [-173, -19, 0, 82],
#     "South America": [-110, -24, -60, 20],
#     "Oceania": [105, 220, -55, 20],
#     "Antarctica": [-180, 180, -89, -54],
# }

# Define a class using params (to add interactable widgets along with panel)
class EarthDisplacement(param.Parameterized):
    # The dropdown menu to select a continent
    continent = param.Selector(objects=boxes.keys(), default="World", label="Select Continent / Region")

    # Zoom sliders with absolute percentage values
    region_width = param.Number(100, bounds=(0, 100), step=1, label="Zoom x / Region Width (%)")
    region_length = param.Number(100, bounds=(0, 100), step=1, label="Zoom y / Region Length (%)")

    # Pan sliders to change the longitude or latitude
    pan_longitude = param.Number(0, bounds=(-45, 45), step=1, label="Pan Longitude")
    pan_latitude = param.Number(0, bounds=(-45, 45), step=1, label="Pan Latitude")

    # Isoline slider to change the number of isolines for the 2D map, in intervals of 100
    isolines = param.Integer(2000, bounds=(100, 5000), step=100, label="Isoline Density")

    # Dropdown menus for the colourmap and colour bar
    colour_map = param.ObjectSelector(default="geo", objects=["geo", "relief", "viridis", "ocean", "topo", "turbo", "jet"], label="Colour Map")

    # Dropdown menu to change the resolution of the images
    resolution = param.ObjectSelector(default="01d", objects=["01d", "30m", "20m", "15m", "10m", "05m", "02m"], label="Resolution")

    # @param.depends("continent", watch=True)
    # def update_slider_bounds(self):
        # Update slider bounds when the continent changes
        # continent_region = continents[self.continent]

        # default_width = continent_region[1] - continent_region[0]
        # default_length = continent_region[3] - continent_region[2]

        # current_width = (self.region_width / 100) * default_width
        # current_length = (self.region_length / 100) * default_length

        # Reset slider bounds when the continent changes
        # self.param.region_width.bounds = (1, 100)
        # self.param.region_length.bounds = (1, 100)

        # Reset slider bounds when the continent changes
        # self.param.pan_longitude.bounds = (-45, 45)
        # self.param.pan_latitude.bounds = (-45, 45)        

        # Set bounds for pan_longitude and pan_latitude when the continent changes
        # if (default_width - current_width == 0):
        #     self.param.pan_longitude.bounds = (0, 0)
        # else:
        #     self.param.pan_longitude.bounds = (-(default_width - current_width), (default_width - current_width))
    
        # if (default_length - current_length == 0):
        #     self.param.pan_latitude.bounds = (0, 0)
        # else:
        #     self.param.pan_latitude.bounds = (-(default_length - current_length), (default_length - current_length))
    
    # Create a relationship to reset pan values
    @param.depends("continent", watch=True)
    def reset_pan_values(self):
        # Reset the zoom values to 0 when the continent changes
        self.param.set_param(region_width=100)
        self.param.set_param(region_length=100)
        # Reset pan values to 0 when the continent changes
        self.param.set_param(pan_longitude=0) 
        self.param.set_param(pan_latitude=0)

    # Updates the region for the maps depending on the slider values
    def update_region(self):
        # Ensure the region is the map region from previously
        initial_region = boxes[self.continent]
        # Set the initial length and width to the pre-defined region size
        initial_width = initial_region["longmax"] - initial_region["longmin"]
        initial_length = initial_region["latmax"] - initial_region["latmin"]

        # Define the region as the initial region size added to the pan values
        region = [
            initial_region["longmin"] + self.pan_longitude,
            initial_region["longmax"] + self.pan_longitude,
            initial_region["latmin"] + self.pan_latitude,
            initial_region["latmax"] + self.pan_latitude,
        ]

        # Calculate the new width and length based on the region percentages
        width_percentage = (self.region_width) / 100
        length_percentage = (self.region_length) / 100
        region_width = width_percentage * initial_width
        region_length = length_percentage * initial_length

        # Adjust the region to zoom in or out
        region = [
            region[0] + ((initial_width - region_width) / 2),
            region[1] - ((initial_width - region_width) / 2),
            region[2] + ((initial_length - region_length) / 2),
            region[3] - ((initial_length - region_length) / 2),
        ]

        return region

    # Create a relationship to update the 3D perspective map
    @param.depends("continent", "region_width", "region_length", "pan_longitude", "pan_latitude", "isolines", "colour_map", "resolution", watch=True)
    def update_map(self):
        # Create a figure
        fig = pygmt.Figure()

        # Calculate the region
        region = self.update_region()

        # Define the 3D perspective map grid
        # Different reolutions e.g. 01d
        grid = pygmt.datasets.load_earth_relief(resolution=self.resolution, region=region)

        # Add the colourmap for the 3D perspective
        fig.grdview(
            grid=grid,
            perspective=[-130, 30],
            frame=["xaf", "yaf", "WSnE"],
            projection="M15c",
            zsize="1.5c",
            surftype="s",
            cmap=self.colour_map,
            plane="1000+ggrey",
        )

        # Define the colourbar for the map
        fig.colorbar(perspective=True, frame=["a2500", "x+lElevation", "y+lm"])

        # Display the figure
        return fig
    
    # Create a relationship to update the 2D isolines map
    @param.depends("continent", "region_width", "region_length", "pan_longitude", "pan_latitude", "isolines", "colour_map", "resolution", watch=True)
    def update_isolines_map(self):
        # Create a figure
        fig2 = pygmt.Figure()

        # Calculate the region
        region = self.update_region()

        # Different resolutions e.g. 01d
        grid = pygmt.datasets.load_earth_relief(resolution=self.resolution, region=region)

        # fig2.image(imagefile="colour_dataset\8081_earthmap2k.jpg", region=region, projection="R12c", position="jBR+w14c")

        # Add the colourmap for the 2D perspective
        fig2.grdimage(
            grid=grid,
            projection="R12c",
            cmap=self.colour_map,
        )
        
        # Add the isolines for the 2D perspective
        fig2.grdcontour(
            annotation=1000,
            interval=self.isolines,
            grid=grid,
            projection="R12c",
        )

        # Define the colourbar for the map
        fig2.colorbar(frame=["a2500", "x+lElevation", "y+lm"])

        # Display the figure
        return fig2
    
# Variable for the class we created
earth_displacement = EarthDisplacement()

# Define the Panel app and its contents
app = pn.Column(
    # Display the header
    "## Greenpeace Scientific Visualisation",
    pn.Spacer(height=20),

    # Display all widgets
    pn.Row(
        pn.Param(
            earth_displacement.param,
            widgets={
                "continent": {"widget_type": pn.widgets.Select, "width": 175},
                "region_width": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "region_length": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "pan_longitude": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "pan_latitude": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "isolines": {"widget_type": pn.widgets.IntSlider, "width": 175},
                "colour_map": {"widget_type": pn.widgets.Select, "width": 175},
                "resolution": {"widget_type": pn.widgets.Select, "width": 175},
            },
        ),

        # Constantly update the 3D map
        earth_displacement.update_map,

        # Constantly update the 2D map
        pn.panel(earth_displacement.update_isolines_map, sizing_mode="fixed", height=260, width=389),
    ),
)

# Check for when the continent changes to then reset the pan values
earth_displacement.param.watch(earth_displacement.reset_pan_values, "continent")

# Run the app
pn.serve(app, show=True)