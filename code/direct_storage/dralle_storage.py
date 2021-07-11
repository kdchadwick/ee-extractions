## Direct/Indirect storage from Dralle et al. (2018), 
# Quantification of the seasonal hillslope water storage that does not drive streamflow
# (https://doi.org/10.1002/hyp.11627).
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


def g(q,p):
    if np.size(np.array(q)) == 1: return np.exp(np.sum([p[i]*np.log(q)**(len(p)-i-1) for i in range(len(p))]))
    return [np.exp(np.sum([p[i]*np.log(qq)**(len(p)-i-1) for i in range(len(p))])) for qq in np.array(q)]

# Bin dq/dt data
def KirchnerBinning(df, min_per_bin = 7, loud=False): #changed this from 10 to 7 to match paper
    df = df.sort_values('q',ascending=False)
    
    logQ = np.array(np.log(df.q))
    
    logRange = np.max(logQ) - np.min(logQ)
    minBinSize = logRange*.01
  
    binBoundaries = [0]
    for i in range(1,len(df)):    
        if abs(logQ[i] - logQ[binBoundaries[-1]]) < minBinSize: 
            if loud: print('Bin too small')
            continue
            
        if abs(i-binBoundaries[-1]) < min_per_bin:
            if loud: print('Not enough data points')
            continue  
            
        curr = df.dq[binBoundaries[-1]:i]
        if np.std(-curr)/np.sqrt(abs(i-binBoundaries[-1])) > np.mean(-curr)/2: 
            if loud: print('Bin too heterogeneous')
            continue    
        
        binBoundaries.append(i)
    return binBoundaries

# Rainfall interception function
def intercept_rain(ppt, interception_depth):
    freq = ppt.index.freq
    idx = ppt.index.copy()
    prcp = ppt.copy()
    precip_pre = ppt.ppt.resample('D').mean()+1e-12
    precip_post = precip_pre.apply(lambda x: np.max([0,x-interception_depth])) 
    frac_int = (precip_pre.sum() - precip_post.sum())/precip_pre.sum()
    print('Fraction intercepted = %.2f'%frac_int)
    rng = pd.date_range(precip_post.index[0], precip_post.index[-1], freq=freq)
    daily_multiplication_factor = precip_post/precip_pre
    daily_multiplication_factor = pd.DataFrame({'factor':daily_multiplication_factor.resample(freq).ffill().tolist()},index=rng)
    ppt.ppt = daily_multiplication_factor.factor*prcp.ppt
    return ppt


def recessionAnalysis(recession, basin_name, rainfall_lag = 1.0, mean_fraction = 0.001, interception = False):
  ##recession = recession.set_index(pd.to_datetime('id'))
  # Set up necessary constants (like dt, lag, and meanQ)
  num_secs = 86400 # seconds in a day
  dt = 1.0 # days
  lag = 1 #int(rainfall_lag/num_secs) #right now this = 0..??
  meanQ = np.mean(recession['q'])

  # Lists to store q and its derivative
  dqs = []
  qs = []

  # Get a list of years to loop through
  years = list(set(recession.index.year))
  years.sort()
  #del years[-1] # This was necessary when the df for q was shorter than for ppt to avoid having mis-matched data lengths in the last year

  # Loop through winter months
  for year in years:
    startdate = '11-' + str(year)
    enddate = '3-' + str(year+1)
    rain = np.array(recession['ppt'].loc[startdate:enddate])
    runoff = np.array(recession['q'].loc[startdate:enddate])
    i = lag

    while i < len(rain):

        # Too much rain.
      if np.sum(dt * rain[i-lag:i+1]) > 2: #I CHANGED THIS TO 2 mm from 0.002 m
        i+=1
        continue


      idx_next_rain = np.where(rain[i+1:]>0)[0]
      if len(idx_next_rain) > 0:
        idx_next_rain = idx_next_rain[0] + (i+1)
      
      else:
        # no more rain for this particular year
        break

        # too short of a rainless period for analysis 
      if idx_next_rain==i+1: 
          i += 2
          continue
      

      # get dq/dt going forward, not including the next day of rainfall
      for j in range(i, idx_next_rain):
          q_diffs = runoff[j] - runoff[j+1:idx_next_rain]
          idx_end = np.where(q_diffs>mean_fraction*meanQ)[0]
          if len(idx_end)>0:
              idx_end = idx_end[0]
              qs.append((runoff[j] + runoff[j+idx_end+1])/2)
              dqs.append((runoff[j+idx_end+1]-runoff[j])/(dt*(idx_end+1)))
          else:
              i = idx_next_rain + lag + 1
              break 

      # End loop by effectively setting i = len(rain)
      i = idx_next_rain + lag + 1
      
  qs = np.array(qs)
  dqs = np.array(dqs)    
  qs = np.array(qs)
  dqs = np.array(dqs)
  df_kirchner = pd.DataFrame({'q':qs, 'dq':dqs})
  df_kirchner = df_kirchner.sort_values('q',ascending=False)
  binBoundaries = KirchnerBinning(df_kirchner, min_per_bin=7) #WAS 7 min per bin
  qs = [np.mean(df_kirchner.q[binBoundaries[i]:binBoundaries[i+1]]) for i in range(len(binBoundaries)-1)]
  dqs =   np.array([np.mean(df_kirchner.dq[binBoundaries[i]:binBoundaries[i+1]]) for i in range(len(binBoundaries)-1)])
  sigmas = np.array([np.std(np.log(-df_kirchner.dq[binBoundaries[i]:binBoundaries[i+1]].loc[df_kirchner.dq[binBoundaries[i]:binBoundaries[i+1]]<0]))/np.sqrt(binBoundaries[i+1]-binBoundaries[i]) for i in range(len(binBoundaries)-1)]) + 1e-12
  p = np.polyfit(x=np.log(qs), y=np.log(-dqs), deg=2, w=1/sigmas**2)
  f = plt.figure(figsize=(4,3))
  plt.errorbar(np.log(qs), np.log(-dqs), yerr = sigmas,fmt='o',capsize=2,**{'ms':2, 'mfc':'k','zorder':1})
  x = np.log(qs)
  coefficient_of_dermination = r2_score(np.log(-dqs), p[2] + p[1]*x + p[0]*x**2)
  plt.plot(x, p[2] + p[1]*x + p[0]*x**2,lw=2, label='$\mathrm{R^2}$ = %.2f'%coefficient_of_dermination,zorder=10)
  p[1] = p[1]-1
  plt.xlabel('log(Q)')
  leg = plt.legend(fontsize=10,loc='best')
  leg.set_frame_on(False)
  #plt.ylim([-12,-5])
  #plt.xlim([-9.1,-4])
  plt.title(basin_name,fontsize=12)
  ax = f.get_axes()[0]
  plt.ylabel(r'$\log \left( -\mathrm{\frac{dQ}{dt}}\right)$')
  plt.tight_layout()
  # plt.savefig('./figures/dqdt_vs_q_clearcreek.pdf')

  (print('\nRecession analysis complete. Number of bins/data = {}'.format(len(qs))))
    
  return years, recession, p, dt

