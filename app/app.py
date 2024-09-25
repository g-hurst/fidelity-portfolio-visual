from dash import Dash, dcc, html, Input, Output
import plotly.express as px

from scripts.process import make_dataframe
from scripts.plotting import get_sankey_data


df_portfolio = make_dataframe()

pie_category_fig = px.pie(df_portfolio, names='Category', values='Current Value')
pie_category_fig.update_layout(
  title=f'Investment Categories',
)
pie_sector_fig = px.pie(df_portfolio[df_portfolio['Category'] == 'Stock'], names='Sector', values='Current Value')
pie_sector_fig.update_layout(
  title=f'Stock Sectors',
)
pie_account_fig = px.pie(df_portfolio, names='Account Name', values='Current Value')
pie_account_fig.update_layout(
  title=f'Account Breakdown',
)

app = Dash(__name__)
app.layout = html.Div(
  className='app',
  children=[
    html.H1(children='Fidelity Portfolio Visual'),
    html.Div(
      className='body',
      children=[
        html.Div(
          className='chart-card',
          children=[
            dcc.Graph(
              figure={
                  'data':[
                    get_sankey_data(df_portfolio, excluded_accts=['Cash Management (Individual - TOD)',]),
                    ],
                  "layout": {
                    "title": "Sankey Breakdown of Portfolio",
                    "height":800,
                    "width":800
                    },
                }
              )
          ],
        ),
        html.Div(
          className='chart-card',
          children=[
            html.Div(
              className='positions_bar-category-buttons',
              children=[
                dcc.Dropdown(
                    id="positions_bar-category-filter",
                    options=[
                        {"label": opt, "value": opt}
                        for opt in ['All', ] + list(df_portfolio['Category'].unique())
                    ],
                    value="All",
                    clearable=False,
                    className="positions_bar-dropdown",
                ),
                dcc.Dropdown(
                    id="positions_bar-sort-filter",
                    options=[
                        {"label":'Alphabetical', "value":'alpha'},
                        {"label":'Numerical', "value":'num'}
                    ],
                    value="alpha",
                    clearable=False,
                    className="positions_bar-dropdown",
                ),
              ]
            ),
            dcc.Graph(id='positions_bar'),
          ],
        )
      ],
    ),
    html.Div(
      className='body',
      children=[
        html.Div(
          className='pie-card',
          children=[
            dcc.Graph(              
              figure=pie_account_fig
              ),
          ],
        ),
        html.Div(
          className='pie-card',
          children=[
            dcc.Graph(              
              figure=pie_category_fig
              ),
          ],
        ),
        html.Div(
          className='pie-card',
          children=[
            dcc.Graph(              
              figure=pie_sector_fig
              ),
          ],
        ),
      ],
    )
  ]
)

@app.callback(
  Output('positions_bar', 'figure'),
  [Input('positions_bar-category-filter', 'value'),
   Input('positions_bar-sort-filter', 'value'),]
)
def update_positions_bar(filter, sort_type):
  df = df_portfolio
  if filter != 'All':
    df = df[df['Category'] == filter]
  
  if sort_type == 'alpha':
      sort_value = 'category descending'
  elif sort_type == 'num':
      sort_value = 'total ascending'


  fig = px.bar(df, x='Current Value', y='Symbol')
  fig.update_layout()
  fig.update_layout(
    title=f'Postion breakdown: {filter}',
    yaxis={'categoryorder':sort_value},
    width=800,
    height=800
  )
  return fig

if __name__ == '__main__':
  app.run_server(debug=False, host='0.0.0.0', port=8050)
