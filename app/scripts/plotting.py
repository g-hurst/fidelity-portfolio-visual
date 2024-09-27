import plotly.graph_objects as go
import pandas as pd

def get_sankey_data(df:pd.DataFrame, excluded_accts:list=None):
    if excluded_accts:
        df = df[~df['Account Name'].isin(excluded_accts)]
    
    sources = []
    targets = []
    values  = []
    labels  = list(df['Account Name'].unique()) 
    labels += list(df['Category'].unique())
    labels += list(df['Sector'])
    labels += list(df['Symbol'])

    # map accounts to category
    for (acct, cat, val) in df[['Account Name', 'Category', 'Current Value']].itertuples(index=False):
        sources.append(labels.index(acct))
        targets.append(labels.index(cat))
        values.append(val)
    # map stock category to sectors
    for (sect, val) in df[df['Category'] == 'Stock'][['Sector', 'Current Value']].itertuples(index=False):
        sources.append(labels.index('Stock'))
        targets.append(labels.index(sect))
        values.append(val)
    # map sectors to stocks
    for (sect, sym, val) in df[df['Category'] == 'Stock'][['Sector', 'Symbol', 'Current Value']].itertuples(index=False):
        sources.append(labels.index(sect))
        targets.append(labels.index(sym))
        values.append(val)
    # map non-stocks to symbols
    for (cat, sym, val) in df[df['Category'] != 'Stock'][['Category', 'Symbol', 'Current Value']].itertuples(index=False):
        sources.append(labels.index(cat))
        targets.append(labels.index(sym))
        values.append(val)

    plot = go.Sankey(
        node = dict(
        pad       = 100,
        thickness = 20,
        line  = dict(color = "black", width = 0.5),
        label = labels,
        color = "blue"
        ),
        link = dict(
        source = sources, 
        target = targets,
        value  = values
    ))

    return plot