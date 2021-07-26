import numpy as np
import pandas as pd

def wtryear_cum(df, et_1 = 'pml_ET', et_2 = 'modis_ET', ppt = 'prism_ppt', q = 'q_mm', single_site = 'False'):
    df = df.set_index(pd.to_datetime(df['id']))
    df['wateryear'] = np.where(~df.index.month.isin([10,11,12]),df.index.year,df.index.year+1)
    
    if single_site == 'False':
        if et_1 != np.nan:
            df['cum_'+ et_1] = df.groupby(['wateryear', 'point'])[et_1].cumsum()
        if et_2 != np.nan:
            df['cum_'+ et_2] = df.groupby(['wateryear', 'point'])[et_2].cumsum()
        if ppt != np.nan:
            df['cum_'+ ppt] = df.groupby(['wateryear', 'point'])[ppt].cumsum()
        if q != np.nan:
            df['cum_'+ q] = df.groupby(['wateryear', 'point'])[q].cumsum()
        
    else:
        if et_1 != np.nan:
            df['cum_'+ et_1] = df.groupby(['wateryear'])[et_1].cumsum()
        if et_2 != np.nan:
            df['cum_'+ et_2] = df.groupby(['wateryear'])[et_2].cumsum()
        if ppt != np.nan:
            df['cum_'+ ppt] = df.groupby(['wateryear'])[ppt].cumsum()
        if q != np.nan:
            df['cum_'+ q] = df.groupby(['wateryear'])[q].cumsum()
        
    return df
