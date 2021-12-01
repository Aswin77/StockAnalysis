import random
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.cache import cache_page
from yahoo_fin.stock_info import get_live_price

from main.models import Stock, GSPCDATA
from .models import WatchList, History
from yahoo_fin import news
import plotly.express as px
from plotly.graph_objs import *
import plotly.graph_objs as go
import pandas as pd
# Create your views here.


def randomStockNews(ticker):
    # take list of ticker choose one randomly
    choose_ticker = random.choice(ticker)
    random_news = news.get_yf_rss(choose_ticker)
    random_top_news = random_news[0:5]
    return random_top_news


# @cache_page(60 * 60 * 24)
@login_required(login_url='/login/')
def index(request):
    home_watchlist = WatchList.objects.filter(user=request.user)[:8]
    history = History.objects.select_related('stock').filter(user=request.user).order_by('-datetime')[:8]
    # stock in watchlist prices
    stock_prices = []
    second_dict = {}
    for stock in home_watchlist:
        second_dict = {"security": stock.security, "ticker": stock.ticker, "price": round(get_live_price(stock.ticker), 2)}
        stock_prices.append(second_dict)

    if "remove_stock" in request.POST:
        ticker = request.POST.get('ticker')
        security = request.POST.get('security')
        user = request.user
        WatchList.objects.filter(user=user, ticker=ticker, security=security).delete()
        messages.success(request, "Stock removed from watchlist")
        return redirect('watchlist')
    gscp_data = pd.DataFrame(list(GSPCDATA.objects.all().values()))
    # Plot a financial chart using plotly
    # remove plotly background
    layout = Layout(
        paper_bgcolor='rgba(0,0,0, 0)',
        plot_bgcolor='rgba(0,0,0, 0)'
    )

    fig = go.Figure(layout=layout)
    fig.add_trace(go.Line(x=gscp_data['date'], y=gscp_data['close'], name='GSPC'))
    fig.update_layout(
        title='GSPC',
        xaxis_title='Date',
        yaxis_title='Close',
        font=dict(
            family="Times New Roman",
            size=14,
            color="#000000",
        ),
        legend=dict(
            x=0,
            y=1.0,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)',
        ),

    ),
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label="1m", step="month", stepmode="backward"),
                dict(count=6, label="6m", step="month", stepmode="backward"),
                dict(count=1, label="YTD", step="year", stepmode="todate"),
                dict(count=1, label="1y", step="year", stepmode="backward"),
                dict(step="all")
            ])
        )
    )
    gscp_graph = fig.to_html(full_html=False)
    stock_ticker = Stock.objects.all().values('ticker')

    ticker_list = []
    for ticker in stock_ticker:
        ticker_list.append(ticker['ticker'])
    random_news = randomStockNews(ticker_list)
    context = {"watchlist": stock_prices, "history": history, "random_news": random_news, "gscp_graph": gscp_graph}
    return render(request, 'home/home.html', context=context)


@login_required(login_url='/login/')
def profile(request):
    user_email = request.user.email
    first_name = request.user.first_name
    last_name = request.user.last_name
    if request.method == "POST":
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        # Update the Name of the user
        user = User.objects.get(username=request.user.username)
        user.first_name = first_name
        user.last_name = last_name
        user.save(update_fields=['first_name', 'last_name'])
        # One time message to the user
        message = "Your profile has been updated"
        messages.success(request, message)
    context = {"user_email": user_email, "first_name": first_name, "last_name": last_name}
    return render(request, 'home/profile.html', context=context)

@login_required(login_url='/login/')
def forgot_password(request):
    if request.method == "POST":
        username = request.user.username
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        if password1 == password2:
            user = User.objects.get(username=username)
            user.set_password(password1)
            user.save()
            messages.success(request, "Password Updated Successfully")
        else:
            return render(request, 'home/forgot_password.html', {'error': 'Passwords do not match'})
    return render(request, 'home/forgot_password.html')

@login_required(login_url='/login/')
def stock_list(request):
    companies = Stock.objects.all()
    watchlist = WatchList.objects.filter(user=request.user)
    for company in companies:
        company.is_in_watchlist = False
        for watch in watchlist:
            if company.ticker == watch.ticker:
                company.is_in_watchlist = True
    
    if request.method == "POST":
        if "search_stock" in request.POST:
            search_text = request.POST['search']
            companies = Stock.objects.filter(security__icontains=search_text)
            if not companies:
                companies = Stock.objects.filter(ticker__icontains=search_text)

         # Adding stock to the watchlist
        if "add_stock" in request.POST:
            ticker = request.POST.get('ticker')
            security = request.POST.get('security')
            print("In this section")
            user = request.user
            WatchList.objects.create(user=user, ticker=ticker, security=security)
            messages.success(request, "Stock added to watchlist")
            return redirect('watchlist')
        elif "remove_stock" in request.POST:
            ticker = request.POST.get('ticker')
            security = request.POST.get('security')
            user = request.user
            WatchList.objects.filter(user=user, ticker=ticker, security=security).delete()
            messages.success(request, "Stock removed from watchlist")
            return redirect('watchlist')
        
    context = {"companies": companies}

   
    return render(request, 'home/stock_list.html', context=context)


    return render(request, 'home/stock_list.html', context=context)

@login_required(login_url='/login/')
def watchlist(request):
    watchlist = WatchList.objects.filter(user=request.user)
    if "remove_stock" in request.POST:
        ticker = request.POST.get('ticker')
        security = request.POST.get('security')
        user = request.user
        WatchList.objects.filter(user=user, ticker=ticker, security=security).delete()
        messages.success(request, "Stock removed from watchlist")
        return redirect('watchlist')
    
    context = {"watchlist": watchlist}

    return render(request, 'home/watchlist.html', context=context)

@login_required(login_url='/login/')
def history(request):
    user_history = History.objects.select_related('stock').filter(user=request.user).order_by('-datetime')
   
    context = {"user_history": user_history}
    return render(request, 'home/history.html', context=context)
