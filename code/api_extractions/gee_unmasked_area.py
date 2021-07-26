import pandas as pd
import numpy as np
import geopandas as gpd
import ee
import time
import sys
import os
import geopandas
ee.Initialize()

def gee_unmasked_area(feature_collection, directory, collection_name):
    #Masks
    woodveg_x_shallowbedrock = ee.Image('users/ericamccormick/20_RockMoisture/masks/woodyVeg_x_shallowBedrock')
    woodyveg = ee.Image('users/ericamccormick/20_RockMoisture/masks/mask_woodyVeg')
    shallowbedrock = ee.Image('users/ericamccormick/20_RockMoisture/masks/mask_shallowBedrock')
    mask_reproj = ee.Image('users/ericamccormick/20_RockMoisture/masks/mask_reproj') #final mask including ET>P
    blank_area = ee.Image(1).reproject(crs='EPSG:4326', scale = 500).multiply(ee.Image.pixelArea())

    list_of_masks = [blank_area, woodveg_x_shallowbedrock, woodyveg, shallowbedrock, mask_reproj]
    all_collection = feature_collection
    for i in list_of_masks:
        mask = i.gt(0).multiply(ee.Image.pixelArea())
        fc_mask = mask.reduceRegions(feature_collection, ee.Reducer.sum(), scale = 500)
        all_collection = all_collection.merge(fc_mask)
    
    task_config = {
        'collection': all_collection,
        'description': 'all_mask_areas',
        'fileFormat': 'SHP'
        }

    task=ee.batch.Export.table.toDrive(**task_config)
    task.start()
    
    print('\nGo to the GEE CodeEditor at: https://code.earthengine.google.com/#')
    print('\nOn the right side, click on the "Tasks" panel. Click the box when complete & follow the link to the files in your GoogleDrive.')
    print('\nPlease fetch the files associated with all_mask_areas.shp from your GoogleDrive and place in ', directory,'.')
    print('\nYou may also want to download the files associated with the clean feature collection', collection_name,'.shp.')
    input('\nType "Done" when complete.\n')
    #time.sleep(120)
    
   # if os.path.isdir(directory + '/all_mask_areas.shp') == False:
   #   
   #     print('File not found.\n Exiting... \n \n \n')
   #     sys.exit()
    path = directory + '/all_mask_areas.shp'
    #print(path)
    gdf = geopandas.read_file(path).dropna()
  

    sites = gdf['Name'].unique()
    list_of_masks_str = ['total_area','woodveg_x_shallowbedrock', 'woodyveg', 'shallowbedrock', 'mask_reproj']

    calc = [str(i) for i in list_of_masks]
    calc = [[i]*len(sites) for i in list_of_masks_str]
    flat_list = [item for sublist in calc for item in sublist]
    #print(flat_list)
    gdf['Mask'] = flat_list
    
    gdf_long = gdf.pivot_table(index=["Gage", "Name"], 
                    columns='Mask', 
                    values='sum')
    gdf_long = gdf_long.reset_index()
    gdf_long['Gage'] = gdf_long['Gage'].astype(str)
    
    for i in list_of_masks_str:
        gdf_long[i+'_%'] = (gdf_long[i] / gdf_long['total_area']) * 100
        
    return gdf_long