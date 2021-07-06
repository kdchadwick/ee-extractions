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


import ee
ee.Initialize()

from getPET_har import getRA
from getPET_har import getPET
from interp_et import interp_et
#from dralle_storage import g
#from dralle_storage import KirchnerBinning
from dralle_storage import recessionAnalysis


def main():
  
  basin_name = 'Clear Creek'
  gage = gage = 11372000 #Clear Creek
  df = pd.read_csv('exports/ClearCreek_ext.csv')
  et_name = 'modis_PET'


  df = getPET(gage, df) # add PET columns using Hargreaves calculated from prism temperature
  df = interp_et(df) # interpolate
  recession = df[['prism_ppt','q_mm', et_name]].rename(columns = {"prism_ppt":"ppt", "q_mm":"q", str(et_name):"et"}).dropna()
  print('Dataframe ready!')
  print('Recession analysis in progress...')
  #years, recession = recessionAnalysis(recession)
  #print('Recession analysis complete.')



  (print('Number of data using (P)ET dataset ' + et_name + ':{}'.format(len(qs))))
  

if __name__ == "__main__":
  main()




