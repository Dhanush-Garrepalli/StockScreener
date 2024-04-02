import streamlit as st
import requests

@st.cache
def search_symbols(keyword, api_key):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'SYMBOL_SEARCH',
        'keywords': keyword,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        symbols = data.get('bestMatches', [])
        return [{'symbol': match['1. symbol'], 'name': match['2. name']} for match in symbols]
    else:
        st.error(f"Failed to search symbols: {response.status_code}")
        return []


@st.cache
def get_stock_data(symbol, api_key):
    url = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': api_key
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        time_series = data.get('Time Series (Daily)', {})
        if time_series:
            latest_date = next(iter(time_series))
            latest_data = time_series[latest_date]
            return {
                'symbol': symbol,
                'price': float(latest_data['4. close']),
                'volume': int(latest_data['5. volume']),
                'cap': None  # Placeholder for market cap
            }
    else:
        st.error(f"Failed to retrieve data for symbol {symbol}: {response.status_code}")
        return None

def filter_stocks(stocks, min_price, max_price, min_volume):
    return [stock for stock in stocks if stock and min_price <= stock["price"] <= max_price and stock["volume"] >= min_volume]

st.title('Stock Screener Application')

api_key = st.secrets["alpha_vantage"]["api_key"]

keyword = st.text_input('Enter a keyword to search for symbols:')
if keyword:
    searched_symbols = search_symbols(keyword, api_key)
    if searched_symbols:
        symbol_options = {s['symbol']: s['name'] for s in searched_symbols}
        selected_symbol = st.selectbox('Select a symbol to screen', options=list(symbol_options.keys()), format_func=lambda x: f"{x} - {symbol_options[x]}")
    else:
        selected_symbol = None
else:
    selected_symbol = None


if selected_symbol:
    st.subheader(f'Screening data for {selected_symbol}')
    min_price = st.slider('Minimum Price', 0, 500, 100)
    max_price = st.slider('Maximum Price', min_price, 500, 150)
    min_volume = st.slider('Minimum Volume', 10000, 10000000, 50000)
    
    if st.button('Screen Stock'):
        stock_data = get_stock_data(selected_symbol, api_key)
        results = filter_stocks([stock_data], min_price, max_price, min_volume)
        if results:
            st.write(results)
        else:
            st.write("No stock data meets the criteria.")
