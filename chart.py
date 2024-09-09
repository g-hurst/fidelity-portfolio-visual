import pandas as pd
import numpy as np

import re
import os
import datetime
from collections import OrderedDict

from plotting import (plot_stocks_gui, plot_sankey)

# TODO: make this more resilliant (will crash if no file is found, but I am currently lazy and accept this tech debt)
def load_portfolio(path:str) -> pd.DataFrame:
    match_str = r'Portfolio_Positions_([A-Z,a-z]{3,4}-\d{2}-\d{4})\.csv'
    files = os.listdir(path)
    dated_files = []
    for f in files:
        match = re.search(match_str, f)
        if match:
            date = datetime.datetime.strptime(match.group(1), '%b-%d-%Y')
            dated_files.append(
                (os.path.join(path, f), date)
            )
    dated_files.sort(key=lambda x: x[1], reverse=True)
    return pd.read_csv(dated_files[0][0])        

def load_sectors(path:str) -> pd.DataFrame:
    return pd.read_csv(path)

def get_investimet_type(symbol:str, df_sectors:pd.DataFrame) -> str:
    if symbol in ['Pending Activity']:
        return np.nan
    elif symbol in ['SPAXX**',]:
        return 'Cash'
    elif symbol in df_sectors['Symbol'].values:
        return 'Stock'
    elif (len(symbol)==5 and symbol[0]=='F' and symbol[-1]=='X'):
        return 'Fidelity Fund'
    else:
        return 'Other'


def select_positions(df:pd.DataFrame, exclude_cash:bool=True, exclude_funds:bool=False) -> dict:
    selection = df[['Symbol', 'Current Value', 'Category']]
    selection = selection.dropna()
    data = OrderedDict()
    for (symbol, val, cat) in selection.itertuples(index=False):
        if cat=='Stock' or (cat=='Cash' and not exclude_cash) or (cat=='Fund' and not exclude_funds):
            if data.get(symbol): data[symbol] += val
            else:                data[symbol]  = val

    return data

def get_sector(symbol, df_sectors):
    if symbol in df_sectors['Symbol'].values:
        return df_sectors[df_sectors['Symbol'] == symbol]['Sector'].values[0]
    else:
        return np.nan

def select_sectors(df:pd.DataFrame) -> dict:
    selection = df[['Current Value', 'Sector']]
    selection = selection.dropna()
    data = OrderedDict()
    for (val, sect) in selection.itertuples(index=False):
        if data.get(sect): data[sect] += val
        else:              data[sect]  = val
    return data


if __name__ == '__main__':
    # load stocks and sector mappings into data frames
    exports_path = 'portfolio_exports'   
    sectors_path = 'sectors/nasdaq_screener_1725826524142.csv'
    df_portfolio = load_portfolio(exports_path)
    df_sectors   = load_sectors(sectors_path)

    # Clean the data and add some columns to the df
    df_portfolio.drop(['Last Price Change',
                       'Today\'s Gain/Loss Dollar', 
                       'Today\'s Gain/Loss Percent',
                       'Total Gain/Loss Dollar', 
                       'Total Gain/Loss Percent',
                       'Percent Of Account', 
                       'Cost Basis Total', 
                       'Average Cost Basis', 
                       'Type'], axis=1, inplace=True)
    df_portfolio = df_portfolio[df_portfolio['Symbol'] != 'Pending Activity']
    df_portfolio = df_portfolio.dropna(subset=['Symbol'])
    df_portfolio['Current Value'] = df_portfolio['Current Value'].apply(lambda x: float(x.replace('$','')))
    df_portfolio['Category']      = df_portfolio['Symbol'].apply(lambda x: get_investimet_type(x, df_sectors))
    df_portfolio['Sector']        = df_portfolio['Symbol'].apply(lambda x: get_sector(x, df_sectors))
    
    print(df_portfolio)

    # create basic plot of just stocks and corresponding sectors
    stocks        = select_positions(df_portfolio, exclude_funds=True)
    stock_sectors = select_sectors(df_portfolio)
    plot_stocks_gui(stocks, stock_sectors)

    plot_sankey(df_portfolio)

    