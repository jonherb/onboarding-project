from flask import Flask, render_template, request, redirect
import requests as rq
from pandas import *
from bokeh.plotting import figure, output_file, show
from bokeh.charts import TimeSeries
from bokeh.resources import CDN
from bokeh.embed import file_html
import requests as rq
import simplejson as sj
import os

import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
apikey = os.environ.get('ALPHAADVANTAGE_KEY')

app = Flask(__name__)
app.vars = {}

@app.route('/', methods = ['GET'])
def get_input():
    return render_template('input.html')

@app.route('/', methods = ['POST'])
def make_output():
    # stock label entry is what's in the input.html file, field entered by user]
    app.vars['stock_label'] = request.form['stock_label_entry']
    app.vars['month'] = request.form['month_entry']
    
    
    payload = {'function': 'TIME_SERIES_DAILY', 'symbol': app.vars['stock_label'], 'outputsize': 'full', 
           'apikey': apikey, 'datatype': 'csv'}
    
    df = rq.get('https://www.alphavantage.co/query', params = payload)
    df = StringIO(df.text)
    df = read_csv(df)
    df.timestamp = to_datetime(df.timestamp)
    df = df.set_index('timestamp')
    
    date_filter = to_datetime(app.vars['month'])
    year_month_filter = str(date_filter.year) + '-' + str(date_filter.month)
    df_f = df.loc[year_month_filter]
    df_f_close = df_f.loc[:, ['close']]
    
    fig = TimeSeries(df_f_close, title = 'Stock Closing Price of ' + str(app.vars['stock_label']) + 
       ' Over ' + str(app.vars['month']), xlabel = 'date', ylabel = 'closing price', legend = False)
    
    output_html = file_html(fig, CDN, 'output plot')
    
    return output_html


if __name__ == '__main__':
  app.run(host = '0.0.0.0')
