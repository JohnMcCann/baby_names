#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt


cc = plt.rcParams["axes.prop_cycle"].by_key()["color"]
markers = ['o', 'v', '^', '<', '>', '8', 's', 'p', 'P', '*', 'h', 'H', 'X', 'D',
           'd', '.', '1', '2', '3', '4', '+', 'x']
child_gender_dict = {'M':'Boy', 'F':'Girl'}


def history_plot(ax, names, genders, df, plot_type='f', log_scale=True,
                 ts_min=None, ts_max=None, legend=True, highlight=None,
                 **plot_kwargs):
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
        highlight: names to highlight in plot (names)
        plot_kwargs: keyword arguments that are passed to ax.plot
        
    Returns:
        Nothing
    """
    # ERROR check
    if len(names) > len(cc)*len(markers):
        print('WARNNING: Number of names exceed unquie identifiers.')
    # Make plot
    for i, (gender, name) in enumerate(zip(genders, names)):
        # Loop through names and genders
        data = df.loc[(df['name'] == name) & (df['gender'] == gender)]
        # Fixup missing data
        dates = pd.date_range(start=data['year'].iloc[0].date(),
                              end=data['year'].iloc[-1].date(), freq='YS')
        s = pd.Series(index=dates, dtype=dates.dtype)
        data.set_index('year',inplace=True)
        data = pd.concat([data, s[~s.index.isin(data.index)]]).sort_index()
        data = data.drop([0], axis=1)
        data.loc[:, 'name'] = name
        data.loc[:, 'gender'] = gender
        data['year'] = data.index
        data.reset_index(inplace=True, drop=True)
        # Add name to plot
        if plot_type == 'rank':
            p = ax.plot(data['year'], data[plot_type], c=cc[i%len(cc)],
                        marker=markers[i//len(cc)],
                        label='{:s} ({:s})'.format(name, gender), **plot_kwargs)
            if highlight is not None and name in list(highlight):
                new_kwargs = {key: value
                              for key, value in plot_kwargs.items()
                              if (key != 'lw' and key != 'ms')}
                hlw = 4*p[0].get_linewidth()
                hms = 1.5*p[0].get_markersize()
                ax.plot(data['year'], data[plot_type], c=cc[(i-1)%len(cc)],
                        marker=markers[i//len(cc)], ms=hms, lw=hlw, zorder=0,
                        alpha=0.9, **new_kwargs)
        else:
            p = ax.plot(data['year'], data[plot_type],
                        label='{:s} ({:s})'.format(name, gender), **plot_kwargs)
    # Make legend
    if legend:
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -.225),
                  fancybox=False, shadow=False, ncol=min(4,len(names)))
    # Fixup x-axis
    ax.set_xlabel('Year')
    if ts_min is not None and ts_max is not None:
        ax.set_xlim([pd.Timestamp(ts_min), pd.Timestamp(ts_max)])
    fig = ax.get_figure()
    fig.autofmt_xdate()
    # Fixup y-axis
    if plot_type == 'f':
        ax.set_ylabel('Name fraction')
    elif plot_type == 'n':
        ax.set_ylabel('Number of occurrences')
    elif plot_type == 'rank':
        ax.set_ylabel('Name Rank')
    else:
        print('Please set your own y-label')
    if log_scale:
        ax.set_yscale('log')
    return