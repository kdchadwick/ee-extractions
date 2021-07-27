import numpy as np
from wtryear_cum import wtryear_cum

def process_timeseries(data, interp = 'True', cumulative = True, single_site = False, out_dir=np.nan):
    df = data.copy()
    if 'point' not in df.columns: df['point']=out_dir
    for i in df['point'].unique():
        temp = df[df['point'] == i]
        temp = temp.interpolate(method='linear', limit = 16, limit_direction='both', limit_area='inside')
        df[df['point'] == i] = temp     

    if 'pml_Ec' in df.columns:
        if 'pml_ET_Ei' not in df.columns:
            # calculate ET and ET+interception
            df['pml_ET'] = (df['pml_Ec'] + df['pml_Es'])
            df['pml_ET_Ei'] = (df['pml_Ec'] + df['pml_Es'] + df['pml_Ei'])

    if 'modis_ET' in df.columns:
        df['modis_ET'] = df['modis_ET'] / 80 # 8 day sum, scale = 0.1
        df['modis_PET'] = df['modis_PET'] / 80 # 8 day sum, scale = 0.1
            
    if cumulative == True:
        df = wtryear_cum(df, single_site = single_site)
    return df
