import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
