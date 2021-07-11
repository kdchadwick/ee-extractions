## Calculate Hargreaves PET using PRISM temperature data
## Code edited by David Dralle, originally from evaplib and meteolib (http://python.hydrology-amsterdam.nl/modules/meteolib.py)

#import requests
from usgs_basin_geometry import usgs_basin_geometry
from meteolib import sun_NR
from evaplib import hargreaves
import numpy as np
import datetime as dt
import pandas as pd

def pet_hargreaves(gage, p, tmin = 'prism_tmin', tmax = 'prism_tmax', tmean = 'prism_tmean'):
    
    '''
    # download packages that Dralle has edited
        url = 'https://raw.githubusercontent.com/daviddralle/daviddralle.github.io/master/teaching_data/evaplib.py'
        r = requests.get(url, allow_redirects=True)
        #open('evaplib.py', 'wb').write(r.content)
        with open('evaplib.py', 'wb') as f:
            f.write(r.content)
            
        url = 'https://raw.githubusercontent.com/daviddralle/daviddralle.github.io/master/teaching_data/meteolib.py'
        r = requests.get(url, allow_redirects=True)
        with open('meteolib.py', 'wb') as f:
            f.write(r.content)
            
        #open('meteolib.py', 'wb').write(r.content)

        from meteolib import meteolib as meteo
        from evaplib import evaplib as evap
    '''

  # Using Eqn 50 From Allen (1998) to get solar radiation from max/min temp difference
    kRs = 0.18


    basin, fts, lat, site_long = usgs_basin_geometry(gage)
    #rng = datetime.datetime.date(p['id'])
    #doy = [rng.timetuple().tm_yday for i in range(len(rng))]
    p['J'] = pd.to_datetime(p['id']).dt.strftime('%j')
    doy = p['J'].astype(int)
    N, Rext = sun_NR(doy, lat)
    Rext_MJ = Rext/(10.0**6)
    Rs = kRs*np.sqrt(p[tmax]-p[tmin])*Rext
    pet = hargreaves(p[tmin], p[tmax], p[tmean], Rext_MJ)
    p['hargreaves_pet'] = pet
  
    return p
'''
  # compute relative humidity using temp and dewpoint
  def get_rh(tmean, tdmean):
      a = 17.625
      b = 243.04
      return 100*np.exp(a*tdmean/(b+tdmean))/np.exp(a*tmean/(b+tmean))

  def get_ea(tdmean):
      return 0.6108*np.exp((17.27*tdmean)/(tdmean+237.3))

  # Using Eqn 50 From Allen (1998) to get solar radiation from max/min temp difference
  kRs = 0.18

  pets = []
  for i,row in gdf.iterrows():
      lat = row.geometry.centroid.y ## E changed to get lat from gage number only
      rng = ppt.index
      doy = [rng[i].timetuple().tm_yday for i in range(len(rng))]
      N, Rext = meteo.sun_NR(doy, lat)
      Rext_MJ = Rext/(10.0**6)
      Rs = kRs*np.sqrt(tmax[row.gage]-tmin[row.gage])*Rext
      pet = evap.hargreaves(tmin[row.gage], tmax[row.gage], tmean[row.gage], Rext_MJ)
      pet = pd.DataFrame(pet,columns=[row.gage])
      pets.append(pet)
  pet = pd.concat(pets,axis=1)
  
  '''