#!/usr/bin/env python

import matplotlib.pyplot as plt

child_gender_dict = {'M':'Boy', 'F':'Girl'}

def history_plot(ax, names, genders, df, plot_type='f', log_scale=True,
                 ts_min=None, ts_max=None, legend=True, **plot_kwargs):
    """
    Description:
        Makes a history plot of the data of the given names and their
        genders. (Not fully fleshed out, worked best for national data)
    
    Arguments:
        ax: ax that is plotted to
        names: list of names to plot data for
        genders: list of gender of name (must match len of names)
        df: dataframe from which data is extracted from
        
    Keyword arguments:
        plot_type: column of dataframe to be plotted as a function of time
        logscale: if y-axis is on a log scale (boolean)
        ts_min: timestamp min of x-scale (string, e.g., '1960')
        ts_max: timestamp max of x-scale (string, e.g., '2010')
        legend: if ax should display its legend (boolean)
        plot_kwargs: keyword arguments that are passed to ax.plot
        
    Returns:
        Nothing
    """
    for i, (gender, name) in enumerate(zip(genders, names)):
        data = df.loc[(df['name'] == name) & (df['gender'] == gender)]
        p = ax.plot(data['year'], data[plot_type],
                    label='{:s} ({:s})'.format(name, gender), **plot_kwargs)
    if legend:
        ax.legend()
    if log_scale:
        ax.set_yscale('log')
    if ts_min is not None and ts_max is not None:
        ax.set_xlim([pd.Timestamp(ts_min), pd.Timestamp(ts_max)])
    if plot_type == 'f':
        ax.set_ylabel('Gender name fraction')
    elif plot_type == 'n':
        ax.set_ylabel('Number of occurrences')
    elif plot_type == 'rank':
        ax.set_ylabel('Gender rank of name')
    else:
        print('Please set your own y-label')
    ax.set_xlabel('Year')
    return