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
  parser.add_argument('-et_name', default = 'hargreaves_pet', type=str) #need to come back to this one
  parser.add_argument('-gage', default=np.nan, type=int) #should this be -gage or just gage?
  parser.add_argument('-basin_name', default = "", type=str)
  parser.add_argument('-disturbance_date', default="NaN", type=str)




  print('\n \ndirect_storage.py is parsing and cleaning arguments')
  args = parser.parse_args()
  if math.isnan(args.gage):
    print('WARNING: No USGS gage is specified. \nExiting... \n \n \n')
    sys.exit()

  print('\nChecking and generating output directory')
  if os.path.isdir(args.output_directory) == True:
    print('WARNING: this output directory already exists. \n Exiting... \n \n \n')
    sys.exit()
  else: 
    subprocess.call('mkdir ' + os.path.join(args.output_directory), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'settings'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'exports'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'figs'), shell=True)

  
  print('\nSaving inputs and args to settings folder in {}'.format(args.output_directory))
  with open(os.path.join(args.output_directory, 'settings', 'input_args.txt'), 'w') as f:
    json.dump(args.__dict__, f, indent=2)

  df = pd.read_csv(args.timeseries_csv)
  #Save original timeseries in the settings folder
  df.to_csv(os.path.join(args.output_directory, 'settings', 'original_timeseries.csv'), mode='a', header=True)

  #Calculate Hargreaves PET
  df = pet_hargreaves(args.gage, df)
  df = df.set_index(pd.to_datetime(df['id']))
  df.to_csv(os.path.join(args.output_directory, 'exports', 'df_withPET.csv'), mode='a', header=True)

  #### SPLIT DATAFRAME INTO PRE AND POST DISTURBANCE ####
  if args.disturbance_date == "NaN":
    
    recession = df[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt = recessionAnalysis(recession, args.basin_name)

    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    recession.to_csv(os.path.join(args.output_directory, 'exports', 'timeseries_withstorage.csv'), mode='a', header=True)
    
    #### PLOTS ####
    # Single water year timeseries
    start_date = '10-2015'
    end_date = '4-2016'
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + '_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(annualmax_indirect, maxyears, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  
  else:
    print('\n \n PRE DISTURBANCE')
    pre = df[df.index < pd.to_datetime(args.disturbance_date)]
    
    recession = pre[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt = recessionAnalysis(recession, args.basin_name)

    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    recession.to_csv(os.path.join(args.output_directory, 'exports', 'pre_disturbance_timeseries_withstorage.csv'), mode='a', header=True)
    
    #### PLOTS ####
    # Single water year timeseries
    start_date = '10-2015'
    end_date = '4-2016'
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + 'pre_disturbance_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(annualmax_indirect, maxyears, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'pre_disturbance_barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  
    print('\n \n POST DISTURBANCE')
    post = df[df.index >= pd.to_datetime(args.disturbance_date)]
    recession = post[['prism_ppt','q_mm', args.et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(args.et_name):"et"}).dropna()
    print('\n \nDataframe ready. Beginning recession analysis.')
    
    # Recession analysis
    years, recession, p, dt = recessionAnalysis(recession, args.basin_name)

    # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
    recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
    recession.to_csv(os.path.join(args.output_directory, 'exports', 'post_disturbance_timeseries_withstorage.csv'), mode='a', header=True)
    
    #### PLOTS ####
    # Single water year timeseries
    start_date = '10-2019'
    end_date = '4-2020'
    f = plot_all_timeseries(recession, dt, args.basin_name, start_date, end_date)
    f.savefig(os.path.join(args.output_directory, 'figs', args.basin_name + 'post_disturbance_timeseries_' + start_date + '_' + end_date + '.pdf'))

    # Bar plots of indirect and direct storage
    f = bar_indirect(annualmax_indirect, maxyears, args.basin_name)
    f.savefig(os.path.join(args.output_directory, 'figs', 'post_disturbance_barplot.pdf'))
    print('\n \nAnalysis complete. Plots and dataframe saved to figs and exports folders.\n')
  


if __name__ == "__main__":
  main()