def storage(years, recession, p, dt):
  recession['direct_storage'] = 0

  for year in years: 
      startDate = '10-01-' + str(year)
      endDate = '9-30-' + str(year+1)
      thisYear = recession.loc[startDate:endDate]
      if len(thisYear)<100:
          continue

      # cumulative integral of dynamic storage for this water year, assuming we start at 0        
      qvar = thisYear.q.tolist()
      direct_S = [0]
      for i in range(1,len(qvar)):
          qi = qvar[i]
          qi1 = qvar[i-1]
          qintegrate = np.linspace(qi1, qi, 5)
          direct_S.append(direct_S[i-1] + np.trapz([1/gg for gg in g(qintegrate,p)],qintegrate))
          if direct_S[i] < 0: 
              direct_S[i] = 0
      recession['direct_storage'].loc[startDate:endDate] = direct_S
  
  ## DIRECT STORAGE:
  recession['indirect_storage'] = 0
  recession['total'] = 0
  annualmax_indirect = []
  annualmax_direct = []
  maxyears = []
  for year in years[:-1]: #I removed the -1 in years[:-1]: for a while, but now I need it to prevent errors...
      startDate = '10-1-' + str(year)
      endDate = '6-1-' + str(year+1)
      idx = recession.loc[startDate:endDate].index
      thisYear = recession.loc[idx]
      petYear = recession['et'].loc[idx].values
      direct_year = recession['direct_storage'].loc[idx].values
      cumQ = np.array(dt*thisYear.q.cumsum())
      rain = np.array(recession['ppt'].loc[idx].ffill())
      cumRain = np.array(dt*recession['ppt'].loc[idx].ffill().cumsum())
      indirect_year = np.zeros(np.shape(cumRain))
      
      for i in range(1,len(indirect_year)):
          iyt = cumRain[i] - cumQ[i] - np.cumsum(petYear*dt)[i] - direct_year[i]
          if iyt<0:
              petYear[i] = 0
          indirect_year[i] = cumRain[i] - cumQ[i] - np.cumsum(petYear*dt)[i] - direct_year[i]
      total = cumRain - cumQ - np.cumsum(petYear)*dt
      indirect_year_df = pd.DataFrame(indirect_year, index=idx).resample('D').mean()
      direct_year_df = pd.DataFrame(direct_year, index=idx).resample('D').mean()
      maxyears.append(year+1)
      recession['indirect_storage'].loc[idx] = indirect_year
      recession['total'].loc[idx] = total
      annualmax_indirect.append(np.max(indirect_year))
      annualmax_direct.append(np.max(direct_year))

  annualmax_indirect = np.array(annualmax_indirect)
  annualmax_direct = np.array(annualmax_direct)
  
  storage_df = pd.DataFrame()
  #storage_df['years'] = years[:,-1]
  storage_df['direct'] = annualmax_direct
  storage_df['indirect'] = annualmax_indirect
  #print(storage_df)

  #### STATISTICS TO PRINT ####
  idx = (recession.index.month>=12)|(recession.index.month<=2)
  ismean = recession.indirect_storage.loc[idx].mean()
  isstd = np.std(recession.indirect_storage.loc[idx])
  iscv = isstd/ismean
  dsmean = recession.direct_storage.loc[idx].mean()
  dsstd = np.std(recession.direct_storage.loc[idx])
  dscv = dsstd/dsmean
  printstr = '\nAll winter months: indirect storage mean = %.2f pm %.2f, cv = %.2f; direct mean = %.2f, cv = %.2f'%(ismean, isstd, iscv, dsmean, dscv)
  print(printstr)
  
  return recession, annualmax_indirect, annualmax_direct, maxyears