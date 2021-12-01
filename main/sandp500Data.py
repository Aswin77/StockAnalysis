from yahoo_fin.stock_info import *
import time

# Today date
today = time.strftime("%Y-%m-%d")
sandp = get_data('^GSPC', start_date='1980-12-31', end_date=today, interval='1d')
# save to dataframe
# set index name to date
sandp.index.name = 'date'
# drop the ticker column
sandp = sandp.drop(columns=['ticker'])
sandp.to_csv('sandp500Data.csv')

