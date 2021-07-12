## Replicate analyses and figures from
# Quantification of the seasonal hillslope water storage that does not drive streamflow
# (Dralle et al, 2018, https://doi.org/10.1002/hyp.11627).

import geopandas as gp
import pandas as pd 
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit
import glob
import pickle
import scipy
import matplotlib.dates as mdates
import datetime
from sklearn.metrics import r2_score
import datetime
import warnings
warnings.filterwarnings('ignore')


import ee
ee.Initialize()

#from getPET_har import getRA
#from getPET_har import getPET
from interp_et import interp_et
from getFlow import usgs_discharge
from dralle_storage import g
from dralle_storage import KirchnerBinning
from dralle_storage import recessionAnalysis
from dralle_storage import storage
from plots_direct_storage import plot_all_timeseries
from plots_direct_storage import bar_indirect
from sklearn.metrics import r2_score
from pet_hargreaves import pet_hargreaves
import os
import json
import sys
import argparse
import subprocess
import glob
import math



def main():

  parser = argparse.ArgumentParser('Calculate direct/indirect storage of a gaged USGS watershed')
  parser.add_argument('output_directory', type=str)
  parser.add_argument('timeseries_csv', type=str)
  parser.add_argument('gage', type=int)
  parser.add_argument('-new_directory', type=str, default='False')
  parser.add_argument('-et_name', default = 'hargreaves_pet', type=str) #need to come back to this one
  parser.add_argument('-basin_name', default = "", type=str)
  parser.add_argument('-disturbance_date', default="NaN", type=str)
  parser.add_argument('-plot_year', default=2015, type=int)
  parser.add_argument('-plot_year_postdisturb', default=2019, type=int)


  print('\n \ndirect_storage.py is parsing and cleaning arguments')
  args = parser.parse_args()
  if math.isnan(args.gage):
    print('WARNING: No USGS gage is specified. \nExiting... \n \n \n')
    sys.exit()
    
  if args.new_directory.lower() == 'true':
    print('\nChecking and generating output directory')
    if os.path.isdir(args.output_directory) == True:
      print('\nWARNING: User specified to make new directory, but one already exists. \nExiting... \n \n \n')
      sys.exit()
    else: 
      subprocess.call('mkdir ' + os.path.join(args.output_directory), shell=True)
      subprocess.call('mkdir ' + os.path.join(args.output_directory, 'settings'), shell=True)
      subprocess.call('mkdir ' + os.path.join(args.output_directory, 'exports'), shell=True)
      subprocess.call('mkdir ' + os.path.join(args.output_directory, 'figs'), shell=True)
  elif args.new_directory.lower() == 'false':
      if os.path.isdir(args.output_directory) == False:
        print('\nWARNING: User specified directory exists, but it does not. \nExiting...\n \n \n')
        sys.exit()
      if os.path.isdir(args.output_directory + '/settings') == False:
        subprocess.call('mkdir ' + os.path.join(args.output_directory, 'settings'), shell=True)
      if os.path.isdir(args.output_directory + '/exports') == False:
        subprocess.call('mkdir ' + os.path.join(args.output_directory, 'exports'), shell=True)
      if os.path.isdir(args.output_directory + '/figs') == False:
        subprocess.call('mkdir ' + os.path.join(args.output_directory, 'figs'), shell=True)
  
  print('\nSaving inputs and args to settings folder in {}'.format(args.output_directory))
  with open(os.path.join(args.output_directory, 'settings', 'input_args.txt'), 'w') as f:
    json.dump(args.__dict__, f, indent=2)

  # save original dataframe
  df = pd.read_csv(args.timeseries_csv)
  df.to_csv(os.path.join(args.output_directory, 'settings', 'original_timeseries.csv'), mode='a', header=True)
  # calculate hargreaves pet
  df = pet_hargreaves(args.gage, df)
  df = df.set_index(pd.to_datetime(df['id']))
  pet_path = os.path.join(args.output_directory, 'exports', 'df_withPET.csv')
  df.to_csv(pet_path, mode='a', header=True)

  ############################ NO DISTURBANCE ############################
  if args.disturbance_date == "NaN":
    
    recession = df[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt, f = recessionAnalysis(recession, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'recession_plot.pdf'))

    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    recession.to_csv(os.path.join(args.output_directory, 'exports', 'timeseries_withstorage.csv'), mode='a', header=True)
    
    # Single water year timeseries
    start_date = '10-' + str(args.plot_year)
    end_date = '4-' + str(args.plot_year + 1)
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + '_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(annualmax_indirect, maxyears, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  
  ############################ PRE DISTURBANCE ANALYSIS ############################
  else:
    print('\n \n PRE DISTURBANCE')
    pre = df[df.index < pd.to_datetime(args.disturbance_date)]
    
    recession = pre[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt, f = recessionAnalysis(recession, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'pre_disturbance_recession_plot.pdf'))
    
    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    pre_data_path = os.path.join(args.output_directory, 'exports', 'pre_disturbance_timeseries_withstorage.csv')
    recession.to_csv(pre_data_path), mode='a', header=True)
    
    # Single water year timeseries
    start_date = '10-' + str(args.plot_year)
    end_date = '4-' + str(args.plot_year + 1)
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + 'pre_disturbance_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(annualmax_indirect, maxyears, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'pre_disturbance_barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  
    ############################ POST DISTURBANCE ANSLYSIS ############################
    print('\n \n POST DISTURBANCE')
    post = df[df.index >= pd.to_datetime(args.disturbance_date)]
    recession = post[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt, f = recessionAnalysis(recession, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'post_disturbance_recession_plot.pdf'))

    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    post_data_path = os.path.join(args.output_directory, 'exports', 'post_disturbance_timeseries_withstorage.csv')
    recession.to_csv(post_data_path, mode='a', header=True)
    
    # Single water year timeseries
    start_date = '10-' + str(args.plot_year_postdisturb)
    end_date = '4-' + str(args.plot_year_postdisturb + 1)
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + 'post_disturbance_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(df)
    f.savefig(os.path.join(args.output_directory, 'figs', 'post_disturbance_barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  


if __name__ == "__main__":
  main()