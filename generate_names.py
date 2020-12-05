#!/usr/bin/env python3

import numpy as np
import pandas as pd

from utils import *


def slice_names(df, gender=None, first_letter=None, rank_lower_bound=None,
                rank_upper_bound=None, year_start=None, year_end=None,
                strict_rank_criteria=False):
    """
    Description:
        Slices data to conforms to the user's desired criteria.

    Arguments:
        df: pandas dataframe of SSA baby name data

    Keyword arguments:
        gender: gender to restrict results to
        first_letter: restrict names to first letter (list of str or str)
        rank_lower_bound: lowest rank of names to consider
        rank_upper_bound: highest rank of names to consider
        year_start: first year to consider
        year_end: last year to consider
        strict_rank_criteria: reject name if rank criteria not satisified
            across all years in consideration (boolean)

    Returns:
        sliced dataframe
    """
    # ERROR check
    if not isinstance(df, pd.DataFrame):
        print('ERROR: 1st argument must be a pandas dataframe.')
        return
    if gender is not None and gender != 'M' and gender != 'F':
        print('ERROR: There are only two genders: M and F.')
        return
    if (year_start is not None and year_end is not None
        and year_start > year_end):
        print('WARNING: Starting year is after ending year, swapping values.')
        temp = year_end
        year_end = year_start
        year_start = temp
    if (rank_lower_bound is not None and rank_upper_bound is not None
        and rank_lower_bound < rank_upper_bound):
        print('WARNING: Rank lower bound is higher than upper bound, '
              'swapping values.')
        temp = rank_lower_bound
        rank_lower_bound = rank_upper_bound
        rank_upper_bound = temp
    # Enforce first_letter being list
    if first_letter is not None:
        first_letter = list(first_letter)
    # slice by gender
    if gender is not None:
        df = df[df['gender']==gender]
    # slice by years
    if year_start is not None:
        df = df[df['year'].dt.year>=year_start]
    if year_end is not None:
        df = df[df['year'].dt.year<=year_end]
    # slice by first letter
    if first_letter is not None:
        df = df[df['name'].astype(str).str[0].isin(first_letter)]
    # slice by rank (Rank 1 is HIGHER than Rank 500, i.e., 1 > 500)
    if rank_lower_bound is not None:
        if strict_rank_criteria:
            temp = df.copy()
            df = df[df['rank']<=rank_lower_bound]
            temp = temp[temp['rank']>rank_lower_bound]
            intersection = np.intersect1d(df['name'].values,temp['name'].values)
            df = df[~df['name'].isin(intersection)]
        else:
            df = df[df['rank']<=rank_lower_bound]
    if rank_upper_bound is not None:
        if strict_rank_criteria:
            temp = df.copy()
            df = df[df['rank']>=rank_upper_bound]
            temp = temp[temp['rank']<rank_upper_bound]
            intersection = np.intersect1d(df['name'].values,temp['name'].values)
            df = df[~df['name'].isin(intersection)]
        else:
            df = df[df['rank']>=rank_upper_bound]
    return df


def generate_names(df, n=None, pout=False, gender=None, first_letter=None,
                   rank_lower_bound=None, rank_upper_bound=None,
                   year_start=None, year_end=None, strict_rank_criteria=False):
    """
    Description:
        Generates names that conforms to the user's desired criteria. Can
        return all matches or randomly draw from sample.

    Arguments:
        df: pandas dataframe of SSA baby name data

    Keyword arguments:
        n: number of random draws (Default: report all matches)
        pout: print out names in a textwrap environment
        gender: gender to restrict results to
        first_letter: restrict names to first letter (list of str or str)
        rank_lower_bound: lowest rank of names to consider
        rank_upper_bound: highest rank of names to consider
        year_start: first year to consider
        year_end: last year to consider
        strict_rank_criteria: reject name if rank criteria not satisified
            across all years in consideration (boolean)

    Returns:
        array of names that satisfy criteria
    """
    df = slice_names(df, gender=gender, first_letter=first_letter,
                     rank_lower_bound=rank_lower_bound,
                     rank_upper_bound=rank_upper_bound,
                     year_start=year_start, year_end=year_end,
                     strict_rank_criteria=strict_rank_criteria)
    if n is not None:
        # Drop duplicates as to not weight by popularity over the years
        names = df.drop_duplicates(subset=['name'])['name'].sample(n=n).values
    else:
        names = np.sort(df['name'].unique())
    names = np.sort(names)
    if pout:
        wraprint(', '.join(names))
    return names