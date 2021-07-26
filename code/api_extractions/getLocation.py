import geopandas as gpd
import pandas as pd
import numpy as np
import datetime
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.geometry import box
import contextily as ctx
import urllib
import os
import json
import ee
import sys
import warnings
warnings.filterwarnings("ignore")

ee.Initialize()

def main():
    # states = ee.FeatureCollection("TIGER/2016/States").getInfo()
    # df = pd.json_normalize(states['features'])
    # print(df.columns)
    # # df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
    # print(df.columns)
    ca = gpd.read_file('data/ca-state-boundary/CA_State_TIGER2016.shp')

    locs= pd.read_csv('data/coordinates.csv')

    getLocation(input_type='USGS_basin', output_type='gpd', gage=11465350, output_directory = 'test', sub_directory = 'sub')
    #getLocation(input_type='points', output_type='ee', points = locs, gage='points')
    #getLocation(input_type='polygon', output_type='ee', shape=ca, gage='ca', plot_map=False)


def getLocation(input_type, output_type, gage=np.nan, shape=np.nan, points=np.nan, plot_map=True, output_directory = np.nan, sub_directory = np.nan):
    
    if input_type=='USGS_basin':
        #Importing basin geometery 
        #url = 'https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/basin?f=json'%gage
        #print(url)
        sites = gpd.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/basin?f=json'%gage)    
        # defining URL to access json 
        request = urllib.request.urlopen("https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/?f=json"%gage)
        #Extracting gage site name from USGS website 
        site_name = [json.load(request)['features'][0]['properties']['name'].title()]
        # Importing flow line geometry 
        flowlines=gpd.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/navigation/UM/flowlines?f=json&distance=1000'%gage)
<<<<<<< HEAD
        print('\n USGS Basin imported at ' + site_name[0] + 'CRS: ' + str(sites.crs))
        sites.to_file(os.path.join(output_directory, sub_directory, "exports","sites_USGS_"+str(gage)+".geojson"), driver="GeoJSON")
=======
        print('\n\tUSGS basin imported at ' + site_name[0] + 'CRS: ' + str(sites.crs))
        sites.to_file(output_directory + sub_directory + "/exports/sites_USGS_"+str(gage)+".geojson", driver="GeoJSON")
>>>>>>> remotes/erica/main

    elif input_type=='points':
        #import points and transform into geopandas
        print('points are being read as geolocations in epsg: 4326')
        locs = pd.read_csv(str(points))
        site_name = locs['Site Name']
        sites = gpd.GeoDataFrame(locs, geometry=gpd.points_from_xy(locs.Long, locs.Lat))
        sites = sites.set_crs('epsg:4326')
        sites.to_file(os.path.join(output_directory, sub_directory, 'exports','points.geojson'), driver="GeoJSON")
        
    
    elif input_type=='polygon':
        # import polygon
        sites = shape
        sites = sites.to_crs('epsg:4326')
        sites.to_file(os.path.join(output_directory, sub_directory,"exports","polygon_site.geojson"), driver="GeoJSON")
        site_name = ['polygon']

    else:
        print('only types USGS_basin, points, and polygon are supported')
        sys.exit()
    
    # getting bounding box with 0.05 degree buffer around basin shape
    bbox_gdf = gpd.GeoDataFrame([1], geometry=[box(*sites.buffer(0.05).total_bounds)], crs=sites.crs)
    
    #plotting basin on basemap
    if plot_map:
        if input_type=='points': loc_plot = sites.to_crs(epsg=3857).plot(color='darkgreen', figsize=(8, 8), label='Points')
        else: loc_plot = sites.to_crs(epsg=3857).boundary.plot(color='darkgreen', figsize=(8, 8), label='Site Area')
        if input_type=='USGS_basin': flowlines.to_crs(epsg=3857).plot(ax=loc_plot, label='Flow Lines')
        bbox_gdf.to_crs(epsg=3857).boundary.plot(ax=loc_plot, color='black', label='Bounding Box')
        ctx.add_basemap(ax=loc_plot)
        plt.legend()
        if input_type=='USGS_basin': plt.title('USGS Gage at: '+site_name[0])
        plt.savefig(os.path.join(output_directory, sub_directory,'figs','extent_'+str(gage)+'.png'))

    #returning bounding box geometry as geopandas dataframe or ee feature collection
    if output_type=='gpd': return sites, bbox_gdf, site_name
    elif output_type=='ee': 
        # if want outputs as ee feature collections - this section will run
        bbox_coords = [item for item in bbox_gdf.geometry[0].exterior.coords]
        bbox_geom = ee.Geometry.Polygon(bbox_coords)
        # creating a gee feature from points
        if input_type=='points': 
            coordinates = locs[['Long', 'Lat']].values.tolist()
            sites_features = []
            # Below gets a feature collection from sites, Erica modified to return a list of features
            for i in range(len(coordinates)):
                temp = ee.Feature(ee.Geometry.Point(coords=coordinates[i]), {'Name': locs['Site Name'][i]})
                sites_features.append(temp)
            #sites_fc = sites_fl # Erica modified and commented out next line so as to return a list of features instead of a collection
            #sites_fc = ee.FeatureCollection(sites_fl)
        elif input_type == 'USGS_basin':
            poly_coords = [item for item in sites.geometry[0].exterior.coords]
<<<<<<< HEAD
            sites_features = ee.Geometry.Polygon(coords=poly_coords)
            #sites_features = ee.FeatureCollection([temp])
            #gee_feat = gee_feat.set('Site',1)
=======
            temp = ee.Feature(ee.Geometry.Polygon(coords=poly_coords), {'Name': str(site_name[0]), 'Gage':int(gage)})
            sites_fc = ee.FeatureCollection([temp])
            #gee_feat = gee_feat.set('Site',1s)
>>>>>>> remotes/erica/main
            #fts_list = [gee_feat]
            #fts = ee.FeatureCollection(fts_list)

        else: 
            # This allows for multipart polygons i.e. california, 
            # but they currnetly behave as their own features, 
            # which is not right... This needs fixing. 
            print(sites['NAME'])
            sites = sites.explode()
            sites_features = []
            for i in sites.geometry:
                poly_coords = list(i.exterior.coords)
                temp = ee.Feature(ee.Geometry.Polygon(coords=poly_coords))
                sites_features.append(temp)
            # sites_fc=ee.FeatureCollection(sites_f)
            # sites_fc.set('Name','CA')
        return sites_features, bbox_geom, site_name
    else: print('not a valid output type, select gpd or ee')


if __name__ == "__main__":
    main()