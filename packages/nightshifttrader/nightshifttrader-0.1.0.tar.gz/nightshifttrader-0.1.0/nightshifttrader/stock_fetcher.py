import requests

def get_stock_price(ticker):
    # Example API endpoint (you'll need to replace this with a real one)
    url = f"https://api.example.com/stock/{ticker}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['price']
    else:
        return None