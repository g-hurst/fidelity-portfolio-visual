import pandas as pd
import re
import os
import datetime
from collections import OrderedDict

from plotting import plot_stocks_gui

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

def select_positions(df:pd.DataFrame, exclude_cash:bool=True, exclude_funds:bool=False) -> dict:
    def exclude_symbol(symbol):
        excludes = ['Pending Activity']
        if exclude_cash:
            excludes.append('SPAXX**')
        if exclude_funds and (len(symbol)==5 and symbol[0]=='F' and symbol[-1]=='X'):
                return True

        return symbol in excludes

    selection = df[['Symbol', 'Current Value']]
    selection = selection.dropna()
    data = OrderedDict()
    for (symbol, val) in selection.itertuples(index=False):
        if not exclude_symbol(symbol):
            val = float(val.replace('$',''))
            if data.get(symbol): data[symbol] += val
            else:                data[symbol]  = val

    return data

def map_to_sectors(positions:dict, df_sectors:pd.DataFrame) -> dict:
    data = OrderedDict()
    for symbol, val in positions.items():
        if symbol in df_sectors['Symbol'].values:
            sector = df_sectors[df_sectors['Symbol'] == symbol]['Sector'].values[0]
            if data.get(sector): data[sector] += val
            else:                data[sector]  = val
        else:
            print(f'error: no sector found for {symbol}')
    return data

if __name__ == '__main__':
    exports_path = 'portfolio_exports'   
    df_portfolio = load_portfolio(exports_path)

    sectors_path = 'sectors/nasdaq_screener_1725826524142.csv'
    df_sectors   = load_sectors(sectors_path)

    all_positions = select_positions(df_portfolio, exclude_funds=True)
    all_sectors  = map_to_sectors(all_positions, df_sectors)
    plot_stocks_gui(all_positions, all_sectors)
