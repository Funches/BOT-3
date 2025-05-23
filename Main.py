import time
import sqlite3
from datetime import datetime
from newsapi import NewsApiClient
from textblob import TextBlob
import yfinance as yf
import requests
import logging

# Initialize NewsAPI client
newsapi = NewsApiClient(api_key='b309cd0d-0724-42fd-9368-56971ec1784d')

# List of reliable news sources
reliable_sources = [
    'bloomberg', 'marketwatch', 'seeking-alpha', 'reuters', 'investors-business-daily'
]

# Fetch market-related news
def get_market_news():
    all_articles = newsapi.get_everything(
        q="stocks OR market OR earnings OR merger OR breakout",  # Keywords to track
        sources="bloomberg,marketwatch,seeking-alpha",  # Limit to financial sources
        language="en",
        sort_by="publishedAt",  # Sort by latest
        page_size=5
    )
    return all_articles['articles']

# Analyze sentiment of headlines
def analyze_sentiment(headline):
    analysis = TextBlob(headline)
    polarity = analysis.sentiment.polarity  # Ranges from -1 (negative) to 1 (positive)

    # Consider headlines with high positive or negative polarity as sensational
    if polarity > 0.5:
        return 'positive'
    elif polarity < -0.5:
        return 'negative'
    else:
        return 'neutral'

# Filter news by reliable sources
def filter_reliable_sources(news_articles):
    return [
        article for article in news_articles if any(source in article['source']['id'] for source in reliable_sources)
    ]

# Filter out sensationalized headlines
def filter_sensational_headlines(news_articles):
    return [
        article for article in news_articles if analyze_sentiment(article['title']) == 'neutral'
    ]

# Get real-time stock data from Yahoo Finance
def get_stock_data(symbol):
    stock = yf.Ticker(symbol)
    return stock.history(period="1d", interval="5m")  # Get 5-minute intervals for live data

# Analyze if volume has spiked
def analyze_volume(stock_data):
    volume_avg = stock_data['Volume'].rolling(window=20).mean()  # 20-period moving average of volume
    latest_volume = stock_data['Volume'].iloc[-1]  # Latest volume
    return latest_volume > volume_avg.iloc[-1] * 2  # Volume spike detected if > 2x average

# Store news data in a database (for future analysis)
def store_news_in_db(news_articles):
    conn = sqlite3.connect('trading_news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news (headline TEXT, source TEXT, date TEXT)''')
    
    for article in news_articles:
        c.execute("INSERT INTO news (headline, source, date) VALUES (?, ?, ?)",
                  (article['title'], article['source']['id'], article['publishedAt']))
    
    conn.commit()
    conn.close()

# Send alerts to Discord
def send_discord_alert(message):
    webhook_url = 'https://discord.gg/S5dm6nZU'
    payload = {'content': message}
    requests.post(webhook_url, data=payload)

# Main function to run 24/7
def continuous_search_and_trade(symbol, interval=300):
    while True:
        print(f"{datetime.now()}: Checking news for {symbol}...")
        
        # Fetch and filter news
        news_articles = get_market_news()
        filtered_articles = filter_reliable_sources(news_articles)
        non_sensational_articles = filter_sensational_headlines(filtered_articles)
        
        # Store filtered news in the database
        store_news_in_db(non_sensational_articles)
        
        if non_sensational_articles:
            for article in non_sensational_articles:
                print(f"Relevant news for {symbol}: {article['title']}")
                
                # Get stock data
                stock_data = get_stock_data(symbol)
                volume_spike = analyze_volume(stock_data)
                
                # Execute trade logic (buy/sell)
                if volume_spike:
                    print(f"Volume Spike Detected for {symbol}. Possible Breakout!")
                    # Execute trade (implement trade logic here)
                    send_discord_alert(f"Trade Alert: Volume Spike Detected for {symbol}. Possible Breakout!")
                else:
                    print(f"No significant volume spike for {symbol}. Hold off on trading.")
        else:
            print(f"No relevant news for {symbol} at this time.")
        
        time.sleep(interval)  # Check for news every interval (default is 5 minutes)

# Example usage
continuous_search_and_trade('AAPL')
import requests

def execute_trade(symbol, action, quantity):
    url = "https://api.tradovate.com/v1/orders"
    headers = {'Authorization': 'Bearer YOUR_API_KEY'}
    data = {
        'symbol': symbol,
        'action': action,  # 'BUY' or 'SELL'
        'quantity': quantity,
        'orderType': 'LIMIT',
        'price': current_price  # Fetch this from your live market data
    }
    response = requests.post(url, headers=headers, data=data)
    print(f"Trade executed: {response.json()}")
import sqlite3

# Create a database to store news articles for further analysis
def store_news_in_db(news_articles):
    conn = sqlite3.connect('trading_news.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS news (headline TEXT, source TEXT, date TEXT)''')
    
    for article in news_articles:
        c.execute("INSERT INTO news (headline, source, date) VALUES (?, ?, ?)",
                  (article['title'], article['source']['id'], article['publishedAt']))
    
    conn.commit()
    conn.close()
import time
from datetime import datetime

# Function to run 24/7 news search and trading decisions
def continuous_search_and_trade(symbol, interval=300):
    while True:
        print(f"{datetime.now()}: Checking news for {symbol}...")
        
        # Fetch latest news
        news_articles = get_market_news()  # Assume get_market_news() is implemented
        filtered_articles = filter_reliable_sources(news_articles)  # Filter by reliable sources
        non_sensational_articles = filter_sensational_headlines(filtered_articles)  # Filter out sensational headlines
        
        # If relevant news is found
        if non_sensational_articles:
            for article in non_sensational_articles:
                print(f"Relevant news for {symbol}: {article['title']}")
                
                # Get stock data
                stock_data = get_stock_data(symbol)  # Assume get_stock_data() is implemented
                volume_spike = analyze_volume(stock_data)  # Assume analyze_volume() is implemented

                # Execute trade if conditions are met
                if volume_spike:
                    print(f"Volume Spike Detected for {symbol}. Possible Breakout!")
                    # Execute buy trade logic (add trade execution here)
                else:
                    print(f"No significant volume spike for {symbol}. Hold off on trading.")
        else:
            print(f"No relevant news for {symbol} at this time.")
        
        # Wait for the next iteration
        time.sleep(interval)  # Check every 'interval' seconds (default is 5 minutes)

# Example usage
continuous_search_and_trade('AAPL')


