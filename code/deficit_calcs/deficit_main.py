# importing
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import glob
import os
import json
import sys
import argparse
import subprocess


from process_timeseries import process_timeseries
import deficit_plots as plot
from deficit_calcs import deficit_calcs

# Set plotting parameters
plt.rcParams.update({'font.size': 20})
plt.rcParams['font.family'] = "serif"
plt.rcParams['font.serif'] = "Times New Roman"
plt.rcParams['axes.grid'] = False
plt.rcParams['axes.axisbelow'] = True
plt.rcParams['axes.labelpad'] = 6


def main():
    
    ################## PARSE ARGS AND DIRECTORIES ##################
    parser = argparse.ArgumentParser('Calculate deficit using method from Dralle et al., 2020; McCormick et al., 2021')
    parser.add_argument('input_timeseries_csv', type=str)
    parser.add_argument('output_directory', type=str)
    parser.add_argument('-new_directory', type=str, default='False')
    parser.add_argument('-interpolate', type=str, default='True')
    parser.add_argument('-xtra_imports', type=str, default='False')
    parser.add_argument('-snow_correction', type=str, default = 'True')
    parser.add_argument('-snow_frac', type=int, default = 10)

    print('\n \ndeficit_main.py is parsing and cleaning arguments')
    args = parser.parse_args()

    if args.new_directory.lower() == 'true':
        print('\nChecking and generating output directory')
        if os.path.isdir(args.output_directory) == True:
            print('\nWARNING: User specified to make new directory, but one already exists. \nExiting... \n \n \n')
            sys.exit()
        else:
            subprocess.call('mkdir ' + os.path.join(args.output_directory), shell=True)
            
    elif args.new_directory.lower() == 'false':
        if os.path.isdir(args.output_directory) == False:
            print('\nWARNING: User specified directory exists, but it does not. \nExiting...\n \n \n')
            sys.exit()
            
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'deficit'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'deficit', 'settings'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'deficit', 'exports'), shell=True)
    subprocess.call('mkdir ' + os.path.join(args.output_directory, 'deficit', 'figs'), shell=True)

    print('\nSaving inputs and args to settings folder in {}'.format(args.output_directory))
    with open(os.path.join(args.output_directory, 'deficit','settings', 'input_args.txt'), 'w') as f:
        json.dump(args.__dict__, f, indent=2)


    ################## BEGIN DATA IMPORT, CLEANING, & CALCS ##################
    
    # Import Data
    if args.xtra_imports.lower() == 'false':
        data = pd.read_csv(args.input_timeseries_csv)
        data.drop(columns=["Unnamed: 0"], inplace=True)
        data['id'] = pd.to_datetime(data['id'])
        data.to_csv(os.path.join(args.output_directory, 'deficit','settings', 'original_timeseries.csv'), mode='a', header=True)

    else:
        # Put something here eventually to pull csv with local et/ppt data?
        print('\nAnalyses not yet compatible with multiple input files.\n\n\nExiting...')
        sys.exit()

    if args.snow_correction.lower() == 'true':
        if 'modis_NDSI_Snow_Cover' not in data.columns:
            print('\nUser specified to use snow correction, but no snow data is provided.\n\nExiting...')
            sys.exit()
    
    # Interpolate Data & get ET columns for MODIS and PML
    df = process_timeseries(data, interp = 'True')
    df.to_csv(os.path.join(args.output_directory, 'deficit','exports', 'post_processed_timeseries.csv'), mode='a', header=True)
    print('\nTimeseries post-processing complete. Deficit being calculated...')
    
    # Calculate deficit
    #df_modis = deficit_calcs(df, et_type = 'modis_ET', snow_correction = args.snow_correction, snow_frac = args.snow_frac)
    df_pml = deficit_calcs(df, et_type = 'pml_ET', snow_correction = args.snow_correction, snow_frac = args.snow_frac)
    print('\nCalculation complete.')
    
    # Plotting
    print('Saving figures to {}'.format(args.output_directory))
    fig = plot.simple_multi_site_fig(df_pml)
    fig.savefig(os.path.join(args.output_directory, 'deficit','figs', 'simple_multisite.png'))

    fig = plot.facet_multi_site_fig(df_pml)
    fig.savefig(os.path.join(args.output_directory, 'deficit','figs', 'facet_multisite.png'))

    
    '''
    ################## ORIGINAL VERSION ##################
    data, interpolated_data = import_data()
    #print(list(data.columns))

    plotting_base_data(data=data, colors=['blue', 'green', 'darkorange', 'red', 'purple'])

    #data_w_calcs = deficit_calcs(data=merged_interpolated_data, snow_frac=10)

    #multi_site_plotting_fig(data=data_w_calcs, file_name='figs/comparison_fig_20201106_2row.png',
    #                        titles=['High Snow Location', 'Low Snow Location'],
    #                        points_plotting=[0, 1], start_year=2013, end_year=2017)


def import_data():
    data = pd.read_csv("exports/test.csv")
    data.drop(columns=["Unnamed: 0"], inplace=True)
    # modis = pd.read_csv("data/modis_gee_export.csv")
    # modis.drop(columns=["Unnamed: 0"], inplace=True)
    # data = pd.merge(clim, modis, how='left', on=['id', 'point'])
    data['id'] = pd.to_datetime(data['id'])
    # data['modis_ET'] = data['modis_ET']/8
    # data['modis_PET'] = data['modis_PET']/8

    # All data columns to keep
    # merged_interpolated_data = data[['id', 'point', 'prism_ppt', 'prism_tdmean', 'prism_tmax', 'prism_tmean',
    #                                 'prism_tmin', 'prism_vpdmax', 'prism_vpdmin', 'pml_Ec', 'pml_Ei', 'pml_Es',
    #                                 'pml_GPP', 'pml_qc', 'snow_cover_modis_NDSI', 'snow_cover_modis_NDSI_Snow_Cover',
    #                                 'modis_ET', 'modis_LE', 'modis_PET', 'modis_PLE', 'modis_DayOfYear', 'modis_EVI',
    #                                  'modis_NDVI']]
    #
    # # Interpolating for all dates
    interpolated_data = data
    for i in interpolated_data['point'].unique():
        temp = interpolated_data[interpolated_data['point'] == i]
        temp = temp.interpolate(method='linear', limit_direction='both')
        interpolated_data[interpolated_data['point'] == i] = temp

    return data, interpolated_data


def deficit_calcs(data, snow_frac):
    data['ET'] = data['pml_Ec']+data['pml_Es']
    data['No Snow ET'] = data['ET']
    data.loc[data['snow_cover_modis_NDSI_Snow_Cover'] > snow_frac, 'No Snow ET'] = 0
    data['A_old'] = data['ET'] - data['prism_ppt']
    data['A_new'] = data['No Snow ET'] - data['prism_ppt']

    data['D_old'] = 0
    data['D_new'] = 0

    new_data = pd.DataFrame()
    for i in data['point'].unique():
        mid0 = data.loc[data['point'] == i]
        mid0 = mid0.reset_index(drop=True)
        mid0['A_cumulative_new'] = mid0['A_new'].cumsum()
        mid0['A_cumulative_old'] = mid0['A_old'].cumsum()

        for _i in range(mid0.shape[0]-1):
            mid0.loc[_i+1, 'D_old'] = max((mid0.loc[_i+1, 'A_old'] + mid0.loc[_i, 'D_old']), 0)
            mid0.loc[_i+1, 'D_new'] = max((mid0.loc[_i+1, 'A_new'] + mid0.loc[_i, 'D_new']), 0)

        new_data = new_data.append(mid0)

    return new_data

# plotting
def multi_site_plotting_fig(data, file_name, points_plotting, titles, start_year, end_year):

    # setting line widths for plots
    lw_old = 3

    # setting y limits for different plots - should probably be updated to manually set based on max values
    et_range = [-0.25, 4.75]
    a_range = [-100.25, 4.75]
    ac_range = [-7000, 500]
    d_range = [-50, 1200]
    p_range = [-5, 150]

    # Setting starting point of axes on the plots, this is for two sites
    sides = [0.0, 0.5]
    # row_fracs = [0.0, 0.25, 0.5, 0.75, 1]
    row_fracs = [0.0, 0.3, 0.6, 0.9]
    row_fracs = [0.0, 0.5]
    # this is for plotting three sites
    # sides = [0.0, 0.3, 0.6]

    width_frac = 0.85/len(points_plotting)
    height_frac = 0.45

    # Dealing with date tick marks
    # format the ticks

    data = data[(data['id'].dt.year >= start_year) & (data['id'].dt.year <= end_year)]

    fig = plt.figure(figsize=(12, 6))

    for i in range(len(points_plotting)):
        # selecting data for selected point
        plot_data = data.loc[data['point'] == points_plotting[i]]
        #
        # # adding precip plot
        ax = fig.add_axes([sides[i], row_fracs[0], width_frac, height_frac])
        ylims = et_range
        a = 1
        ax.plot(plot_data['id'], plot_data['ET'], linewidth=lw_old, color='dimgray',label='Old Method', zorder=1, alpha=a)
        ax.plot(plot_data['id'], plot_data['No Snow ET'], linewidth=1, color='black', label='New Method', zorder=4, alpha=a)
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.35, lw=0.1, colors='gray', zorder=0)
        # ylims = p_range
        # ax.plot(plot_data['id'], plot_data['prism_ppt'], linewidth=lw_old, color='blue')
        # ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
        #           alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        if i == 0:
            ax.set_ylabel('Evapotranspiration \n'+r'(F$_{in}$'+', mm/day)\n   ')
        # format the coords message box
        ax.format_xdata = mdates.DateFormatter('%Y-%m-%d')
        locs, labels = plt.xticks()
        locs = [loc for _loc, loc in enumerate(locs) if _loc % 2 == 0]
        plt.xticks(locs, rotation=40)


        # adding deficit axis
        ax = fig.add_axes([sides[i], row_fracs[1], width_frac, height_frac], xticklabels=[])
        ylims = d_range
        ax.plot(plot_data['id'], plot_data['D_old'], linewidth=lw_old, color='dimgray', label='Old Method')
        ax.plot(plot_data['id'], plot_data['D_new'], linewidth=1, color='black', label='New Method')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)

        if i == 0:
            ax.set_ylabel('Root zone storage deficit \n (D, mm)')
            ax.legend(loc='upper left', prop={'size': 12})
        ax.set_title(titles[i])

    plt.savefig(file_name, bbox_inches='tight')


# plotting extracted and calculated data from each site - individual plot for each.
# Not currently called in main()
def plotting_single_site_data(data):

    lw_new = 1
    lw_old = 3
    et_range = [-0.25, 4.1]
    t_range = [-5, 35]
    evi_range = [-.2,1]
    ndsi_range = [-0.5,1]
    s_range = [0, 100]
    a_range = [-50, 10]
    ac_range = [-6500, 500]
    d_range = [-50, 1200]
    p_range = [-5, 250]

    for i in data['point'].unique():
        plot_data = data.loc[data['point'] == i]
        fig = plt.figure(figsize=(30, 15))

        ax = fig.add_axes([.0, .0, .4, .16])
        ylims = p_range
        ax.plot(plot_data['id'], plot_data['prism_ppt'], linewidth=lw_old, color='blue')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(xlabel='Date', ylabel='Precip (mm)')

        ax = fig.add_axes([.0, .2, .4, .16])
        ylims = et_range
        ax.plot(plot_data['id'], plot_data['ET'], linewidth=lw_old, color='blue')
        ax.plot(plot_data['id'], plot_data['No Snow ET'], linewidth=lw_new, color='orange')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(ylabel='ET (mm)')

        ax = fig.add_axes([.0, .4, .4, .16], xticklabels=[])
        ylims = a_range
        ax.plot(plot_data['id'], plot_data['A_old'], linewidth=lw_old, color='blue')
        ax.plot(plot_data['id'], plot_data['A_new'], linewidth=lw_new, color='orange')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(ylabel="A (mm)")

        ax = fig.add_axes([.0, .6, .4, .16], xticklabels=[])
        ylims = ac_range
        ax.plot(plot_data['id'], plot_data['A_cumulative_old'], linewidth=lw_old, color='blue')
        ax.plot(plot_data['id'], plot_data['A_cumulative_new'], linewidth=lw_new, color='orange')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(ylabel="A cumulative")

        ax = fig.add_axes([.0, .8, .4, .16], xticklabels=[])
        ylims = d_range
        ax.plot(plot_data['id'], plot_data['D_old'], linewidth=lw_old, color='blue', label='Old Method')
        ax.plot(plot_data['id'], plot_data['D_new'], linewidth=lw_new, color='orange', label='New Method')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='D', title="Point_"+str(i))

        ax = fig.add_axes([.5, .0, .4, .16])
        ylims = s_range
        ax.plot(plot_data['id'], plot_data['snow_cover_modis_NDSI_Snow_Cover'], linewidth=lw_old, color='blue')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(xlabel='Date')
        ax.set(ylabel='Snow Cover %')

        ax = fig.add_axes([.5, .2, .4, .16])
        ylims = ndsi_range
        ax.plot(plot_data['id'], plot_data['snow_cover_modis_NDSI']/10000, linewidth=lw_old, color='red', label='MODIS')
        ax.plot(plot_data['id'], plot_data['snow_cover_landsat_NDSI'], linewidth=lw_old, color='green', label='Landsat')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='NDSI')

        ax = fig.add_axes([.5, .4, .4, .16], xticklabels=[])
        ylims = evi_range
        ax.plot(plot_data['id'], plot_data['landsat_EVI'], linewidth=lw_old, color='green')
        ax.plot(plot_data['id'], plot_data['modis_EVI']/10000, linewidth=lw_old, color='red')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.set_ylim(ylims)
        ax.set(ylabel='EVI')

        ax = fig.add_axes([.5, .6, .4, .16], xticklabels=[])
        ylims = t_range
        ax.plot(plot_data['id'], plot_data['prism_tmax'], linewidth=lw_old, color='red', label='max')
        ax.plot(plot_data['id'], plot_data['prism_tmin'], linewidth=lw_new, color='blue', label='min')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='Temp')
        ax.set_ylim(ylims)

        ax = fig.add_axes([.5, .8, .4, .16], xticklabels=[])
        ylims = et_range
        ax.plot(plot_data['id'], plot_data['pml_Ec'], linewidth=lw_old, color='green', label='Transpiration')
        ax.plot(plot_data['id'], plot_data['pml_Es'], linewidth=lw_old, color='brown', label='Evaporation')
        ax.vlines(plot_data.loc[plot_data['No Snow ET'] == 0]['id'], ylims[0], ylims[1],
                  alpha=0.5, lw=0.1, colors='gray', zorder=1)
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='E/T (mm)')

        plt.savefig('figs/et_wb_' + str(i) + '.png', bbox_inches='tight')


# plotting extracted data from each site - individual plot for each.
# Not currently called in main()
def plotting_base_data(data, colors):

    for _i in data['point'].unique():
        fig = plt.figure(figsize=(10, 10))
        plot_data = data.loc[data['point'] == _i]
        ax = fig.add_axes([.1, .0, .9, .2])
        ax.plot(plot_data['id'], plot_data['prism_ppt'], linewidth=1, color='blue')
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(xlabel='Date', ylabel='Precip (mm)')

        ax = fig.add_axes([.1, .25, .9, .2], xticklabels=[])
        ax.plot(plot_data['id'], plot_data['pml_Ec'], linewidth=1, color='green', label='Ec')
        ax.plot(plot_data['id'], (plot_data['pml_Es']), linewidth=1, color='brown', label='Es')
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel="Transpiration (mm)")

        ax = fig.add_axes([.1, .5, .9, .2], xticklabels=[])
        ax.plot(plot_data['id'], (plot_data['modis_EVI']/10000), linewidth=1, color='red', label='MODIS')
        ax.plot(plot_data['id'], (plot_data['landsat_EVI']), linewidth=1, color='blue', label='Landsat')
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='EVI (mm)')

        ax = fig.add_axes([.1, .75, .9, .2], xticklabels=[])
        ax.plot(plot_data['id'], plot_data['pml_GPP'], linewidth=1, color='black', label='PML')
        ax.plot(plot_data['id'], (plot_data['modis_Gpp_x']/100), linewidth=1, color='red', label='MODIS')
        ax.plot(plot_data['id'], (plot_data['landsat_GPP']/100), linewidth=1, color='blue', label='Landsat')
        ax.legend(loc='upper left', prop={'size': 12})
        ax.set(ylabel='GPP')

        plt.savefig('figs/Point'+_i+'_data_detail.png', bbox_inches='tight')


# For generating generic scatter plots,
# not currently called in main()
def scatters(data, x, y, labs, fname):
    fig = plt.figure(figsize=(6, 6))
    colors = ['blue', 'green', 'darkorange', 'red', 'purple']

    for _i in data['point'].unique():
        plot_data = data.loc[data['point'] == _i]
        ax = fig.add_axes([.0, .0, .9, .9])
        ax.scatter(plot_data[x], plot_data[y], color=colors[_i], s=40, alpha=.3)
        ax.set(xlabel=labs[0], ylabel=labs[1])

    plt.savefig('figs/'+fname+'.png', bbox_inches='tight')

'''
if __name__ == "__main__":
    main()
