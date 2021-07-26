import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
matplotlib.rcParams.update(matplotlib.rcParamsDefault)


#matplotlib.rcParams['pdf.fonttype'] = 42
#matplotlib.rcParams['ps.fonttype'] = 42

################## ERICA PLOTS ##################

def single_site_fig(data, data_modis, show_modis = False, ppt = 'cum_prism_ppt', et_1 = 'cum_pml_ET', et_2 = 'cum_modis_ET', directory_name = np.nan):
   # site_names = data['point'].unique()
   # num_of_sites = len(site_names)
    fig, ax = plt.subplots(nrows=1,ncols=1, sharex = True, figsize = (20,20), dpi = 300)
    #ax = ax.flatten()

   # for i in range(num_of_sites):
        
    gs = gridspec.GridSpec(1, 1) #these need to match subplots above

    ax = plt.subplot(gs[0])
    axMain = ax
    plt.sca(axMain) #sca = set current axes

    #all the axes
    divider = make_axes_locatable(axMain)
    axShallow = divider.append_axes("top", size="50%", pad=0.3, sharex=axMain) #middle, needs to have cf = in front
    ##axShallow2 = divider.append_axes("top", size="80%", pad=0.1, sharex=axMain) #top
    #axMain is the bottom
    
    plot_data = data.copy()

    # DEFICITS
    axMain.plot(plot_data['id'], plot_data['D_new'], '-',color='#ED9935', label='PML')
    
    # CUMULATIVE ET & PRECIP
    axShallow.fill_between(plot_data['id'], 0, plot_data[ppt],color='#b1d6f0', label='Precipitation (mm)')
    cf = axShallow.plot(plot_data['id'], plot_data[et_1],'--',color='#ED9935', alpha = 0.8)

    if show_modis == 'True':
        plot_modis = data_modis.copy()
        # DEFICIT
        axMain.plot(plot_modis['id'], plot_modis['D_new'], '-',color='#612fa3', label='MODIS')
        # CUMULATIVE ET
        axShallow.plot(plot_modis['id'], plot_modis[et_2],'--',color='#612fa3', alpha = 0.8)

    # Set labels
    ##axShallow.set_xticklabels([])
    #axShallow2.set_xticklabels([])
    axMain.legend(loc='best')
    axShallow.set_title(directory_name)
    
    # Y axis labels
    axShallow.set_ylabel('P and ET (mm)')
    axMain.set_ylabel('Deficit (mm)')

    return fig

def simple_multi_site_fig(data):
    site_names = data['point'].unique()
    num_of_sites = len(site_names)
    fig, ax = plt.subplots(nrows=4,ncols=3, sharex = True, figsize = (20,20), dpi = 300)
    ax = ax.flatten()
    for i in range(num_of_sites):
        plot_data = data[data['point'] == site_names[i]]
        ax[i].plot(plot_data['id'], plot_data['D_new'], '-', color='#ED9935')#, label='MODIS 10x10')
        ax[i].set_ylabel('Deficit (mm)')
        ax[i].set_title(site_names[i])
       # ax[i].xticks(rotation = 'vertical')
    ax[2].legend()
    #ax[i].set_ylim(0,1000)
    return fig


def facet_cum_multisite_fig(data, data_modis, show_modis = False, ppt = 'cum_prism_ppt', et_1 = 'cum_pml_ET', et_2 = 'cum_modis_ET'):
    site_names = data['point'].unique()
    num_of_sites = len(site_names)
    fig, ax = plt.subplots(nrows=4,ncols=3, sharex = True, figsize = (20,20), dpi = 300)
    ax = ax.flatten()

    for i in range(num_of_sites):
        
        gs = gridspec.GridSpec(4, 3) #these need to match subplots above

        ax[i] = plt.subplot(gs[i])
        axMain = ax[i]
        plt.sca(axMain) #sca = set current axes

        #all the axes
        divider = make_axes_locatable(axMain)
        axShallow = divider.append_axes("top", size="50%", pad=0.3, sharex=axMain) #middle, needs to have cf = in front
        ##axShallow2 = divider.append_axes("top", size="80%", pad=0.1, sharex=axMain) #top
        #axMain is the bottom
        
        plot_data = data[data['point'] == site_names[i]]

        # DEFICITS
        axMain.plot(plot_data['id'], plot_data['D_new'], '-',color='#ED9935', label='PML')
        
        # CUMULATIVE ET & PRECIP
        axShallow.fill_between(plot_data['id'], 0, plot_data[ppt],color='#b1d6f0', label='Precipitation (mm)')
        cf = axShallow.plot(plot_data['id'], plot_data[et_1],'--',color='#ED9935', alpha = 0.8)
 
        if show_modis == 'True':
            plot_modis = data_modis[data_modis['point'] == site_names[i]]
            # DEFICIT
            axMain.plot(plot_modis['id'], plot_modis['D_new'], '-',color='#612fa3', label='MODIS')
            # CUMULATIVE ET
            axShallow.plot(plot_modis['id'], plot_modis[et_2],'--',color='#612fa3', alpha = 0.8)
            axShallow.fill_between(plot_modis['id'], 0, plot_modis[ppt],color='#b1d6f0', label='Precipitation (mm)')

        # Set labels
        axShallow.set_xticklabels([])
        #axShallow2.set_xticklabels([])

        axShallow.set_title(site_names[i])
        
        # Y axis labels
        axShallow.set_ylabel('P and ET (mm)')
        axMain.set_ylabel('Deficit (mm)')

    return fig


################## DANA PLOTS ##################


def multi_site_plotting_fig(data, start_year = 2003, end_year = 2017):
    
    points_plotting = data['point'].unique()
    titles = points_plotting #maybe this could change at some point
    
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
        
    return fig
    #plt.savefig(file_name, bbox_inches='tight')
