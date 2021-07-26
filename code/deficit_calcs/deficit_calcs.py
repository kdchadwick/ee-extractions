import pandas as pd
import sys

def deficit_calcs(df, et_type, snow_correction = 'True', snow_frac = 10, single_site = 'False'):

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
    if single_site == 'False':
        if snow_correction == 'True':
            df['ET'] = df[et_type]
            df['No Snow ET'] = df[et_type]
            df.loc[df['modis_NDSI_Snow_Cover'] > snow_frac, 'No Snow ET'] = 0
            df['A_old'] = df['ET'] - df['prism_ppt']
            df['A_new'] = df['No Snow ET'] - df['prism_ppt']

            df['D_old'] = 0
            df['D_new'] = 0

            new_data = pd.DataFrame()
            for i in df['point'].unique():
                mid0 = df.loc[df['point'] == i]
                mid0 = mid0.reset_index(drop=True)
                mid0['A_cumulative_new'] = mid0['A_new'].cumsum()
                mid0['A_cumulative_old'] = mid0['A_old'].cumsum()

                for _i in range(mid0.shape[0]-1):
                    mid0.loc[_i+1, 'D_old'] = max((mid0.loc[_i+1, 'A_old'] + mid0.loc[_i, 'D_old']), 0)
                    mid0.loc[_i+1, 'D_new'] = max((mid0.loc[_i+1, 'A_new'] + mid0.loc[_i, 'D_new']), 0)

                new_data = new_data.append(mid0)

            return new_data
        else:
            #df['ET Type'] = df[et_type]
            df['No Snow ET'] = df[et_type]
            df['A_old'] = df['ET'] - df['prism_ppt']

            df['D_old'] = 0

            new_data = pd.DataFrame()
            for i in df['point'].unique():
                mid0 = df.loc[df['point'] == i]
                mid0 = mid0.reset_index(drop=True)
                mid0['A_cumulative_old'] = mid0['A_old'].cumsum()

                for _i in range(mid0.shape[0]-1):
                    mid0.loc[_i+1, 'D_old'] = max((mid0.loc[_i+1, 'A_old'] + mid0.loc[_i, 'D_old']), 0)

                new_data = new_data.append(mid0)
    else:
        if snow_correction == 'True':
            df = df[df[et_type].notna()]
            df['ET'] = df[et_type]
            df['No Snow ET'] = df[et_type]
            df.loc[df['modis_NDSI_Snow_Cover'] > snow_frac, 'No Snow ET'] = 0
            df['A_old'] = df['ET'] - df['prism_ppt']
            df['A_new'] = df['No Snow ET'] - df['prism_ppt']

            df['D_old'] = 0
            df['D_new'] = 0

            new_data = pd.DataFrame()
            mid0 = df.copy().reset_index(drop=True)
            mid0['A_cumulative_new'] = mid0['A_new'].cumsum()
            mid0['A_cumulative_old'] = mid0['A_old'].cumsum()

            for _i in range(mid0.shape[0]-1):
                mid0.loc[_i+1, 'D_old'] = max((mid0.loc[_i+1, 'A_old'] + mid0.loc[_i, 'D_old']), 0)
                mid0.loc[_i+1, 'D_new'] = max((mid0.loc[_i+1, 'A_new'] + mid0.loc[_i, 'D_new']), 0)

            new_data = mid0
            
        else:
            #df['ET Type'] = df[et_type]
            df['No Snow ET'] = df[et_type]
            df['A_old'] = df['ET'] - df['prism_ppt']

            df['D_old'] = 0

            new_data = pd.DataFrame()
            mid0 = df.copy().reset_index(drop=True)

            mid0['A_cumulative_old'] = mid0['A_old'].cumsum()

            for _i in range(mid0.shape[0]-1):
                mid0.loc[_i+1, 'D_old'] = max((mid0.loc[_i+1, 'A_old'] + mid0.loc[_i, 'D_old']), 0)
            new_data = mid0

    return new_data
        