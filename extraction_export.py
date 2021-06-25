def extraction_export(assets, pts, names, outputfile, start, end):
  import get_data_df as gd
  import pandas as pd

  all_points = pd.DataFrame()

  for i in range(len(pts)):
    print('Getting data for point={}'.format(i))
    temp_point = pd.DataFrame({'id':pd.date_range(str(start)+"-01-01", str(end)+"-01-01"), 'point': names[i]})

    for d in range(len(assets['gee_path'])):
      path = assets['gee_path'][d]
      collection_short_name=assets['name'][d]+"_"

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
        test = gd.get_data_df(testextract, dateformat=assets['date_format'][d], collection_short_name=collection_short_name)
        annual_temp = annual_temp.append(test)
      temp_point = pd.merge(temp_point, annual_temp, how='left', on=['id'])

    all_points = all_points.append(temp_point)

  all_points.to_csv(outputfile, mode='a', header=False)

