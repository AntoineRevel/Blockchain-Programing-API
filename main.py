import requests



def GetCoin():
    response = requests.get("https://api.coinbase.com/v2/currencies")

    # Check the status code to make sure the request was successful
    if response.status_code == 200:
        data = response.json()
        # The list of currencies is stored in the "data" field of the response
        currencies = data['data']
        # Extract the names of the currencies
        currency_names = [currency['name'] for currency in currencies]
        # Print the list of currency names
        print(currency_names)
    else:
        # Print an error message if the request was unsuccessful
        print("Error:", response.status_code)



def print_menu():
  print("1. Get all pairs listed on coin base")
def menu():
    while True:
        print_menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            print("You selected option 1")
            GetCoin()

#menu()
GetCoin()