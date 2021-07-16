import geopandas as gp
import pandas as pd
import datetime
import ee
ee.Initialize()

#### PREVIOUSLY getBASIN ####

## Could merge this with the watershed portion of getGeometry...
# Would want to think about how things would need to change for a list of watersheds
# Maybe this could be the function for a single geometry given a gage and the 'getGeometry' is for a list of things, either points or watersheds?
# Note that the getGeometry uses this code
def usgs_basin_geometry(gage):
    #print('\n running getBasin function from getFlow.py')
    basin = gp.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/basin?f=json'%gage)
    flowlines=gp.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/navigation/UM/flowlines?f=json&distance=1000'%gage)
    coords = [item for item in basin.geometry[0].exterior.coords]
    gee_feat = ee.Feature(ee.Geometry.Polygon(coords))
    gee_feat = gee_feat.set('Site',1)
    fts_list = [gee_feat]
    fts = ee.FeatureCollection(fts_list)

    site_lat = basin.to_crs('epsg:4326').geometry[0].centroid.y
    site_long = basin.to_crs('epsg:4326').geometry[0].centroid.x

    return basin, fts, site_lat, site_long