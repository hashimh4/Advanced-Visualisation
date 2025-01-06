import panel as pn
import pygmt
import param

# Load a panel template
pn.config.template = "fast"

# Define the map regions (West, East, South and North) for the world and each continent
continents = {
    "Europe": [-28, 53, 34, 71],
    "Asia": [25, 192, -13, 82],
    "Africa": [-25, 64, -40, 42],
    "North America": [-173, -19, 0, 82],
    "South America": [-110, -24, -60, 20],
    "Oceania": [105, 220, -55, 20],
}

# Define a class using params (to add interactable widgets along with panel)
class EarthDisplacement(param.Parameterized):
    # The dropdown menu to select a continent
    continent = param.Selector(objects=continents.keys(), default="Europe", label="Select Continent")

    # Pan sliders to change the longitude or latitude
    pan_longitude = param.Number(0, bounds=(-180, 180), step=45, label="Pan Longitude")
    pan_latitude = param.Number(0, bounds=(-90, 90), step=45, label="Pan Latitude")

    # Isoline slider to change the number of isolines for the 2D map, in intervals of 100
    isolines = param.Integer(2400, bounds=(100, 5000), step=200, label="Isoline Density")

    # Dropdown menus for the colour map and colour bar
    colour_map = param.ObjectSelector(default="geo", objects=["geo", "viridis", "ocean"], label="Colour Map")

    # Text sections for the two maps
    text_3D = pn.pane.Markdown(width=400)
    text_2D = pn.pane.Markdown(width=400)

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
    # Updates the region for the maps depending on the slider values
    def update_region(self):
        # Ensure the region is the map region from previously
        initial_region = [-180, 180, -80, 85]
        region = [
            initial_region[0] + self.pan_longitude,
            initial_region[1] + self.pan_longitude,
            initial_region[2] + self.pan_latitude,
            initial_region[3] + self.pan_latitude,
        ]
        return region

    # Create a relationship to update the 2D isolines map
    @param.depends("pan_longitude", "pan_latitude", "isolines", "colour_map", watch=True)
    def update_globe(self):
        # Create a figure
        fig = pygmt.Figure()

        # Update the region based on the selected longitude and latitude 
        region = [-180, 180, -90, 90]

        # Ensure the second set of data is loaded if the ocean colourmap is selected
        if self.colour_map == "ocean":
            grid = pygmt.datasets.load_earth_geoid(resolution="01d", region=region)
        else:
            grid = pygmt.datasets.load_earth_relief(resolution="01d", region=region)

        # Add the colourmap for the globe perspective
        fig.grdimage(
            grid=grid,
            projection=f"G{self.pan_longitude}/{self.pan_latitude}/12c",
            cmap=self.colour_map,
        )
        
        # Add the isolines for the globe perspective
        fig.grdcontour(
            annotation=1000,
            interval=self.isolines,
            grid=grid,
            projection=f"G{self.pan_longitude}/{self.pan_latitude}/12c",
        )

        # Add text annotations for each continent
        for continent, coords in continents.items():
            lon, lat = (coords[0] + coords[1]) / 2, (coords[2] + coords[3]) / 2
            # Define the text and its positions
            fig.text(
                x=lon,
                y=lat,
                text=continent,
                justify="CM",
                offset="0p/5p",
                font="20p,Helvetica-Bold,white",
            )

        # Text to display if "geo" is chosen
        if self.colour_map == "geo":
            self.text_3D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Causes of Climate Change</h3>

            <p>"Climate change can be a natural process where temperature, rainfall, wind, and other elements vary over decades or more. 
            In millions of years, our world has been warmer and colder than it is now. But today we are experiencing unprecedented rapid warming 
            from human activities, primarily due to burning fossil fuels that generate greenhouse gas emissions."</p>

            <h3>Burning Fossil Fuels</h3>
            <p>"Fossil fuels such as oil, gas, and coal contain carbon dioxide that has been 'locked away' in the ground for thousands of years. 
            When we take these out of the land and burn them, we release the stored carbon dioxide into the air."</p>

            <h3>Deforestation</h3>
            <p>"Forests remove and store carbon dioxide from the atmosphere. Cutting them down means that carbon dioxide builds up quicker since 
            there are no trees to absorb it. Not only that, trees release the carbon they stored when we burn them."</p>

            <h3>Agriculture</h3>
            <p>"Planting crops and rearing animals release many different types of greenhouse gases into the air. For example, animals produce methane, 
            which is 30 times more powerful than carbon dioxide as a greenhouse gas. The nitrous oxide used for fertilizers is ten times worse and is 
            nearly 300 times more potent than carbon dioxide!"</p>

            <h3>Cement</h3>
            <p>"Producing cement is another contributor to climate change, causing 2 percent of our entire carbon dioxide emissions."</p>

            <h3>References</h3>
            <p>"Causes of climate change. Met Office. Available at: "<a href="https://www.metoffice.gov.uk/weather/climate-change/causes-of-climate-change">
            Causes of climate change - Met Office</a></p>
            <p>"Causes of climate change. Met Office. Available at: "<a href="https://www.metoffice.gov.uk/weather/climate-change/causes-of-climate-change">
            Causes of climate change - Met Office</a></p>
            """
        
        # Text to display if "viridis" is chosen
        if self.colour_map == "viridis":

            self.text_3D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Causes of Climate Change [COLOURBLIND FRIENDLY MAP]</h3>
            <p>"Climate change can be a natural process where temperature, rainfall, wind, and other elements vary over decades or more. 
            In millions of years, our world has been warmer and colder than it is now. But today we are experiencing unprecedented rapid warming 
            from human activities, primarily due to burning fossil fuels that generate greenhouse gas emissions."</p>

            <h3>Burning Fossil Fuels</h3>
            <p>"Fossil fuels such as oil, gas, and coal contain carbon dioxide that has been 'locked away' in the ground for thousands of years. 
            When we take these out of the land and burn them, we release the stored carbon dioxide into the air."</p>

            <h3>Deforestation</h3>
            <p>"Forests remove and store carbon dioxide from the atmosphere. Cutting them down means that carbon dioxide builds up quicker since 
            there are no trees to absorb it. Not only that, trees release the carbon they stored when we burn them."</p>

            <h3>Agriculture</h3>
            <p>"Planting crops and rearing animals release many different types of greenhouse gases into the air. For example, animals produce methane, 
            which is 30 times more powerful than carbon dioxide as a greenhouse gas. The nitrous oxide used for fertilizers is ten times worse and is 
            nearly 300 times more potent than carbon dioxide!"</p>

            <h3>Cement</h3>
            <p>"Producing cement is another contributor to climate change, causing 2 percent of our entire carbon dioxide emissions."</p>

            <h3>References</h3>
            <p>"Causes of climate change. Met Office. Available at: "<a href="https://www.metoffice.gov.uk/weather/climate-change/causes-of-climate-change">
            Causes of climate change - Met Office</a></p>
            <p>"Causes of climate change. Met Office. Available at: "<a href="https://www.metoffice.gov.uk/weather/climate-change/causes-of-climate-change">
            Causes of climate change - Met Office</a></p>
            """

        # Text to display if "ocean" is chosen
        if self.colour_map == "ocean":
            self.text_3D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Effects of Climate Change - Ocean Related Data</h3>
            <h3>Sea Level Rise</h3>
            <p>"Sea-level rise has accelerated in recent decades due to increasing ice loss in the world’s polar regions. 
            Latest data from the World Meteorological Organization shows that global mean sea-level reached a new record high in 2021, 
            rising an average of 4.5 millimeters per year over the period 2013 to 2021."</p>

            <h3>Marine Heatwaves</h3>
            <p>"Marine heatwaves have doubled in frequency, and have become longer-lasting, more intense and extensive. 
            The IPCC says that human influence has been the main driver of the ocean heat increase observed since the 1970s. 
            The majority of heatwaves took place between 2006 and 2015, causing widespread coral bleaching and reef degradation."</p>

            <h3>Loss of Marine Biodiversity</h3>
            <p>"At a 1.1°C increase in temperature today, an estimated 60 percent of the world's marine ecosystems have already been degraded 
            or are being used unsustainably. A warming of 1.5°C threatens to destroy 70 to 90 percent of coral reefs, 
            and a 2°C increase means a nearly 100 percent loss - a point of no return."</p>

            <h3>References</h3>
            <p>"Climate Change. United Nations. Available at: "<a href="https://www.un.org/en/climatechange">Climate Change - United Nations</a></p>
            """
        
        # Define the colourbar for the map
        fig.colorbar(frame=["a2500", "x+lElevation", "y+lm"])

        # Display the figure
        return pn.Column(fig, self.text_3D)
    
    # Create a relationship to update the 2D isolines map
    @param.depends("continent", "isolines", "colour_map", watch=True)
    def update_isolines_map(self):
        # Create a figure
        fig2 = pygmt.Figure()

        # Adjust the region based on the continent selected
        region = continents[self.continent]

        # Different resolutions e.g. 01d
        grid = pygmt.datasets.load_earth_relief(resolution="01d", region=region)

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

        # fig2.colorbar(frame=["a2500", "x+lElevation", "y+lm"])

        # Text to display if "Europe" is chosen
        if self.continent == "Europe":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from Europe</h3>

            <p>"With the European Climate Law, the EU made climate neutrality by 2050 a legally binding goal, set an interim target of a net 55 
            percent emission reduction by 2030, and is working on setting the 2040 target. The Fit for 55 proposal aims to bring EU legislation 
            in line with the 2030 goal."</p>

            <h3>References</h3>
            <p>"Climate Change Mitigation: Reducing Emissions. European Environment. Available at: 
            "<a href="https://www.eea.europa.eu/en/topics/in-depth/climate-change-mitigation-reducing-emissions">
            Climate Change Mitigation: Reducing Emissions - European Environment</a></p>
            """
        
        # Text to display if "North America" is chosen
        if self.continent == "North America":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from North America</h3>

            <p>"Reducing U.S. greenhouse gas emissions 50-52 percent below 2005 levels in 2030. Reaching 100 percent carbon pollution-free electricity 
            by 2035. Achieving a net-zero emissions economy by 2050. Delivering 40 percent of the benefits from federal investments in climate and 
            clean energy to disadvantaged communities."</p>

            <h3>References</h3>
            <p>"National Climate Task Force. The White House. Available at: 
            "<a href="https://www.whitehouse.gov/climate">
            President Biden’s Actions to Tackle the Climate Crisis</a></p>
            """
        
        # Text to display if "Africa" is chosen
        if self.continent == "Africa":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from Africa</h3>

            <p>"A solution to the crisis comes in the form of green bonds. This wholesale finance is based on fundraising for environmentally friendly 
            projects, such as renewable energies or clean transport. Most of Africa's green bonds have been issued by the AfDB, which has raised more 
            than $1.5bn since 2013."</p>

            <h3>References</h3>
            <p>"Climate Change Injustice. African Business. Available at: 
            "<a href="https://african.business/2023/10/resources/the-injustice-of-climate-change-what-solutions-for-africa">
            The injustice of climate change: What solutions for Africa?</a></p>
            """
        
        # Text to display if "Oceania" is chosen
        if self.continent == "Oceania":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from Oceania</h3>

            <p>"In 2019, New Zealand passed the Climate Change Response (Zero Carbon) Amendment Act, setting the targets of reducing net emissions of greenhouse 
            gases (other than biogenic methane) to zero by 2050, as well as to reduce biogenic emissions to 10 percent below 2017 levels by 2030, and to 24-27 
            percent by 2050."</p>

            <h3>References</h3>
            <p>"About Partners. Climate and Clean Air Coalition. Available at: 
            "<a href="https://www.ccacoalition.org/partners/new-zealand">
            New Zealand - CCAC Partner</a></p>
            """
        
        # Text to display if "Asia" is chosen
        if self.continent == "Asia":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from Asia</h3>

            <p>"As an extremely biodiverse region, Southeast Asia has the potential to sequester carbon and create carbon credits through nature-based climate 
            solutions such as restoring forests and wetlands, regenerative farming, and harnessing the region's abundant clean energy."</p>

            <h3>References</h3>
            <p>"Solving Climate Change (Finance). Imperial College Business School. Available at: 
            "<a href="https://www.imperial.ac.uk/business-school/ib-knowledge/finance/solving-climate-change-unleashing-the-potential-southeast-asia">
            Solving climate change: unleashing the potential of Southeast Asia</a></p>
            """   

        # Text to display if "South America" is chosen
        if self.continent == "South America":
            self.text_2D.object = """
            <style>
                body {
                    margin: 5px;
                    font-size: 10px;
                }
                h3 {
                    margin-bottom: 2px;
                }
                p {
                    margin-bottom: 5px;
                }
            </style>

            <h3>Solution from Asia</h3>

            <p>"Among the best-known adaptation measures are building safer, sustainable, and resilient infrastructures, conserving and restoring forests and natural 
            ecosystems, implementing nature-based solutions, managing disaster risks, and diversifying crops."</p>

            <h3>References</h3>
            <p>"Latin American Solutions. CAF. Available at: 
            "<a href="https://www.caf.com/en/currently/news/2023/11/3-latin-american-solutions-against-climate-change/">
            3 Latin American Solutions Against Climate Change</a></p>
            """  

        # Display the figure
        return pn.Column(fig2, self.text_2D)
    
# Variable for the class we created
earth_displacement = EarthDisplacement()

# tabs = pn.Tabs(("Global View", earth_displacement.update_globe), 
#                ("Regional View", pn.panel(earth_displacement.update_isolines_map, sizing_mode="stretch_both")))

# Define the Panel app and its contents
app = pn.Column(
    # Define the header
    "## Greenpeace Public Interactive Visualisation",
    pn.Spacer(height=20),
    pn.Row(

        # Display all the widgets
        pn.Param(
            earth_displacement.param,
            widgets={
                "continent": {"widget_type": pn.widgets.Select, "width": 175},
                "pan_longitude": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "pan_latitude": {"widget_type": pn.widgets.FloatSlider, "width": 175},
                "isolines": {"widget_type": pn.widgets.IntSlider, "width": 175},
                "colour_map": {"widget_type": pn.widgets.Select, "width": 175},
            },
        ),

    # Constantly update the globe
    earth_displacement.update_globe,
    # Ensure the isolines map is sized correctly and update it
    pn.panel(earth_displacement.update_isolines_map, sizing_mode="fixed", height=260, width=389)),
)

# Run the app
pn.serve(app, show=True)