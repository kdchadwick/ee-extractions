
import ee
import datetime
import pandas as pd
import geopandas as gp
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image

# Personal functions
import extraction_export
import get_data_df
from getFlow import getFlow
from getFlow import getBasin
from getGeometry import getGeometry

#ee.Authenticate() #Don't need if you save your authentication
ee.Initialize()

watershed = True
gage = 11134800
#start = '1988-09-30'
#stop = '202-01-01'
#beginning = 2003
#end = 2004
outputfile = 'exports/watershed_wflow_5.csv'




def main():

  ## Pick one or the other to get GEE geometry from set of points (in csv) or from USGS watershed gage ID:
  #pts, bounding_box, names = getGeometry(watershed = False, gage = 0, point_csv = 'data/coordinates.csv')
  fts, bounding_box = getGeometry(watershed = True, gage = 11134800, point_csv = '')



  # Import csv of GEE assets you want to extract from
  assets = pd.read_csv('data/layers_short.csv')
  assets['scale'] = assets['scale'].astype('float')

 ### extraction_export(assets, bounding_box, pts, names, 'exports/test.csv', 2003, 2004)



#def extraction_export(assets, pts, names, outputfile, start, end, watershed = False, gage = 11134800):

  
  all_points = pd.DataFrame()

  #if watershed == True:
  temp_point = pd.DataFrame({'id':pd.date_range(str(2003)+"-01-01", str(2003)+"-01-02")})

  for d in range(len(assets['gee_path'])):
    path = assets['gee_path'][d]
    collection_short_name=assets['name'][d]+"_"
    beginning = assets['beginning_year'][d]
    end = assets['end_year'][d]

    def extract(image):
      s = assets['scale'][d]
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
      d = testextract
      df = pd.json_normalize(d['features'])
      df['id'] = df['properties.system:index']
      df['id'] = pd.to_datetime(df['id'], format= dateformat)
      df = df.set_index('id')
      df = df.drop(df.filter(regex='index').columns, axis=1)

      oldnames = df.columns[df.columns.str.contains('properties')]
      df = df[df.columns[df.columns.str.contains('properties')]]
      df.columns = list(map(lambda x: x.replace('properties.', collection_short_name),oldnames))

      annual_temp = annual_temp.append(df)
    
    temp_point = pd.merge(temp_point, annual_temp, how='outer', on=['id'])
    

  all_points = all_points.append(temp_point)
  flow = getFlow(gage)
  print(flow.head())
  print(all_points.head())
  all_points = pd.merge(all_points, flow, how = 'outer', on = ['id'], sort = True)
  print(all_points.head())
  #all_points = all_points.sort_index()
  all_points.to_csv(outputfile, mode='a', header=True)

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
