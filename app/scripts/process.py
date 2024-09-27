import pandas as pd
import numpy as np
from scipy.optimize import minimize

import types
import re
import os
import datetime
from collections import OrderedDict
import json
import base64

def regex_match_name(f_name):
    match_str = r'Portfolio_Positions_([A-Z,a-z]{3,4}-\d{2}-\d{4})\.csv'
    return re.search(match_str, f_name)

def save_csv(content:str, exports_path:str, f_name:str):
    content_type, content_string = content.split(',')
    if ('text/csv' in content_type) and regex_match_name(f_name):
        content_string = base64.b64decode(content_string)
        path_out = os.path.join(exports_path, f_name)
        with open(path_out, 'w', encoding='utf-8') as f_out:
            f_out.write(content_string.decode('utf-8'))
        return True
    return False

def load_portfolio(path:str, f_name:str=None) -> pd.DataFrame:   
    if not os.path.exists(path):
        os.makedirs(path)
        return None 
    
    dated_files = []
    # get files and sort by date
    if f_name is None:
        files = os.listdir(path)
        for f in files:
            match = regex_match_name(f)
            if match:
                date = datetime.datetime.strptime(match.group(1), '%b-%d-%Y')
                dated_files.append(
                    (os.path.join(path, f), date)
                )
        dated_files.sort(key=lambda x: x[1], reverse=True)
    # get specified file from parameter if not None
    else:
        # sus tech debt things bcz lazy adding date here
        dated_files.append((os.path.join(path, f_name), None))

    # return a pandas dataframe of the most recent file
    if len(dated_files) > 0:
        return pd.read_csv(dated_files[0][0])  
    else:
        return None

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

# commented out for now in case needed later
# def select_positions(df:pd.DataFrame, exclude_cash:bool=True, category:str='All') -> dict:
#     selection = df[['Symbol', 'Current Value', 'Category']]
#     selection = selection.dropna()
#     data = OrderedDict()
#     for (symbol, val, cat) in selection.itertuples(index=False):
#         if exclude_cash and cat=='Cash':
#             continue
#         elif (category=='All') or (category==cat):
#             if data.get(symbol): data[symbol] += val
#             else:                data[symbol]  = val

#     return data

def get_sector(symbol, df_sectors):
    if symbol in df_sectors['Symbol'].values:
        return df_sectors[df_sectors['Symbol'] == symbol]['Sector'].values[0]
    else:
        return np.nan
    

# commented out for now in case needed later
# def select_sectors(df:pd.DataFrame) -> dict:
#     selection = df[['Current Value', 'Sector']]
#     selection = selection.dropna()
#     data = OrderedDict()
#     for (val, sect) in selection.itertuples(index=False):
#         if data.get(sect): data[sect] += val
#         else:              data[sect]  = val
#     return data

def make_dataframe(exports_path:str, f_name:str=None) -> pd.DataFrame:
    # load stocks and sector mappings into data frames  
    sectors_path = 'data/sectors/nasdaq_screener_1725826524142.csv'
    df_portfolio = load_portfolio(exports_path, f_name=f_name)
    if df_portfolio is not None:
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
    
    return df_portfolio

if __name__ == '__main__':
    df_portfolio = make_dataframe()
    
    watchlist_path = 'data/watchlist.json'
    if os.path.isfile(watchlist_path):
        # load watchlist data from json file
        with open(watchlist_path, 'r') as f:
            watchlist = json.load(f)      
        
        # calculate stock percentage of non-watchlist positions
        df_stocks = df_portfolio[df_portfolio['Category'] == 'Stock']
        watchlist['other'] = {
            'goal': 1 - sum([v['goal'] for v in watchlist.values()])
        }
        watchlist['other']['stocks'] =  list(set(df_stocks['Symbol'].unique()) - set(stock for v in watchlist.values() if v.get('stocks') for stock in v.get('stocks')))

        # update watchlist dict with actual-percentage of categories and 
        # the current value of each category
        stocks_value = df_stocks['Current Value'].sum()
        for cat, data in watchlist.items():
            data['value']  = df_stocks[df_stocks['Symbol'].isin(data['stocks'])]['Current Value'].sum()
            data['actual'] = data['value'] / stocks_value

        # define function to minimize solving for X
        def objective(X, watchlist):
            values      = np.zeros(len(watchlist))       
            total_value = 0
            P_goal      = np.zeros(len(watchlist))
            for i, data in enumerate(watchlist.values()):
                new_val = data['value'] + X[i]
                values[i] = new_val
                total_value += new_val
                P_goal[i] = data['goal']
            
            P_calc = values / total_value
            
            return np.linalg.norm(P_goal - P_calc, ord=1)

        # solve for minimium X in objective constrained to all elements in X > 0
        # update the watchlist dict once calulations are complete
        result = minimize(objective, np.zeros(len(watchlist)+1), args=(watchlist,),bounds=[(0, None)])
        for i, data in enumerate(watchlist.values()):
            data['add'] = result.x[i]

        # print current breakdown of portfolio funds based on categories
        for cat, data in watchlist.items():
            print(
                '{:<20} ({:6} %) {:8} + {:8} = {:8} ({:6} %)'.format(
                    cat, 
                    round(data['actual']*100, 2), 
                    round(data['value'], 2),
                    round(data['add'], 2),
                    round(data['add']+data['value'], 2),
                    round(data['goal']*100, 2)
                    )
            )
        
        # print a more in depth break based on individual stocks
        for cat, data in watchlist.items():
            print(f'\n{cat}:')
            for stock in sorted(data.get('stocks')):
                value = df_stocks[df_stocks['Symbol'] == stock]['Current Value'].sum()
                percentage = value / stocks_value
                print('  {:6} ${:7} ({} %) '.format(stock, round(value, 2), round(percentage*100, 2)))