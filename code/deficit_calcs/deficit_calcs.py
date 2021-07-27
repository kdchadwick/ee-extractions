import pandas as pd
import numpy as np
import sys

def deficit_calcs(df, et_type, snow_correction = 'True', snow_frac = 10, dir_name=np.nan):

    # Maybe someday we can have it calculate the deficit for all present ETs
    '''
    et_types = []
    if 'modis_ET' in df.columns:
        et_types = et_types.append('modis_ET')
    if 'pml_ET_Ei' in df.columns:
        et_types = et_types.append('pml_ET_Ei')
    if 'pml_ET' in df.columns:
        et_types = et_types.append('pml_ET')
    else:
        print('\nNo ET supplied.\n\nExiting...')
        sys.exit()
    '''       
    df['ET'] = df[et_type]
    if snow_correction == 'True': df.loc[df['modis_NDSI_Snow_Cover'] > snow_frac, 'ET'] = 0
    df['A'] = df['ET'] - df['prism_ppt']
    df['D'] = 0
    if 'q_mm' in df.columns: df['S'] = df['prism_ppt'] - df['ET'] - df['q_mm']
    if 'point' not in df.columns: df['point']=dir_name

    new_data = pd.DataFrame()

    for i in df['point'].unique():
        calcs = df.loc[df['point'] == i].reset_index(drop=True)
        if 'q_mm' in df.columns: 
            calcs['S_agg'] = calcs['S'].cumsum()
        
        for _i in range(calcs.shape[0]-1):
            calcs.loc[_i+1, 'D'] = max((calcs.loc[_i+1, 'A'] + calcs.loc[_i, 'D']), 0)

        new_data = new_data.append(calcs)



    return new_data
        