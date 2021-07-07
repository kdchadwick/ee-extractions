import datetime
import pandas as pd
import math
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import geopandas as gpd
import folium
from IPython.display import Image
import ee
ee.Initialize()

# Initial date of interest (inclusive).
i_date = '2017-01-01'

# Final date of interest (exclusive).
f_date = '2020-01-01'


ca = ee.FeatureCollection('TIGER/2016/States').filter(ee.Filter.eq('NAME', 'California')).getInfo()
past_temp = ee.ImageCollection("ECMWF/ERA5_LAND/MONTHLY").select('temperature_2m').filterDate(i_date, f_date).getInfo()
pred_temp = ee.ImageCollection("NASA/NEX-DCP30_ENSEMBLE_STATS").select('tasmax_median').filterDate(i_date, f_date)
ca_json = ee.FeatureCollection('TIGER/2016/States').filter(ee.Filter.eq('NAME', 'California')).geometry.toGeoJSON()

# df = pd.json_normalize(past_temp)
# df = df[df.columns[df.columns.str.contains('id')].append(df.columns[~df.columns.str.contains('visualization')])]
# print(df.head())
# print(pd.json_normalize(past_temp).columns)
# print(pd.json_normalize(past_temp).head())

# print(pd.__version__)

# past_img = past_temp.mean()
# past_img = past_img.add(-273.15)
# past_img_ca = past_img.clip(ca.geometry())
# ca_shp = ca.geometry()
#print(ca.geometry())

fig = plt.figure(figsize=(6, 6))
ax = fig.add_axes([0.05, 0.05, 0.9, 0.9])
ca_json.plot(ax=ax, facecolor='none', edgecolor='black')
plt.savefig('test_ca.png')

# Create a URL to the styled image for CA
# url = past_img_ca.getThumbUrl({
#     'min': 0, 'max': 30, 'dimensions': 512, #'region': ca.geometry(),
#     'palette': ['blue', 'yellow', 'orange', 'red']})
# print('\n' + url)

# # Display the thumbnail land surface temperature in CA
# print('\nPlease wait while the thumbnail loads, it may take a moment...')
# Image(url=url)


# def add_ee_layer(self, ee_image_object, vis_params, name):
#     """Adds a method for displaying Earth Engine image tiles to folium map."""
#     map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)
#     folium.raster_layers.TileLayer(
#         tiles=map_id_dict['tile_fetcher'].url_format,
#         attr='Map Data &copy; <a href="https://earthengine.google.com/">Google Earth Engine</a>',
#         name=name,
#         overlay=True,
#         control=True
#     ).add_to(self)

# # Add Earth Engine drawing method to folium.
# folium.Map.add_ee_layer = add_ee_layer
# #testextract = ee.ImageCollection(path).filterDate(yearstart, yearend).filterBounds(bounding_box).map(extract).getInfo()
# #test = get_data_df(testextract, dateformat=assets['date_format'][d], collection_short_name=collection_short_name)



# plot(ca, {}, 'California')
# plt.show()


# # Define the center of our map.
# lat, lon = 36.5, -119

# lc_vis_params = {
#     'min': 1,'max': 17,
#     'palette': ['05450a','086a10', '54a708', '78d203', '009900', 'c6b044',
#                 'dcd159', 'dade48', 'fbff13', 'b6ff05', '27ff87', 'c24f44',
#                 'a5a5a5', 'ff6d4c', '69fff8', 'f9ffa4', '1c0dff']
# }

# my_map = folium.Map(location=[lat, lon], zoom_start=6)
# my_map.add_ee_layer(ca, lc_vis_params, 'CA')
# my_map.save('my_lc_interactive_map.html')

#plt.imshow(ca)
#plt.show()
#ca.plot(figsize=(5,5), edgecolor="purple", facecolor="None")






# months = ee.List.sequence(1, 12)
# years = ee.List.sequence(2010, 2011)

# def function1(y):
#     def function2(m):
#         return past_temp.filter(ee.Filter.calendarRange(y, y, 'year')).filter(ee.Filter.calendarRange(m, m, 'month')).mean().set('month', m).set('year', y)
#     return months.map(function2)

# byMonthYear = ee.ImageCollection.fromImages(years.map(function1).flatten())

# print(byMonthYear)

