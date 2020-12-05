#!/usr/bin/env python

import io
import os
import numpy as np
import pandas as pd
from zipfile import ZipFile
from bs4 import BeautifulSoup

from utils import *


# Vanity dictionary for converting SSA table headers
_my_header_dict = {
    'Year of birth': 'year',
    'Male': 'male',
    'Female': 'female',
    'Total': 'total'
}

_gender_dict = {
    'M' : 'male',
    'F' : 'female'
}


class ssa_data:
    """
    Description:
        A class containing functions for fetching, saving, and loading the
        data on first names provided by the SSA (social security
        administration). When called returns an object that has all the data
        loaded into pandas dataframes.
    
    Keyword arguements:
        data_folder: directory where data is stored
        total_file: parquest file name of total dataframe
        national_file: parquest file name of national dataframe
        state_file: parquest file name of state dataframe
        
    Attributes:
        totals: dataframe of totals
        national: dataframe of naitonal data
        state: dataframe of state data
    """
    def __init__(self, data_folder = 'data/',
                 total_file='birth_totals.parquet',
                 national_file='birth_US_national.parquet',
                 state_file='birth_US_state.parquet'):
        self._ssa_url = 'https://www.ssa.gov/oact/babynames/'
        self._totals_url = self._ssa_url+'numberUSbirths.html'
        self._natioanl_url = self._ssa_url+'names.zip'
        self._state_url = self._ssa_url+'state/namesbystate.zip'
        # check that data_folder exist, if not create it
        if not os.path.exists(data_folder):
            os.makedirs(data_folder, exist_ok=True)
        # file paths
        self.total_path = data_folder+total_file
        self.national_path = data_folder+national_file
        self.state_path = data_folder+state_file
        # fetch and set US annual birth totals
        self.fetch_US_birth_totals(header_dict=_my_header_dict)
        self.totals = pd.read_parquet(self.total_path)
        # fetch and set US first-name totals at the national level
        self.fetch_US_birth_national()
        self.national = pd.read_parquet(self.national_path)
        # fetch and set US first-name totals at the state level
        self.fetch_US_birth_state()
        self.state = pd.read_parquet(self.state_path)
        return
    

    def fetch_US_birth_totals(self, header_dict={}, update=False):
        """
        Description:
            Scraps the SSA table of total births in US proper (not including
            territories). Saves the data as a parquet file, broken down by
            year and gender.
            
        Keyword arguments:
            header_dict: dictionary to convert SSA table headers
            update: if we should update data even if it exist (boolean)
            
        Returns:
            Nothing (but saves dataframe parquet file in data/ by default)
        """
        if not update and os.path.isfile(self.total_path):
            return
        print('Fetching totals by year of US baby names')
        soup = BeautifulSoup(_request_content(self._totals_url), 'html.parser')
        header = [header_dict.get(h.text.strip(), h.text.strip())
                  for h in soup.find_all('th')]
        data = [[int(td.text.strip().replace(',', ''))
                 for td in tr.find_all('td')]
                for i, tr in enumerate(soup.find_all('tr')) if i != 0]
        df = pd.DataFrame(data, columns=header)
        year_str = header_dict.get('Year of birth', 'Year of birth')
        df[year_str] = pd.to_datetime(df[year_str], format='%Y')
        return df.to_parquet(self.total_path)
    

    def fetch_US_birth_national(self, update=False):
        """
        Description:
            Downloads the data from the SSA about first name assigned at
            birth in US proper (not including territories). Saves the data
            to a parquet file. Contains the number of occurances (n),
            fraction of that gender ('f'), popularity rank ('rank') for each
            name broken down by year and gender.
            
        Keyword arguments:
            update: if we should update data even if it exist (boolean)
            
        Returns:
            Nothing (but saves dataframe parquet file in data/ by default)
        """
        if not update and os.path.isfile(self.national_path):
            return
        print('Fetching national level data of US baby names')
        buffer = io.BytesIO(_request_content(self._natioanl_url))
        files_ = ZipFile(buffer).namelist()
        data = []
        for file_ in files_:
            if file_[0:3] == 'yob' and file_[-4:] == '.txt': 
                year = file_[3:7]
                year_totals = self.totals.loc[self.totals['year']==year]
                df = pd.read_csv(io.BytesIO(ZipFile(buffer).read(file_)),
                                 index_col=None, header=0,
                                 names=['name', 'gender', 'n']
                                ).assign(year=year)
                for gender in ['M', 'F']:
                    df_gender = df.loc[df['gender']==gender]
                    yearly_total = year_totals[_gender_dict[gender]].values[0]
                    df_gender = df_gender.assign(
                        f = df_gender['n']/yearly_total,
                        rank = df_gender['n'].rank(method='min',
                                                   ascending=False)
                    )
                    data.append(df_gender)
            else:
                print('  Extracting: {:s}'.format(file_))
                ZipFile(buffer).extract(file_, path='data/') 
        data_stack = np.vstack(data)
        df = pd.DataFrame(data_stack,
                          columns=['name', 'gender', 'n', 'year', 'f', 'rank'])
        df['year'] = pd.to_datetime(df['year'], format='%Y')
        return df.to_parquet(self.national_path)


    def fetch_US_birth_state(self, update=False):
        """
        Description:
            Downloads the data from the SSA about first name assigned at
            birth in US proper (not including territories). Saves the data
            to a parquet file. Contains the number of occurances (n),
            fraction of that gender ('f'), popularity rank ('rank') for each
            name broken down by year, gender, and state.
            
        Keyword arguments:
            update: if we should update data even if it exist (boolean)
            
        Notes:
            ^The fraction ('f') is not 100% accurate as it does not use the
             total births in a given state as the demoniator. Instead we use
             the total number of names recorded by the SSA and released to
             the public. As thee SSA does not release information on
             children whose name had less than five occurances, we are under
             counting the total births. This is not a completely neglible
             amount. For example, in 2000 for males there are 1963202 boys
             accounted for in the national name data, while the totals data
             states there were 2097629 boys born in 2000. That means that
             ~6% of boys are unaccounted for in the national data! In the
             same year ~10% of girls are unaccounted for. This is a randomly
             selected example and may not even be the worse year. In general
             girls have more unquie names and thus are more unaccounted for.
            
        Returns:
            Nothing (but saves dataframe parquet file in data/ by default)
        """
        if not update and os.path.isfile(self.state_path):
            return
        print('Fetching state level data of US baby names')
        buffer = io.BytesIO(_request_content(self._state_url))
        files_ = ZipFile(buffer).namelist()
        data = []
        for file_ in files_:
            if len(file_) == 6 and file_[-4:] == '.TXT': 
                state = file_[0:2]
                df = pd.read_csv(io.BytesIO(ZipFile(buffer).read(file_)),
                                 index_col=None, header=0,
                                 names=['state', 'gender', 'year', 'name', 'n'])
                for gender in ['M', 'F']:
                    for year in df['year'].unique():
                        df_gender_year = df.loc[(df['gender']==gender) &
                                                (df['year']==year)]
                        # This is not 100% accurate, but close enough guess as
                        # we lack total state births (we undercount births)
                        gender_year_total = df_gender_year['n'].sum()
                        df_gender_year = df_gender_year.assign(
                            f = df_gender_year['n']/gender_year_total,
                            rank = (df_gender_year['n'].rank(method='min',
                                                             ascending=False))
                        )
                        data.append(df_gender_year)
            else:
                print('  Extracting: {:s}'.format(file_))
                ZipFile(buffer).extract(file_, path='data/') 
        data_stack = np.vstack(data)
        df = pd.DataFrame(data_stack,
                          columns=['state', 'gender', 'year',
                                   'name', 'n', 'f', 'rank'])
        df['year'] = pd.to_datetime(df['year'], format='%Y')
        return df.to_parquet(self.state_path)