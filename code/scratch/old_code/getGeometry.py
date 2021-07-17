import ee
import pandas as pd
import math
import numpy as np
from getLocation import getLocation 

def getGeometry(watershed, gage = np.nan, point_csv = np.nan):

    print('\n \nRunning getGeometry.py')
    if type=='USGS_basin':
        print('From USGS API: Getting watershed geometry and bounding box')
        bounding_box = getLocation(gage)
        sites_fc, bbox_fc =  getLocation(type, output_type, gage=np.nan, shape=np.nan, points=np.nan, plot_map=True):
        print(bounding_box.geometry)
        ee.Geometry.Polygon(bounding_box.geometry)
        # Setup edges for bounding box   
        # min_long = math.floor(lon) + 1
        # max_long = math.floor(lon) - 1
        # min_lat = math.floor(lat) - 1
        # max_lat = math.floor(lat) + 1

        # bounding_box = ee.Geometry.Polygon(
        #         [[[min_long, max_lat],
        #         [min_long, min_lat],
        #         [max_long, min_lat],
        #         [max_long,max_lat]]])

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