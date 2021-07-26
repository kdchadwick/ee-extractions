#### Given a list of USGS basins, export geojsons ####
from getLocation import getLocation
from gee_unmasked_area import gee_unmasked_area
import pandas as pd
import numpy as np
import geopandas as gpd
import os
import json
import sys
import argparse
import subprocess
import warnings
import ee
ee.Initialize()
warnings.filterwarnings("ignore")

def main():
  parser = argparse.ArgumentParser('Export geometry of list of USGS gauges')
  parser.add_argument('gage_list_csv', type=str)
  parser.add_argument('output_directory', type=str)
  parser.add_argument('-calc_unmasked_areas', type = str, default = 'False')
  parser.add_argument('-exported_collection_name', type = str, default = 'exported_collection')


  args = parser.parse_args()

  print('basin_vis.py is checking and generating output directory')
  if os.path.isdir(args.output_directory) == True:
    print('WARNING: this output directory already exists. \n Exiting... \n \n \n')
    sys.exit()
  else: 
    subprocess.call('mkdir ' + os.path.join(args.output_directory), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'basin_vis'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'basin_vis', 'settings'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'basin_vis', 'exports'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'basin_vis', 'figs'), shell=True)



  sites = pd.read_csv(args.gage_list_csv)
  gages = sites['SITE_NO'].unique()
  print('Gage geometries to extract: ', gages)
  
  print('\n \nSaving inputs and args to settings folder in {}'.format(args.output_directory))
  with open(os.path.join(args.output_directory, 'basin_vis', 'settings', 'input_args.txt'), 'w') as f:
    json.dump(args.__dict__, f, indent=2)
  sites.to_csv(os.path.join(args.output_directory, 'basin_vis', 'settings', 'sites.csv'))
  
  type='USGS_basin'
  output_type = 'ee'
  ca = gpd.read_file('data/ca-state-boundary/CA_State_TIGER2016.shp')
  
  counter = 1
  for gage in gages:
      print('\nGetting gage ', counter,' of', len(gages))
      #print('Getting gage ', gage)
      sites_fc, bbox_fc, site_name = getLocation(type, output_type, gage, shape = ca, plot_map=True, output_directory = args.output_directory, sub_directory = '/basin_vis')
      counter += 1

      if counter == 2:
        all_sites_fc = sites_fc
      else:
        all_sites_fc = all_sites_fc.merge(sites_fc)
  

  task_config = {
    'collection': all_sites_fc,
    'description': args.exported_collection_name,
    'fileFormat': 'SHP'
  }

  task=ee.batch.Export.table.toDrive(**task_config)
  task.start()
  
  if args.calc_unmasked_areas.lower() == 'true':
    gdf_long = gee_unmasked_area(feature_collection = all_sites_fc, directory = args.output_directory, collection_name=args.exported_collection_name)
    gdf_long.to_csv(os.path.join(args.output_directory, 'basin_vis', 'exports', 'basins_w_unmasked_area.csv'))


      
if __name__ == "__main__":
  main()

