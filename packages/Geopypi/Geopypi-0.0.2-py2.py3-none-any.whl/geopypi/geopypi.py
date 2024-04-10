"""Main module."""
import ipyleaflet
from ipyleaflet import basemaps
import ipywidgets as widgets

class Map(ipyleaflet.Map):

    def __init__(self, center= [40, -100], zoom =4, **kwargs):
        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True
        super().__init__(center=center, zoom=zoom, **kwargs)
        
    def add_tile_layer(self, url, name, **kwargs):
        layer = ipyleaflet.TileLayer(url=url, name=name, **kwargs)
        self.add_layer(layer)

    def add_basemap(self, name):
       
        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name) 
        else:
            self.add(name)
            
    def add_image(self, url, bounds, name= 'Image', **kwargs):
        layer = ipyleaflet.ImageOverlay(url=url, bounds=bounds, name=name, **kwargs)
        self.add_layer(layer)

    def add_layers_control(self, position='topright'):
        control = ipyleaflet.LayersControl(position=position)
        self.add_control(control)

    def add_geojson(self, data, name='geojson', **kwargs):
        import json
        if isinstance(data, str):
            with open(data) as f:
                data = json.load(f)
        
        self.add_layer(ipyleaflet.GeoJSON(data=data, name=name, **kwargs))
        
    def add_zoom_slider(self, description = 'Zoom Level:', min=4, max=15, value=10, position='topright'):

        zoom_slider = widgets.IntSlider(description=description, min=min, max=max, value=value)               
        control = ipyleaflet.WidgetControl(widget=zoom_slider, position=position)
        self.add(control)
        widgets.jslink((zoom_slider, 'value'), (self, 'zoom'))