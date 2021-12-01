from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
import time
import datetime
import pandas as pd
import plotly.express as px
from fbprophet import Prophet
import matplotlib.pyplot as plt
from fbprophet.plot import plot_plotly
from plotly import graph_objs as go
from .models import Stock

from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from home.models import History
from yahoo_fin import news


# Create your views here.

def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


# @cache_page(60 * 60 * 24)
@vary_on_cookie
def stock(request, ticker):
    data = historicaldata(ticker, 1577750400,
                          1635465600)  # 1577750400, 1635465600 are the period converted into unix time stamp(For Yahooo Finance API)
    df = pd.DataFrame(data)
    # Saving User History
    stock = Stock.objects.get(ticker=ticker)
    user = request.user
    user_history = History(user=user, stock=stock)
    user_history.save()
    # UserHistory.objects.create(user=request.user, stock=stock)
    # prediction of the selected stock
    if request.method == 'POST':
        start_date = request.POST.get('startDate')
        end_date = request.POST.get('endDate')
        period1 = int(time.mktime(datetime.datetime.strptime(start_date, "%Y-%m-%d").timetuple()))
        period2 = int(time.mktime(datetime.datetime.strptime(end_date, "%Y-%m-%d").timetuple()))
        data = historicaldata(ticker, period1, period2)
        # Clear previously stored cache if any
        cache.clear()
        df = pd.DataFrame(data)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Open'], name='Opening Price'))
    fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name="Closing Price"))
    fig.layout.update(title_text=f"Time Series Data of {ticker}", xaxis_rangeslider_visible=True, width=650,
                      paper_bgcolor='rgba(0,0,0, 0)',
                      plot_bgcolor='rgba(0,0,0, 0)',
                      legend=dict(
                          orientation="h",
                          yanchor="bottom",
                          y=1.02,
                          xanchor="right",
                          x=1
                      )
                      )

    # predicted_graph = stock_prediction(ticker, period=365)
    df_train = df[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=365)
    forecast = m.predict(future)
    predicted_graph = plot_plotly(m, forecast)
    predicted_graph.update_layout(title_text="Predicted Stock Price", xaxis_rangeslider_visible=True,
                                  yaxis_title="Price", xaxis_title="Date",
                                  autosize=False,
                                  width=650,
                                  height=450,
                                  paper_bgcolor='rgba(0,0,0, 0)',
                                  plot_bgcolor='rgba(0,0,0, 0)'
                                  )
    # Converting graphs to html
    predicted_graph = predicted_graph.to_html(full_html=False)
    graph = fig.to_html(full_html=False)
    df['Close'] = df['Close'].map('${:,.2f}'.format)
    df['Open'] = df['Open'].map('${:,.2f}'.format)
    df['High'] = df['High'].map('${:,.2f}'.format)
    df['Low'] = df['Low'].map('${:,.2f}'.format)
    df = df.tail().T.to_dict().values()
    forecast = forecast.tail().T.to_dict().values()
    topnews = stock_news(ticker)
    return render(request, 'home/graph.html',
                  {'fig': graph, 'predicted_fig': predicted_graph, "dataframe": df, "predicted_df": forecast,
                   "topnews": topnews})


def stock_prediction(ticker, period):
    data = historicaldata(ticker)
    df = pd.DataFrame(data)

    df_train = df[['Date', 'Close']]
    df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})
    m = Prophet()
    m.fit(df_train)
    future = m.make_future_dataframe(periods=period)
    forecast = m.predict(future)
    graph = plot_plotly(m, forecast)
    return graph


def historicaldata(ticker, start_date, end_date):
    # period1 = int(time.mktime(datetime.datetime(2020, 12, 1, 23, 59).timetuple()))
    # period2 = int(time.mktime(datetime.datetime(2021, 10, 28, 23, 59).timetuple()))
    period1 = start_date
    period2 = end_date
    ticker = ticker
    interval = '1d'  # Weekly - 1wk, Monthly- 1m, Daily - 1d
    query_string = f'https://query1.finance.yahoo.com/v7/finance/download/{ticker}?period1={period1}&period2={period2}&interval={interval}&events=history&includeAdjustedClose=true'
    df = pd.read_csv(query_string)
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    df['Date'] = pd.to_datetime(df['Date'])
    return df


def stock_news(ticker):
    all_news = news.get_yf_rss(ticker)
    topnews = all_news[0:5]
    return topnews
