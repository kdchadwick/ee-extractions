## PET from Hargreave and Samani 1985
from getFlow import getBasin
import pandas as pd
import numpy as np

def getRA(site_lat_decimal):

  ## J (julian day)
  J = (np.linspace(1,365,365))

  ## Gsc (solar constant)  [MJ m-2 day -1] ### DOES THIS NEED TO BE mm??
  Gsc = 0.0820

  ## inverse relative distance Earth-Sun
  dr = 1+0.033*np.cos(((2*np.pi)/365)*J) #checked

  ## delta = solar declination [rad]
  delta = 0.409*np.sin(((2*np.pi)/365)*J-1.39)  #checked

  ## psi [rad] = convert decimal latitude to radians
  psi = (np.pi/180)*(site_lat_decimal) # checked

  ## omega_s (ws)= solar time angle at beginning of period [rad]
  omega_s = np.arccos(-np.tan(psi)*np.tan(delta)) # checked


  ### RA = Put it all together

  ## [ws * sin(psi) * sin(delta) + cos(psi) * cos(delta) * sin(ws)]
  angles = omega_s * np.sin(psi) * np.sin(delta) + np.cos(psi) * np.cos(delta) * np.sin(omega_s)

  RA = ((24*60)/np.pi) * Gsc * dr * angles

  df = pd.DataFrame()
  df['RA'] = RA
  df['J'] = J
  df['J']= df['J'].astype(int)
  return df

# p = df that has prism temperature columns
def getPET(gage, p, tmin = 'prism_tmin', tmax = 'prism_tmax', tmean = 'prism_tmean'):
  #p['id'] = p.index

  # get RA (extraterrestrial radiation) with julian day column
  basin, pts, lat, lon = getBasin(gage)
  RA_df = getRA(lat)

  # add a julian day column to the original prism extraction df
  p['J'] = pd.to_datetime(p['id']).dt.strftime('%j')
  p['J'] = p['J'].astype(int)
  

  # merge prism extraction with RA
  p = p.merge(RA_df, how='left', on=['J'])
  p.to_csv('exports/merge_test.csv', mode='a', header=True)

  #p['Date'] = pd.to_datetime(p['Date'])
  #p = p.sort_values(by=['Date'])

  # calculate PET (Hargreave and Semani 1985)
  Krs = 0.00023
  p['PET'] = Krs * p['RA'] * np.sqrt(p[tmax] - p[tmin]) * (p[tmean] + 17.8) #MADE A CHANGE HERE
  
  p['id'] = pd.to_datetime(p['id'])
  p.set_index('id', inplace=True)
  p.to_csv('exports/final_test.csv', mode='a', header=True)

  return p
