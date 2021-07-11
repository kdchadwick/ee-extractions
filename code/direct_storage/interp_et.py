# interpolate with built in functionality for prism and modis so we dont mess it up ever again
import pandas as pd
import numpy as np

def interp_et(df):
    if 'pml_Ec' in df.columns:

        # calculate ET and ET+interception and x8
        df['pml_ET'] = (df['pml_Ec'] + df['pml_Es'])
        df['pml_ET_Ei'] = (df['pml_Ec'] + df['pml_Es'] + df['pml_Ei'])

        # interp them
        df['pml_ET'] = df['pml_ET'].interpolate()
        df['pml_ET_Ei'] = df['pml_ET_Ei'].interpolate()

    if 'modis_ET' in df.columns:
        df['modis_ET'] = df['modis_ET'].interpolate() / 8
        df['modis_PET'] = df['modis_PET'].interpolate() /8


    return df
