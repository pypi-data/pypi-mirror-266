"""Main module."""

import ipyleaflet

class Map(ipyleaflet.Map):
    """
    This is the map class that inherits from ipyleaflet.Map.

    Args:
        ipyleaflet.Map (Map): The ipyleaflet.Map class.
    """
    def __init__(self, center=[20,0], zoom=2, **kwargs):
        """
        Initialize the map.

        Args:
            center (list): Set the center of the map. Defaults to [20, 0].
            zoom (int): Set the zoom level of the map. Defaults to 2.

        """
        super().__init__(center=center, zoom=zoom, **kwargs) 
        self.add_control(ipyleaflet.LayersControl())

def add_basemap(self, name):
        """
        Adds a basemap to the current map.

        Args:
            name (str or object): The name of the basemap as a string, or an object representing the basemap.

        Raises:
            TypeError: If the name is neither a string nor an object representing a basemap.

        Returns:
            None
        """

        if isinstance(name, str):
            url = eval(f"basemaps.{name}").build_url()
            self.add_tile_layer(url, name)
        else:
            self.add(name)

            
def add_geojson(self, data, name="geojson", **kwargs):
        """Adds a GeoJSON layer to the map.

        Args:
            data (str | dict): The GeoJSON data as a string or a dictionary.
            name (str, optional): The name of the layer. Defaults to "geojson".
        """
        import json

        if isinstance(data, str):
            with open(data) as f:
                data = json.load(f)

        if "style" not in kwargs:
            kwargs["style"] = {"color": "blue", "weight": 1, "fillOpacity": 0}

        if "hover_style" not in kwargs:
            kwargs["hover_style"] = {"fillColor": "#ff0000", "fillOpacity": 0.5}

        layer = ipyleaflet.GeoJSON(data=data, name=name, **kwargs)
        self.add(layer)


def add_shp(self, data, name='shp', **kwargs):
    """Adds a shapefile to the map 

    Args:
        data (str or dict): The path to the map
        name (str, optional): The name of the shapefile. Defaults to 'shp'.
    """
    import shapefile
    import json

    if isinstance(data, str):
        with shapefile.Reader(data) as shp:
            data = shp.__geo_interface__

    self.add_geojson(data, name, **kwargs)

def add_vector(self, data, name="Vector", **kwargs):
    """Adds a vector layer to the map from any GeoPandas-supported vector data format.

    Args:
        data (str, dict, or geopandas.GeoDataFrame): The vector data. It can be a path to a file (GeoJSON, shapefile), a GeoJSON dict, or a GeoDataFrame.
        name (str, optional): The name of the layer. Defaults to "Vector".
    """
    import geopandas as gpd
    import json

    if isinstance(data, gpd.GeoDataFrame):
        geojson_data = json.loads(data.to_json())
    elif isinstance(data, (str, dict)):
        if isinstance(data, str):
            data = gpd.read_file(data)
            geojson_data = json.loads(data.to_json())
        else:  
            geojson_data = data
    else:
        raise ValueError("Unsupported data format")

    self.add_geojson(geojson_data, name, **kwargs)
