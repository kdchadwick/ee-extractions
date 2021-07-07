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

from getPET_har import getRA
from getPET_har import getPET
from interp_et import interp_et
from dralle_storage import g
from dralle_storage import KirchnerBinning
from dralle_storage import recessionAnalysis
from dralle_storage import storage
from plots_direct_storage import plot_all_timeseries
from plots_direct_storage import bar_indirect
from sklearn.metrics import r2_score


def main():
  # Set up imports/exports and names
  basin_name = 'ClearCreek'
  gage = gage = 11372000 #Clear Creek
  df = pd.read_csv('exports/ClearCreek_ext.csv')
  et_name = 'modis_PET'
  print('(P)ET dataset being used is ' + et_name)

  # Get dataframe in order
  df = getPET(gage, df) # add PET columns using Hargreaves calculated from prism temperature
  df = interp_et(df) # interpolate
  recession = df[['prism_ppt','q_mm', et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(et_name):"et"}).dropna()
  print('Dataframe ready!')
  
  # Recession analysis
  years, recession, p, dt = recessionAnalysis(recession, basin_name)
  print('Recession analysis complete.')

  # Calculate indirect and direct storage using results from recession analysis, update 'recession' df
  recession, annualmax_indirect, annualmax_direct, maxyears = storage(years, recession, p, dt)
  
  #### PLOTS ####
  
  # Single water year timeseries
  start_date = '10-2015'
  end_date = '4-2016'
  plot_all_timeseries(recession, dt, basin_name, start_date, end_date)
  
  # Bar plots of indirect and direct storage
  bar_indirect(annualmax_indirect, maxyears, basin_name)
  
  #
  
if __name__ == "__main__":
  main()




