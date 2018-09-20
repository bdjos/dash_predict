import dash
from dash.dependencies import Output, Event
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import pandas as pd
import sys

PATHS = ['.', './dash_predict','./dash_predict/modules']

for PATH in PATHS:
    if PATH not in sys.path:
        sys.path.insert(0, PATH)

## If running from apache server, import from dash_predict, else import from ./
if __name__ == "__main__":  
    import pandasdb  
else:
    from dash_predict import pandasdb
    
from datetime import datetime, timedelta

def dash_data(start_date, end_date, title, db_obj, **tables):
    '''Input start_date and end_date as datetime objects with (year, month, day, hour) values.
    (minute, second) == 0. **tables = dictionary of tables:columns.'''

    ## Find delta hours for date_range periods
    delta = end_date - start_date
    delta_hours = delta.days*24 + delta.seconds/3600 +1
    date_range = pd.date_range(start=start_date, end=end_date, periods = delta_hours)
    
    ## Pull data from each table and create graph trace for each
    data = []
    for table in tables:
        table_df = db_obj.pd_from_db(table)
        table_df = table_df.set_index('Date/Time')
        table_df = table_df[~table_df.index.duplicated()]
        table_df = table_df.reindex(date_range)
        table_df = table_df[tables[table]['Column']]
#        df[tables[table]['Column']] = table_df

        ## Create plot data for all tables
        trace = go.Scatter(
            x=date_range,
            y=table_df,
            name=tables[table]['Name'],
            mode= 'lines',
            line=dict(
                    color=tables[table]['Line Color'],
                    width=2,
                    dash=tables[table]['Dash'])
            )
        data.append(trace)

    data = go.Data(data)
    return {'data': data,'layout' : go.Layout(xaxis=dict(title='Date', range=[start_date, end_date]),
                                              yaxis=dict(title='Demand', range=[10000, 25000]),
                                              title=title)}

## Database Info and connect to database
database = 'bjos'
password = '3iRM7Ihr@'
host = '138.197.155.217'

db_obj = pandasdb.pandasdb(database, password, host)

## Dash app body info
app = dash.Dash(__name__)
app.css.append_css({"external_url": "https://codepen.io/chriddyp/pen/bWLwgP.css"})

app.layout = html.Div(style={'margin-top': 20}, children=[
            html.H1(children='Ontario Demand Forecast',
                    style={'textAlign': 'center'}),
            html.Div(children='''The tables below compare IESO predicted values to a prediction based
                     on a neural network model. The NN is a 12-hour-ahead prediction updated at 10:00
                     and 22:00. IESO predictions are 24-hour updated at 10:00. IESO actuals are updated
                     hourly.''',
                     style={'textAlign': 'center', 'margin-left': 150, 'margin-right': 150}),
            dcc.Graph(id='live-graph', animate=True),
            dcc.Graph(id='five-day', animate=True),
            dcc.Interval(
                    id='graph-update',
                    interval=10*1000),
            dcc.Interval(
                    id='previous-update',
                    interval=60*1000)
        ]
)

## Generate graph data
## Graph 1: Today's data from 00:00 to 23:00
@app.callback(Output('live-graph', 'figure'),
              events=[Event('graph-update', 'interval')])
def update_graph_scatter():
    start_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0)
    end_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 23)
    title = 'Today'

    return dash_data(start_date,
                     end_date,
                     title,
                     db_obj,
                     IESOACTUAL={'Column': 'IESO Actual Demand', 'Name': 'IESO Actual Demand', 'Line Color': 'blue', 'Dash': 'line'},
                     IESOFORECAST={'Column': 'IESO Predicted Demand', 'Name': 'IESO Predicted Demand', 'Line Color': 'orange', 'Dash': 'dot'},
                     MYFORECAST={'Column': 'Predicted Demand', 'Name': 'Neural Network Prediction', 'Line Color': 'green', 'Dash': 'dot'},
                     MYFORECAST1={'Column': 'Predicted Demand', 'Name': 'Neural Network Prediction (v2)', 'Line Color': 'red', 'Dash': 'dot'})

## Graph 2: Past five days of data
@app.callback(Output('five-day', 'figure'),
          events=[Event('previous-update', 'interval')])
def update_graph_scatter():
    start_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0) + timedelta(days=-5)
    end_date = datetime(datetime.now().year, datetime.now().month, datetime.now().day, 0)
    title = 'Previous Five Days'

    return dash_data(start_date,
                     end_date,
                     title,
                     db_obj,
                     IESOACTUAL={'Column': 'IESO Actual Demand', 'Name': 'IESO Actual Demand', 'Line Color': 'blue', 'Dash': 'line'},
                     IESOFORECAST={'Column': 'IESO Predicted Demand', 'Name': 'IESO Predicted Demand', 'Line Color': 'orange', 'Dash': 'dot'},
                     MYFORECAST={'Column': 'Predicted Demand', 'Name': 'Neural Network Prediction', 'Line Color': 'green', 'Dash': 'dot'},
                     MYFORECAST1={'Column': 'Predicted Demand', 'Name': 'Neural Network Prediction (v2)', 'Line Color': 'red', 'Dash': 'dot'})

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)

