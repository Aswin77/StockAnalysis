import bs4 as bs
import pickle
import requests
import pandas as pd

html = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
soup = bs.BeautifulSoup(html.text, 'lxml')
table = soup.find('table', {'class': 'wikitable sortable'})
tickers = []
urls = []
name = []
for row in table.findAll('tr')[2:]:
    ticker = row.findAll('td')[0].text
    name.append(row.findAll('td')[1].text)
    ticker = ticker[:-1]

    yahoo_url = 'https://finance.yahoo.com/quote/' + ticker + '/history?p=' + ticker
    urls.append(yahoo_url)
    tickers.append(ticker)

dataframe = pd.DataFrame({
    'ticker': tickers,
    'security': name,
    'yahoo_urls': urls
})
dataframe.to_csv('sp500tickers.csv')

