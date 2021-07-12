# plots direct storage

import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import pandas as pd
import seaborn as sns

def plot_all_timeseries(recession, dt, basin_name, start_date, end_date):
  uselog = True
  f, (ax1) = plt.subplots(1,figsize=(6.5,4))
  labels = []
  recession['indirect_storage'].plot(style='--',linewidth=1.5, ax=ax1)
  labels.append('Indirect storage ($\mathrm{S}_\mathrm{i}$)')
  recession['direct_storage'].plot(linewidth=1.5, ax=ax1)
  labels.append('Direct storage ($\mathrm{S}_\mathrm{d}$)')
  recession['total'].plot(linewidth=1.5, ax=ax1, alpha=0.3)
  labels.append('Total ($\mathrm{S}_\mathrm{T}$)')

  pcumulative = recession['ppt'].loc[start_date:end_date].cumsum()*dt*1000
  qcumulative = recession['q'].loc[start_date:end_date].cumsum()*dt
  pcumulative.plot(style=':', lw=1.5)
  labels.append('$\sum P$')
  qcumulative.plot(style='-.', lw=1.5)
  labels.append('$\sum Q$')

  ax1.set_xlim([start_date,end_date])
  if uselog:
      ax1.set_yscale('log')
      ax1.set_ylim([1e-1,1e4])
      ax1.yaxis.set_major_formatter(matplotlib.ticker.FormatStrFormatter("%.1f"))
      ax1.yaxis.grid(which="minor", color='k', linestyle='-', linewidth=0.5, alpha=0.1)
  else:
      ax1.set_ylim([0,2000])
      ax1.grid(**{'ls':'--', 'lw':0.3})


  ax1.set_title(basin_name)

  leg = ax1.legend(labels, loc='upper left', ncol=2)
  leg.set_frame_on(False)
  ax1.set_ylabel('[mm]')
  ax1.set_xlabel('')
  f.autofmt_xdate()
  plt.tight_layout()
  return f
  #plt.savefig('figs/' + basin_name + '_' + start_date + '_' + end_date + '.pdf')

def bar_indirect(annualmax_indirect, maxyears, basin_name):
    
  d = pd.DataFrame({'Annual maximum':annualmax_indirect[:-1], 'Year':maxyears[:-1]})
  f = plt.figure(figsize=(5,4.5))
  themean = 10*round(d['Annual maximum'].mean()/10.0)
  upper = 10*round(np.std(d['Annual maximum'])/10.0)+themean
  lower = -10*round(np.std(d['Annual maximum'])/10.0)+themean
  legstr = r'Mean ($\mu - \sigma$, $\mu+\sigma$) $\approx$'
  legstr +=  ' %.0f (%.0f, %.0f)'%(themean,lower,upper)
  plt.plot([-0.5,len(maxyears) - 1.5],[themean,themean],label=legstr,c='C1',lw=2)
  h = plt.bar(range(len(d.Year)), d['Annual maximum'], width=0.2)
  plt.subplots_adjust(bottom=0.3)
  xticks_pos = [0.5*patch.get_width() + patch.get_xy()[0] for patch in h]
  plt.xticks(xticks_pos, maxyears[:-1],  ha='right', rotation=45) ### Erica added :-1

  plt.ylabel('mm')
  leg = plt.legend(loc='upper left')
  leg.set_frame_on(False)
  plt.axhspan(lower,upper,color='k',alpha=0.1)

  plt.xlim([-0.5, len(maxyears) - 1.5])
  #plt.ylim([0,600])
  plt.title('Indirect storage max by water year ' + basin_name)
  plt.xlabel('Water year')

  return f
  #plt.savefig('figs/' + basin_name + '_maxes.pdf')

def plot_dv(df, args.disturbance_date):
  winter_months = [11, 12, 1, 2, 3]
  df = df[df.index.map(lambda t: t.month in winter_months)]
  df['wateryear'] = np.where(~df.index.month.isin([10,11,12]),df.index.year,df.index.year+1)
  df['disturbance'] = np.where(df.index < args.disturbance_date, 'pre_disturbance', 'post_disturbance')
  f = plt.figure(figsize=(6.5,4))
  sns.scatterplot(x = df['prism_ppt'], y = (df['prism_ppt']-df['q_mm'], hue = df['wateryear'], style = df['disturbance'])
                  
  return f
  
def plot_wshd_activation():
  elderdv = (precip_2017['precip'].cumsum()-
         elder_q_2017['runoff'].cumsum() - 
         elder_pet_2017['pet'].cumsum()
         )