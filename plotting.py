from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import plotly.graph_objects as go
import pandas as pd

def plot_stocks_gui(stocks, sectors):
    fig, (ax_pie,  ax_bar) = plt.subplots(1, 2)
    fig.suptitle(f'Fidelity Portfolio Breakdown (${round(sum(stocks.values()), 2)})')
    
    class PlotSort:
        is_alpha   = False
        is_numeric = False

        def __init__(self, stocks, sectors):
            self.stocks_numeric = {k:v for (k,v) in sorted(stocks.items(), key=lambda x:x[1])}
            self.stocks_alpha   = {k:v for (k,v) in sorted(stocks.items(), key=lambda x:x[0], reverse=True)}
            self.sectors_numeric = {k:v for (k,v) in sorted(sectors.items(), key=lambda x:x[1])}
            self.sectors_alpha   = {k:v for (k,v) in sorted(sectors.items(), key=lambda x:x[0], reverse=True)}
            self.total_value       = sum(stocks.values())
            self.update_plot(stocks, sectors)

        def alpha(self, event):
            if self.is_alpha:
                return  
            self.is_alpha   = True
            self.is_numeric = False
            self.update_plot(self.stocks_alpha, self.sectors_alpha)
        
        def numeric(self, event):
            if self.is_numeric:
                return  
            self.is_alpha   = False
            self.is_numeric = True
            self.update_plot(self.stocks_numeric, self.sectors_numeric)

        def update_plot(self, stocks, sectors):
            ax_pie.clear()
            ax_pie.pie(sectors.values(), labels=sectors.keys())
            ax_pie.set_title('Sectors of stocks')

            ax_bar.clear()
            ax_bar.barh(list(stocks.keys()), stocks.values())
            ax_bar.set_title('Stocks')
            ax_bar.set_xlabel('Value USD')
            ax_bar.set_ylabel('Ticker')
            for bar, val in zip(ax_bar.patches, stocks.values()):
                width  = bar.get_width()
                height = bar.get_height()
                x, y   = bar.get_xy()
                ax_bar.text(x+width+40,
                        y+height/2,
                        str(round(val/self.total_value*100, 2))+'%',
                        ha='center', 
                        va='center')
            plt.draw()
            plt.tight_layout()

    callback    = PlotSort(stocks, sectors)
    ax_aplha    = fig.add_axes([0.05, 0.05, 0.1, 0.075])
    ax_numeric  = fig.add_axes([0.16, 0.05, 0.1, 0.075])
    btn_alpha   = Button(ax_aplha, 'Alphabetical')
    btn_numeric = Button(ax_numeric, 'Numeric')
    btn_alpha.on_clicked(callback.alpha)
    btn_numeric.on_clicked(callback.numeric)

    plt.show()

def plot_sankey(df:pd.DataFrame, excluded_accts:list=None):
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

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad       = 15,
        thickness = 20,
        line  = dict(color = "black", width = 0.5),
        label = labels,
        color = "blue"
        ),
        link = dict(
        source = sources, 
        target = targets,
        value  = values
    ))])

    fig.update_layout(title_text="Portfolio breakdown", font_size=10)
    fig.show()