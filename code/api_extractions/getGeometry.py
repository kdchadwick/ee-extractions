 
import ee
import pandas as pd
import math
from getFlow import getBasin
 

def getGeometry(watershed, gage = 11134800, point_csv = 'data/coordinates.csv'):

    print('\n \nRunning getGeometry.py')
    if watershed == True:
        print('From USGS API: Getting watershed geometry and bounding box')
        basin, pts, lat, lon = getBasin(gage)

        # Setup edges for bounding box   
        min_long = math.floor(lon) + 1
        max_long = math.floor(lon) - 1
        min_lat = math.floor(lat) - 1
        max_lat = math.floor(lat) + 1

        bounding_box = ee.Geometry.Polygon(
                [[[min_long, max_lat],
                [min_long, min_lat],
                [max_long, min_lat],
                [max_long,max_lat]]])

        names = []
        
    
    else:
        print('Getting all lat/longs geometries from points list and define bounding box')
        locs = pd.read_csv('data/coordinates.csv')
        coordinates = locs[['Long', 'Lat']].values.tolist()
        names = locs['Site Name']

        pts = []
        for i in range(len(coordinates)):
            temp = ee.Feature(ee.Geometry.Point(coords=coordinates[i]))
            pts.append(temp)

        bounding_box = ee.Geometry.Polygon(
                [[[math.floor(min(locs['Long'])), math.ceil(max(locs['Lat']))],
                [math.floor(min(locs['Long'])), math.floor(min(locs['Lat']))],
                [math.ceil(max(locs['Long'])), math.floor(min(locs['Lat']))],
                [math.ceil(max(locs['Long'])), math.ceil(max(locs['Lat']))]]])

        
    return pts, bounding_box, names
