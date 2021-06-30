
import ee
import datetime
import pandas as pd
import geopandas as gp
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image
import extraction_export
import get_data_df
from getFlow import getFlow
from getFlow import getBasin

#ee.Authenticate()
ee.Initialize()

gage = 11134800
start = '1988-09-30'
stop = '2019-11-01'
beginning = 2003
end = 2003



def main():

    basin, fts, lat, lon = getBasin(gage)
    flow = getFlow(gage, basin, start, stop)


 #   locs = pd.read_csv('data/coordinates.csv')
 #   coordinates = locs[['Long', 'Lat']].values.tolist()
 #   names = locs['Site Name']
    assets = pd.read_csv('data/layers_short.csv')
    assets['scale'] = assets['scale'].astype('float')

 #   pts = []
 #   for i in range(len(coordinates)):
 #       temp = ee.Feature(ee.Geometry.Point(coords=coordinates[i]))
 #       pts.append(temp)
   
    min_long = math.floor(lon) + 1
    max_long = math.floor(lon) - 1
    min_lat = math.floor(lat) - 1
    max_lat = math.floor(lat) + 1

    #print(lon, min_long, max_long)
    #print(lat, min_lat, max_lat)

    bounding_box = ee.Geometry.Polygon(
            [[[min_long, max_lat],
              [min_long, min_lat],
              [max_long, min_lat],
              [max_long,max_lat]]])

 #   extraction_export(assets, bounding_box, pts, names, 'exports/test.csv', 2003, 2004)



#def extraction_export(assets, pts, names, outputfile, start, end):


    all_points = pd.DataFrame()

  # for i in range(len(pts)):
  #   print('Getting data for point={}'.format(i))
  #   temp_point = pd.DataFrame({'id':pd.date_range(str(start)+"-01-01", str(end)+"-01-01"), 'point': names[i]})

    for d in range(len(assets['gee_path'])):
      path = assets['gee_path'][d]
      collection_short_name=assets['name'][d]+"_"

      def extract(image):
      # pt = pts[i]
        s = assets['scale'][d]
      # ft = ee.Feature(pt.geometry())
        reduced = image.reduceRegion(geometry=fts,
                                    reducer=ee.Reducer.mean(),
                                    scale=s)
        fts_reduced = fts.set(reduced)
        return fts_reduced

      print('Extracting data from asset {}'.format(path))
      annual_temp=pd.DataFrame()
      for year in range(beginning, end):
        print('year {}'.format(year))
        yearstart = str(year)
        yearend = str(year+1)
        testextract = ee.ImageCollection(path).filterDate(yearstart, yearend).filterBounds(bounding_box).map(extract).getInfo()
        
        #test = get_data_df(testextract, dateformat=assets['date_format'][d], collection_short_name=collection_short_name)
        d = testextract
        df = pd.json_normalize(d['features'])

        df.to_csv('test_watershed.csv', mode='a', header=False)
        #print(df.head())
        #df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
        #df['id'] = pd.to_datetime(df['id'].values, format=dateformat)
        #df = df.set_index('id')
        #oldnames = df.columns[df.columns.str.contains('properties')]
        #df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))
        #annual_temp = annual_temp.append(test)
      #temp_point = pd.merge(temp_point, annual_temp, how='left', on=['id'])

      #print(temp_point.head())

    #all_points = all_points.append(temp_point)

    #all_points.to_csv(outputfile, mode='a', header=False)


"""
  def get_data_df(d, dateformat, collection_short_name):
    df = pd.json_normalize(d['features'])
    df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
    df['id'] = pd.to_datetime(df['id'].values, format=dateformat)
    df = df.set_index('id')
    oldnames = df.columns[df.columns.str.contains('properties')]
    df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))
    return df
"""

if __name__ == "__main__":
  main()
