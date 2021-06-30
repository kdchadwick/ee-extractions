
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
#beginning = 2003
#end = 2004



def main():

    basin, fts, lat, lon = getBasin(gage)
    flow = getFlow(gage, basin, start, stop)


 #   locs = pd.read_csv('data/coordinates.csv')
 #   coordinates = locs[['Long', 'Lat']].values.tolist()
 #   names = locs['Site Name']
    assets = pd.read_csv('data/layers_short.csv')
    assets['scale'] = assets['scale'].astype('float')
    min_year = assets['beginning_year'].min()
    max_year = assets['end_year'].max()

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
    outputfile = 'exports/watershed2.csv'
  # for i in range(len(pts)):
  #   print('Getting data for point={}'.format(i))
    temp_point = pd.DataFrame({'id':pd.date_range(str(min_year)+"-01-01", str(max_year)+"-01-01")})#, 'point': names[i]})
    #temp_point = pd.DataFrame({'id':pd.datetime('2010-01-01')})
   # temp_point = pd.DataFrame(columns = ["id"])
   # temp_point = temp_point.set_index('id')
   ## print(temp_point.head())
    for d in range(len(assets['gee_path'])):
      path = assets['gee_path'][d]
      collection_short_name=assets['name'][d]+"_"
      beginning = assets['beginning_year'][d]
      end = assets['end_year'][d]

      #print(beginning, end)
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
        
        dateformat=assets['date_format'][d]
        #test = get_data_df(testextract, dateformat=assets['date_format'][d], collection_short_name=collection_short_name)
        d = testextract
        df = pd.json_normalize(d['features'])
        print(df.head())
"""
        #print(df.head())
        #df = df[df.columns[df.columns.str.contains('index')].append(df.columns[df.columns.str.contains('properties')])]
        #print(df.head())
       # df['id'] = df[df.columns[df.columns.str.contains('system:index')]]#.values()
        print(df.filter(regex='properties.system:index').columns)
        df['id'] = df[df.filter(regex='system:index').columns]
        print(df.head())
        df['id'] = pd.to_datetime(df['id'], format= dateformat)
        #df = df[df.columns[df.columns.str.contains('id')].append(df.columns[df.columns.str.contains('properties')])]
        #df = df.reset_index()
        #df = df.set_index('id')
        #df = df.drop(df.filter(regex='index').columns, axis=1)
        oldnames = df.columns[df.columns.str.contains('properties')]
        df = df[df.columns[df.columns.str.contains('properties')]]
        df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))
        print(df.tail())
        annual_temp = annual_temp.append(df)
        print(annual_temp.head())
        #      temp_point = pd.merge(temp_point, annual_temp, how='outer', left_index = True, right_index = True)#on=['id'])

      temp_point = pd.merge(temp_point, annual_temp, how='outer', on=['id'])
      print(temp_point.tail())
      #temp_point.to_csv('exports/{}.csv'.format(collection_short_name), mode='a', header=True)

      #print(temp_point.head())

    all_points = all_points.append(temp_point)

    all_points.to_csv(outputfile, mode='a', header=True)

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
