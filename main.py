from datetime import datetime

import requests
import mysql.connector
import json
import sys


def GetCoin():
    response = requests.get("https://api.coinbase.com/v2/currencies")

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The list of currencies is stored in the "data" field of the response
        currencies = data['data']
        # Extract the names of the currencies
        currency_names = [currency['id'] for currency in currencies]
        # Print the list of currency names
        print(currency_names)
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

import requests

def getDepth(asset, side):
    # Send a GET request to the Coinbase Pro API
    response = requests.get(f"https://api.pro.coinbase.com/products/{asset}/ticker")

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The ask or bid price is stored in the "price" field of the response
        price = data['price']
        # Return the price
        return price
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)


def menuBidAsk():
    while True:
        # Print the menu options
        print("1. Get ask price")
        print("2. Get bid price")
        print("3. Quit")
        # Get the user's input
        choice = input("Enter your choice: ")

        # Validate the input
        if choice == "1":
            # User wants to get the ask price
            asset = input("Enter the asset (e.g., BTC-USD): ")
            # Call the get_price() function with the 'ask' side
            ask_price = getDepth(asset, 'ask')
            print(ask_price)
        elif choice == "2":
            # User wants to get the bid price
            asset = input("Enter the asset (e.g., BTC-USD): ")
            # Call the get_price() function with the 'bid' side
            bid_price = getDepth(asset, 'bid')
            print(bid_price)
        elif choice == "3":
            # User wants to quit
            break
        else:
            # Invalid input
            print("Invalid choice. Please try again.")


def get_order_book(asset):
    # Send a GET request to the Coinbase Pro API
    response = requests.get(f"https://api.pro.coinbase.com/products/{asset}/book")

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The order book is stored in the "bids" and "asks" fields of the response
        bids = data['bids']
        asks = data['asks']
        # Return the order book
        return bids, asks
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

import requests

def get_candlestick_data(asset, granularity):
    # Send a GET request to the Coinbase Pro API
    response = requests.get(f"https://api.pro.coinbase.com/products/{asset}/candles", params={'granularity': granularity})

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The candlestick data is returned as a list of lists
        candles = data
        # Return the candlestick data
        return candles
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

def menu_get_candlestick_data():
    granularity_options = {
        '1': 60,
        '2': 300,
        '3': 900,
        '4': 3600,
        '5': 21600,
        '6': 86400
    }

    # Main menu loop
    while True:
        # Print the menu options
        print("1. 1-minute candlesticks")
        print("2. 5-minute candlesticks")
        print("3. 15-minute candlesticks")
        print("4. 1-hour candlesticks")
        print("5. 6-hour candlesticks")
        print("6. 1-day candlesticks")
        print("7. Quit")
        # Get the user's input
        choice = input("Enter your choice: ")

        # Validate the input
        if choice in granularity_options:
            # User has chosen a valid granularity option
            asset = input("Enter the asset (e.g., BTC-USD): ")
            # Get the corresponding granularity value from the dictionary
            granularity = granularity_options[choice]
            # Call the get_candlestick_data() function
            candles = get_candlestick_data(asset, granularity)
            connect_db_store_candles(candles,asset)
            print(candles)
        elif choice == "7":
            # User wants to quit
            break
        else:
            # Invalid input
            print("Invalid choice. Please try again.")

def connect_database():
    # Load the configuration file
    with open('config.json') as f:
        config = json.load(f)

    # Extract the database connection details from the configuration file
    host = config['database']['host']
    user = config['database']['user']
    password = config['database']['password']
    database = config['database']['database']

    # Connect to the database
    cnx = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
    return cnx


def connect_db_store_candles(candles,asset):

    cnx=connect_database()
    cursor=cnx.cursor()

    for candle in candles:
        # Extract the data from the candle
        timestamp,low_price, high_price,open_price, close_price, volume = candle
        # Insert the data into the table
        try:
            cursor.execute(
            f"INSERT INTO Candel (pair,Date, high, low,open, close, volume) VALUES ('{asset}',{timestamp}, {high_price}, {low_price},{open_price}, {close_price}, {volume})")
        except mysql.connector.errors.IntegrityError:
            print(sys.exc_info())

    # Commit the changes
    cnx.commit()
    cursor.close()
    cnx.close()


def store_latest_trades(asset):
    cnx=connect_database()
    cursor=cnx.cursor()

    # Send a GET request to the Coinbase Pro API
    response = requests.get(f"https://api.pro.coinbase.com/products/{asset}/trades")

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The trades data is returned as a list of dictionaries
        trades = data
        # Iterate over the trades
        for trade in trades:
            print(trade)
            # Extract the data from the trade
            trade_id = trade['trade_id']
            timestamp = trade['time']
            dt = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
            dt_str = dt.strftime('%Y-%m-%d %H:%M:%S')
            side = trade['side']
            price = trade['price']
            size = trade['size']

            try:
                # Insert the data into the table
                cursor.execute(f"INSERT INTO trades (trade_id, asset, trades.timestamp, side, price, size) VALUES ({trade_id}, '{asset}', '{dt_str}', '{side}', {price}, {size})")
            except mysql.connector.errors.IntegrityError:
                print(sys.exc_info())

    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)

    # Commit the changes
    cnx.commit()
    cursor.close()
    cnx.close()


def print_menu():
  print("1. Get all pairs listed on coin base")
  print("2. Get the bid or ask on a pair")
  print("3. Get the orderbook on a pair")
  print("4. Get candel and store in db")
  print("5. Get trades and store in db")

def menu():
    while True:
        print_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            print("You selected option 1")
            GetCoin()
        if choice =="2":
            menuBidAsk()
        if choice== "3":
            asset = input("Enter the asset (e.g., BTC-USD): ")
            print(get_order_book())
        if choice =="4":
            menu_get_candlestick_data()
        if choice =="5":
            asset = input("Enter the asset (e.g., BTC-USD): ")
            store_latest_trades(asset)


menu()
