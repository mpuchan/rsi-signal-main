import schedule
import time
import requests
from rsi_calculator import get_coins_rsi
from bot_sender import send_message
import pandas as pd
from dotenv import load_dotenv
import json
import os

load_dotenv()
BYBIT_API_KEY = os.getenv("BYBIT_API_KEY")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET")
BYBIT_URL = "https://api.bybit.com/v5/"

with open('settings.json') as f:
    settings = json.load(f)
    
COINS = settings['coins']
CHECK_INTERVAL = settings['check_interval']
RSI_THRESHOLD = settings['rsi_threshold']

def job():   
    rsi_values = get_coins_rsi(COINS)
    for coin, rsi in rsi_values.items():
        print(f"{coin}: {rsi}")      
        if isinstance(rsi, float) and rsi < RSI_THRESHOLD:
            url1 = f'{BYBIT_URL}market/tickers?category=spot&symbol={coin}'
            response = requests.get(url1)
            data = response.json()['result']['list']
            df = pd.DataFrame(data, columns=[
                'lastPrice', 'prevPrice24h', 'price24hPcnt', 'highPrice24h', 'lowPrice24h', 
                'volume24h', 'turnover'
            ])
            df['last'] = df['lastPrice'].astype(float)
            df['vol'] = df['volume24h'].astype(float)
            lastprice = df['last'].to_string(index=False)
            x = float(lastprice)
            target = x-(x * 3)/100
            volume = df['vol'].to_string(index=False)
            message = f"😱 Hati-Hati {coin} DUMP 😱\n \n RSI Oversold Dibawah 30 📉 \n \n 🕰️ Time Frame : {CHECK_INTERVAL} menit \n 📍 RSI Saat Ini : {round(rsi,1)} \n 💰 Harga Saat ini : $ {lastprice} \n 📊 Volume : {volume} \n \n *Diprediksi Bisa Turun Lebih Dalam ke : $ {target}"
            send_message(message)

def main():
    print(f'Bot is Started, Checking RSI every {CHECK_INTERVAL} Minutes')
    schedule.every(CHECK_INTERVAL).minutes.do(job)    
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()