## Direct/Indirect storage from Dralle et al. (2018), 
# Quantification of the seasonal hillslope water storage that does not drive streamflow
# (https://doi.org/10.1002/hyp.11627).
import numpy as np
import pandas as pd

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


def recessionAnalysis(recession, rainfall_lag = 1.0,   mean_fraction = 0.001, interception = False):
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

    

    (print('Number of data using (P)ET dataset ' + et_name + ':{}'.format(len(qs))))
    
    return years, recession