import geopandas as gp
import pandas as pd
import datetime
import matplotlib.pyplot as plt
from shapely.geometry import Polygon
from shapely.geometry import box
import contextily as ctx
import urllib
import json
import ee
ee.Initialize()

def main():
    getBasin(11465350)


def getBasin(gage,  plot_map=True):
    #Importing basin geometery 
    basin = gp.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/basin?f=json'%gage)    
    # defining URL to access json 
    request = urllib.request.urlopen("https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/?f=json"%gage)
    #Extracting gage site name from USGS website 
    site_name = json.load(request)['features'][0]['properties']['name'].title()
    # Importing flow line geometry 
    flowlines=gp.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/navigation/UM/flowlines?f=json&distance=1000'%gage)
    print('\n running getBasin function from getFlow.py for ' + site_name)
    
    #outputting basin shapefile
    basin.to_file("exports/basin_"+str(gage)+".geojson", driver="GeoJSON")

    # getting bounding box with 0.05 degree buffer around basin shape
    bbox_gdf = gp.GeoDataFrame([1], geometry=[box(*basin.buffer(0.05).total_bounds)], crs=basin.crs)

    #plotting basin on basemap
    if plot_map:
        basin_plot = basin.to_crs(epsg=3857).boundary.plot(color='darkgreen', figsize=(8, 8), label='Basin')
        flowlines.to_crs(epsg=3857).plot(ax=basin_plot, label='Flow Lines')
        bbox_gdf.to_crs(epsg=3857).boundary.plot(ax=basin_plot, color='black', label='Bounding Box')
        ctx.add_basemap(ax=basin_plot)
        plt.legend()
        plt.title('USGS Gage at: '+site_name)
        plt.savefig('figs/extent_'+str(gage)+'.png')

    # returning bounding box geometry as geopandas dataframe 
    return bbox_gdf


def getFlow(gage, start = '1988-01-01', stop = '2020-01-01'):
    print('\n running getFlow function from getFlow.py')
    site = str(gage)
    basin = gp.read_file('https://labs.waterdata.usgs.gov/api/nldi/linked-data/nwissite/USGS-%s/basin?f=json'%gage)

    # url of flow data (usgs)
    url = 'https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no=' + site + '&referred_module=sw&period=&begin_date='+start+'&end_date='+stop
    # get df
    df = pd.read_csv(url, header=31, delim_whitespace=True)
    df.columns = ['usgs', 'site_number', 'datetime', 'q_cfs', 'a'] 
    df['id'] = pd.to_datetime(df.datetime)
    df = df[['q_cfs','id']]
    df['q_cfs'] = df['q_cfs'].astype(float, errors='ignore')  #this is needed because sometimes there are non-numeric entries and we want to ignore them
    df['q_m3day']= (86400*df['q_cfs'])/(35.31) #m3/day
    # Calculate drainage area in m^2
    drainage_area_m2=basin.to_crs('epsg:26910').geometry.area 

    df['q_m'] = df['q_m3day'] / float(drainage_area_m2)
    df['q_mm'] = df['q_m3day'] / float(drainage_area_m2) * 1000

    df.set_index('id',inplace=True) 

    return df

    #bbox = bounds.total_bounds

    # coords = [item for item in basin.geometry[0].exterior.coords]
    # gee_feat = ee.Feature(ee.Geometry.Polygon(coords))
    # gee_feat = gee_feat.set('Site',1)
    # fts_list = [gee_feat]
    # fts = ee.FeatureCollection(fts_list)
    # print(fts)

    # site_lat = basin.to_crs('epsg:4326').geometry[0].centroid.y
    # site_long = basin.to_crs('epsg:4326').geometry[0].centroid.x




if __name__ == "__main__":
    main()