
import ee
import datetime
import pandas as pd
import geopandas as gp
import glob
import math
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import Image
import os
import json
import sys
import argparse
import subprocess

 #Personal functions
from extraction_export import extraction_export
from get_data_df import get_data_df
from getFlow import getFlow
from getFlow import getBasin
from getGeometry import getGeometry

ee.Initialize()

def main():

  parser = argparse.ArgumentParser('Run extractions from GEE or USGS API')
  parser.add_argument('asset_layers_csv', type=str)
  parser.add_argument('output_directory', type=str)
  parser.add_argument('-point_csv', type=str)
  parser.add_argument('-wshd', type=str, default='False')
  parser.add_argument('-gage', default=11372000, type=int)

  print('\n \n ee_extractions.py is parsing and cleaning arguments \n')
  args = parser.parse_args()
  if args.wshd.lower() == 'true':
      args.wshd = True

  print('Checking and generating output directory')
  if os.path.isdir(args.output_directory) == True:
    print('WARNING: this output directory already exists. \n Exiting... \n \n \n')
    sys.exit()
  else: 
    subprocess.call('mkdir ' + os.path.join(args.output_directory), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'settings'), shell=True)

  assets = pd.read_csv(args.asset_layers_csv)
  assets['scale'] = assets['scale'].astype('float')
  print('Assets to be extracted: \n ')
  print(assets.head())
  
  print('\n \nSaving inputs and args to settings folder in {}'.format(args.output_directory))
  with open(os.path.join(args.output_directory, 'settings', 'input_args.txt'), 'w') as f:
    json.dump(args.__dict__, f, indent=2)
  assets.to_csv(os.path.join(args.output_directory, 'settings', 'assets.csv'))
  subprocess.call('cp ' + os.path.join(args.point_csv) +' ' + os.path.join(args.output_directory, 'settings', 'export_coords.csv'), shell=True)
  
  pts, bounding_box, names = getGeometry(args.wshd, args.gage, args.point_csv)
  extraction_export(assets, pts, bounding_box, names, args.output_directory, args.wshd, args.gage)


if __name__ == "__main__":
  main()




# ### TO CHANGE BETWEEN EXTRACTING WATERSHED VIA GAGE ID AND POINTS, SET WATERSHED = TRUE OR FALSE
# watershed = False
# gage = 11372000 #set these as optional inputs?
# point_csv = 'data/coordinates_career.csv'
# outputfile = 'exports/career.csv'
