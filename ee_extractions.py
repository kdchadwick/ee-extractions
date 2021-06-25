
import ee
import datetime
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image
import extraction_export
import get_data_df

ee.Authenticate()
ee.Initialize()


def main():

    locs = pd.read_csv('data/coordinates.csv')
    coordinates = locs[['Long', 'Lat']].values.tolist()
    names = locs['Site Name']
    assets = pd.read_csv('data/layers.csv')
    assets['scale'] = assets['scale'].astype('float')

    pts = []
    for i in range(len(coordinates)):
        temp = ee.Feature(ee.Geometry.Point(coords=coordinates[i]))
        pts.append(temp)

    bounding_box = ee.Geometry.Polygon(
            [[[math.floor(min(locs['Long'])), math.ceil(max(locs['Lat']))],
              [math.floor(min(locs['Long'])), math.floor(min(locs['Lat']))],
              [math.ceil(max(locs['Long'])), math.floor(min(locs['Lat']))],
              [math.ceil(max(locs['Long'])), math.ceil(max(locs['Lat']))]]])

    extraction_export(assets, bounding_box, pts, names, 'exports/test.csv', 2003, 2017)

""" 
def extraction_export(assets, bounding_box, pts, names, outputfile, start, end):

  all_points = pd.DataFrame()

  for i in range(len(pts)):
    print('Getting data for point={}'.format(i))
    temp_point = pd.DataFrame({'id': pd.date_range(str(start)+"-01-01", str(end)+"-01-01"), 'point': names[i]})

    for d in range(len(assets['gee_path'])):
      path = assets['gee_path'][d]
      collection_short_name=assets['name'][d]+"_"

      def extract(image):
          pt = pts[i]
          s = assets['scale'][d]
          ft = ee.Feature(pt.geometry())
          reduced = image.reduceRegion(geometry=pt.geometry(), reducer=ee.Reducer.first(), scale=s)
          ft = ft.set(reduced)
          return ft

      print('Extracting data from asset {}'.format(path))
      annual_temp=pd.DataFrame()
      for year in range(start, end):
        print('year {}'.format(year))
        yearstart = str(year)
        yearend = str(year+1)
        testextract = ee.ImageCollection(path).filterDate(yearstart, yearend).filterBounds(bounding_box).map(extract).getInfo()
        test = get_data_df(testextract, dateformat=assets['date_format'][d], collection_short_name=collection_short_name)
        annual_temp = annual_temp.append(test)
      temp_point = pd.merge(temp_point, annual_temp, how='left', on=['id'])

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
