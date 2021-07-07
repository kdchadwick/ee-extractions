from get_data_df import get_data_df
from getFlow import getFlow
import pandas as pd
import ee

def extraction_export(assets, pts, bounding_box, names, outputfile, watershed, gage):
  all_points = pd.DataFrame()

  if watershed == True:
    temp_point = pd.DataFrame({'id':pd.date_range(str(2003)+"-01-01", str(2003)+"-01-02")})

    for d in range(len(assets['gee_path'])):
      path = assets['gee_path'][d]
      collection_short_name = assets['name'][d]+"_"
      beginning = int(assets['beginning_year'][d])
      end = int(assets['end_year'][d])
      dateformat=assets['date_format'][d]

      def extract(image):
        s = assets['scale'][d]
        reduced = image.reduceRegion(geometry=pts,
                                    reducer=ee.Reducer.mean(),
                                    scale=s)
        fts_reduced = pts.set(reduced)
        return fts_reduced


      print('Extracting data from asset {}'.format(path))
      annual_temp=pd.DataFrame()

      for year in range(beginning, end):
        print('year {}'.format(year))
        yearstart = str(year)
        yearend = str(year+1)
        testextract = ee.ImageCollection(path).filterDate(yearstart, yearend).filterBounds(bounding_box).map(extract).getInfo()
        df = get_data_df(testextract, dateformat, collection_short_name, watershed)
        annual_temp = annual_temp.append(df)
      
      temp_point = pd.merge(temp_point, annual_temp, how='outer', on=['id'])
      

    all_points = all_points.append(temp_point)
    flow = getFlow(gage)
    all_points = pd.merge(all_points, flow, how = 'outer', on = ['id'], sort = True)
    all_points.to_csv(outputfile, mode='a', header=True)

  else:
    start_min = assets['beginning_year'].min()
    end_max = assets['end_year'].max()
    for i in range(len(pts)):
      print('Getting data for point={}'.format(i))
      temp_point = pd.DataFrame({'id':pd.date_range(str(start_min)+"-01-01", str(end_max)+"-01-01"), 'point': names[i]})
      #temp_point = pd.DataFrame({'id':pd.date_range(str(2003)+"-01-01", str(2003)+"-01-02")})

      for d in range(len(assets['gee_path'])):
        path = assets['gee_path'][d]
        collection_short_name=assets['name'][d]+"_"
        dateformat=assets['date_format'][d]
        start = assets['beginning_year'][d]
        end = assets['end_year'][d]

        def extract(image):
          pt = pts[i]
          s = assets['scale'][d]
          ft = ee.Feature(pt.geometry())
          reduced = image.reduceRegion(geometry=pt.geometry(),
                                      reducer=ee.Reducer.first(),
                                      scale=s)
          ft = ft.set(reduced)
          return ft

        print('Extracting data from asset {}'.format(path))
        annual_temp=pd.DataFrame()
        for year in range(start, end):
          print('year {}'.format(year))
          yearstart = str(year)
          yearend = str(year+1)
          testextract = ee.ImageCollection(path).filterDate(yearstart, yearend).filterBounds(bounding_box).map(extract).getInfo()
          test = get_data_df(testextract, dateformat, collection_short_name, watershed)

          annual_temp = annual_temp.append(test)
        temp_point = pd.merge(temp_point, annual_temp, how='left', on=['id'], sort = True)

      all_points = all_points.append(temp_point)

    all_points.to_csv(outputfile, mode='a', header=True)