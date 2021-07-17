
from wtryear_cum import wtryear_cum

def process_timeseries(data, interp = 'True', cumulative = True):
    df = data.copy()
    if interp == 'True':
        for i in df['point'].unique():
            temp = df[df['point'] == i]
            temp = temp.interpolate(method='linear', limit_direction='both')
            df[df['point'] == i] = temp     

    if 'pml_Ec' in df.columns:
        if 'pml_ET_Ei' not in df.columns:
            # calculate ET and ET+interception and x8
            df['pml_ET'] = (df['pml_Ec'] + df['pml_Es'])
            df['pml_ET_Ei'] = (df['pml_Ec'] + df['pml_Es'] + df['pml_Ei'])

    if 'modis_ET' in df.columns:
        if 'modis_ET_x8' not in df.columns:
            df['modis_ET_x8'] = df['modis_ET'] / 8
            df['modis_PET_x8'] = df['modis_PET'] / 8
            
    if cumulative == True:
        df = wtryear_cum(df)
        
    return df
