import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go
from collections import deque
import pandas as pd
import os
import sys

PATHS = ['.', './dash_predict','./dash_predict/modules']

for PATH in PATHS:
    if PATH not in sys.path:
        sys.path.insert(0, PATH)
    
from modules import pandasdb
import pandas as pd
from datetime import datetime, timedelta


## Database Info and connect to database   
database = 'bjos'
password = '3iRM7Ihr@'
host = '138.197.155.217'
tables = {'IESOACTUAL': 'IESO Actual Demand', 
          'IESOFORECAST': 'IESO Predicted Demand', 
          'MYFORECAST': 'Predicted Demand'}
        
db_obj = pandasdb.pandasdb(database, password, host)

app = dash.Dash(__name__)

app.layout = html.Div(
        [
            html.H1(children='IESO Predictions'),
            dcc.Graph(id='live-graph', animate=True),
            dcc.Interval(
                    id='graph-update',
                    interval=10*1000
            )
        ]
)

@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])
def update_graph_scatter():
    ## Create date range for previous/next 12 hours
    date_now = datetime(datetime.now().year, datetime.now().month, datetime.now().day, datetime.now().hour)
    date_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0)
    date_end = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23)
    date_range = pd.date_range(start=date_start, end=date_end, periods = 24)
    
    ## Get predictions from database for the selected range
    df = pd.DataFrame()
    for key in tables:
        table_df = db_obj.pd_from_db(key)
        table_df = table_df.set_index('Date/Time')
        table_df = table_df[~table_df.index.duplicated()]
        table_df = table_df.reindex(date_range)
        table_df = table_df[tables[key]]
        df[tables[key]] = table_df
    
    data = [go.Scatter(
        x=df.index,
        y=df['IESO Actual Demand'],
        name='IESO Actual Demand',
        mode= 'lines'
        ),
        plotly.graph_objs.Scatter(
        x=df.index,
        y=df['IESO Predicted Demand'],
        name='IESO Predicted Demand',
        mode= 'lines',
        line=dict(
                color='orange',
                width=2,
                dash='dot')
        ),
        plotly.graph_objs.Scatter(
        x=df.index,
        y=df['Predicted Demand'],
        name='Neural Network Predicted Demand',
        mode= 'lines',
        line=dict(
                color='green',
                width= 2,
                dash = 'dot')
        )
    ]
    data = go.Data(data)
    return {'data': data,'layout' : go.Layout(xaxis=dict(title='Date', range=[date_start, date_end]),
                                              yaxis=dict(title='Demand', range=[12500, 25000]))}        

server = app.server

if __name__ == '__main__':
    my_data = update_graph_scatter()
    print(my_data['data'])
