import ee, os
from getLocation import getLocation
import numpy as np
import pandas as pd

ee.Initialize()

# Determine sites 
sites_features, bbox_geom, site_name = getLocation(input_type='USGS_basin', output_type='ee', gage=11465350, output_directory = 'test', sub_directory = 'sub')
startDate = ee.Date('1990-01-01')
endDate = ee.Date('2017-12-31')
pws_start_year= 2011
pws_end_year= 2016


# Grab datasets
states = ee.FeatureCollection("TIGER/2016/States")
landsat = ee.ImageCollection("LANDSAT/LC08/C02/T1_L2")
usgs_lc = ee.ImageCollection("USGS/NLCD_RELEASES/2016_REL")
cwc = ee.ImageCollection("users/pgbrodrick/CWC")
print(type(cwc))


roi = ee.Feature(states.filter(ee.Filter.eq('NAME', 'California')))

# Filter the collection to the 2016 product.
nlcd2016 = usgs_lc.filter(ee.Filter.eq('system:index', '2016')).first()

# Select the land cover band.
landcover = nlcd2016.select('landcover').clipToCollection(sites_features)

def calc_ndvi_landsat(img, startDate, endDate):
  img = img.filter(ee.Filter.date(startDate, endDate))
  img = img.reduce(ee.Reducer.median()).clipToCollection(sites_features)
  ndvi = (img.select([4]).subtract(img.select([3]))).divide(img.select([4]).add(img.select([3])))
  return ndvi


# NDVI calculation for landsat from 1990 when time series begins
base_landsat_ndvi = calc_ndvi_landsat(landsat, ee.Date.fromYMD(2015,6,1), ee.Date.fromYMD(2015,8,1))
# cwc = cwc.toBands()
# cwc = cwc.updateMask(landcover.gte(41))
# cwc = cwc.updateMask(landcover.lte(52))
# cwc = cwc.updateMask(base_landsat_ndvi.gt(0.2))
# cwc = ee.ImageCollection.fromImages(cwc)
# print(type(cwc))


# NDVI calculation for landsat from PWS base year
landsat_ndvi = calc_ndvi_landsat(landsat, ee.Date.fromYMD(2015,6,1), ee.Date.fromYMD(2015,8,1))
# calc 2013-2017 PWS
pws = landcover.multiply(0)
for year in range(pws_start_year, pws_end_year+1):
    loc_cwc_y1 = ee.Image(cwc.filter(ee.Filter.date(ee.Date.fromYMD(year,1,1), ee.Date.fromYMD(year,12,31))).first()).clipToCollection(sites_features)
    loc_cwc_y2 = ee.Image(cwc.filter(ee.Filter.date(ee.Date.fromYMD(year+1,1,1), ee.Date.fromYMD(year+1,12,31))).first()).clipToCollection(sites_features)
    print(year)
    delta_cwc_relative = (loc_cwc_y1.subtract(loc_cwc_y2)).divide(loc_cwc_y1)

    delta_cwc_relative = delta_cwc_relative.updateMask(delta_cwc_relative.gt(0))
    delta_cwc_relative = delta_cwc_relative.unmask(0)

    pws = pws.add(delta_cwc_relative)

pws = pws.updateMask(landcover.gte(41))
pws = pws.updateMask(landcover.lte(52))
pws = pws.updateMask(landsat_ndvi.gt(0.2))

task = ee.batch.Export.image.toDrive(image=pws,  # an ee.Image object.
                                     description='pws_test_export',
                                     folder='pws_test',
                                     fileNamePrefix='pws_test',
                                     scale=30,
                                     crs='EPSG:32610')

task.start()
# collection = pws.sample(geometries=True)

# df = geemap.ee_to_pandas(collection, selectors=['id', 'name'])
# df.head()


# # Break point coordinates up into properties (table columns) explicitly.
# def get_ll(feature):
#     coordinates = feature.geometry().transform('epsg:4326').coordinates()
#     return feature.set('lon', coordinates.get(0), 'lat', coordinates.get(1))

# collection_with_latlon = collection.map(get_ll)
# print(pd.json_normalize(collection).columns())
# #print(collection_with_latlon)

# # Export.table.toDrive({
#     collection: collection_with_latlon,
#     description: 'hist_tx',
#     fileFormat: 'CSV',
# });