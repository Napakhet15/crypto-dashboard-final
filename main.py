# main.py
import tkinter as tk
from tkinter import Menu
import threading
import json
import sys
import requests
import websocket
from datetime import datetime

# import other files
from utils.config import *
from components.ticker import WatchlistPanel
from components.orderbook import OrderBookPanel
from components.chart import ChartPanel
from components.history import TradeHistoryPanel
from components.controls import ControlPanel

# main class to control the application
class CryptoApp(tk.Tk):
    # initialize the application and variables
    def __init__(self):
        super().__init__()
        self.title("CRYPTO Dashboard (30m Timeframe)")
        self.geometry("1280x850")
        
        # set minimum size of window
        self.minsize(1000, 600) 

        self.configure(bg=BG_COLOR)
        self.protocol("WM_DELETE_WINDOW", self.close_app)
        self.is_running = True

        # dictionary for coin list
        self.coins = {
            "BTC/USDT": "btcusdt", "ETH/USDT": "ethusdt",
            "SOL/USDT": "solusdt", "BNB/USDT": "bnbusdt", "XRP/USDT": "xrpusdt"
        }
        self.active_coins = list(self.coins.keys())
        self.current_coin = "BTC/USDT"
        
        # variables to save data
        self.latest_prices = {} 
        self.chart_data = {k: [] for k in self.coins}
        self.trade_list = []
        self.websockets = [] 

        # create user interface
        self.setup_ui()
        
        # start background processes
        self.load_historical_data()   # get old data
        self.start_websockets()       # connect to socket
        self.update_loop()            # start timer loop

    # create all user interface components
    def setup_ui(self):
        # create header section
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill=tk.X, padx=20, pady=15)
        tk.Label(header, text="CRYPTO Dashboard", fg=TEXT_COLOR, bg=BG_COLOR, font=("Segoe UI", 24, "bold")).pack(side=tk.LEFT)
        tk.Button(header, text="Refresh", bg="#374151", fg="white", font=FONT_BOLD, padx=15, pady=5, command=self.load_historical_data).pack(side=tk.RIGHT)

        # create main layout container
        main_layout = tk.Frame(self, bg=BG_COLOR)
        main_layout.pack(fill=tk.BOTH, expand=True)
        left_panel = tk.Frame(main_layout, bg=BG_COLOR, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 15))
        right_panel = tk.Frame(main_layout, bg=BG_COLOR)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20))

        # add panels to the screen
        self.watchlist_panel = WatchlistPanel(left_panel)
        self.watchlist_panel.create_rows(self.active_coins)
        
        self.orderbook_panel = OrderBookPanel(left_panel)

        # create chart container
        chart_container = tk.Frame(right_panel, bg=CARD_COLOR, padx=10, pady=10)
        chart_container.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        top_chart_bar = tk.Frame(chart_container, bg=CARD_COLOR)
        top_chart_bar.pack(fill=tk.X, pady=(0, 10))
        
        self.la_chart_title = tk.Label(top_chart_bar, text="Market Chart", fg=TEXT_COLOR, bg=CARD_COLOR, font=("Segoe UI", 16, "bold"))
        self.la_chart_title.pack(side=tk.LEFT)
        
        # create menu to change coin
        self.var_coin = tk.StringVar(value=self.current_coin)
        option_menu = tk.OptionMenu(top_chart_bar, self.var_coin, *self.coins.keys(), command=self.change_coin)
        option_menu.config(bg="#374151", fg="white", highlightthickness=0, borderwidth=0, font=FONT_MAIN)
        option_menu["menu"].config(bg=CARD_COLOR, fg="white")
        option_menu.pack(side=tk.RIGHT)

        self.chart_panel = ChartPanel(chart_container)
        self.trade_panel = TradeHistoryPanel(right_panel)
        
        self.control_panel = ControlPanel(right_panel, 
                                          on_buy=self.action_buy,
                                          on_sell=self.action_sell,
                                          on_watchlist=self.popup_watchlist_menu)

    def action_buy(self):
        self.auto_fill_price("BUY")

    def action_sell(self):
        self.auto_fill_price("SELL")

    # loop to update the screen every 5 seconds
    def update_loop(self):
        if not self.is_running: return

        # update trade history panel
        if self.trade_list:
            self.trade_panel.update_trades(self.trade_list[:5]) # show top 5
            self.trade_list = [] # clear list

        # update chart panel
        data = self.chart_data.get(self.current_coin, [])
        self.chart_panel.draw_chart(data, self.current_coin)

        # call this function again in 5000 milliseconds
        self.after(5000, self.update_loop)

    # start a background thread to get old data
    def load_historical_data(self):
        threading.Thread(target=self._fetch_api_data, args=(self.current_coin,), daemon=True).start()

    # connect to api to get candlestick data
    def _fetch_api_data(self, symbol):
        try:
            code = self.coins[symbol].upper()
            url = f"https://api.binance.com/api/v3/klines?symbol={code}&interval=30m&limit=50"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            # organize data into a list
            parsed_data = [{'t': i[0], 'o': float(i[1]), 'h': float(i[2]), 'l': float(i[3]), 'c': float(i[4]), 'v': float(i[5])} for i in data]
            self.chart_data[symbol] = parsed_data
            
            # update the chart immediately
            self.after(0, lambda: self.chart_panel.draw_chart(parsed_data, symbol))
        except: pass

    # connect to websocket for real-time updates
    def start_websockets(self):
        # close old connections
        for ws in self.websockets:
            try: ws.close()
            except: pass
        self.websockets = []

        # connect ticker for all coins in watchlist
        for coin in self.active_coins:
            code = self.coins[coin]
            url = f"wss://stream.binance.com:9443/ws/{code}@ticker"
            ws = websocket.WebSocketApp(url, on_message=lambda ws, msg, c=coin: self.on_ticker_message(c, msg))
            self.websockets.append(ws)
            threading.Thread(target=ws.run_forever, daemon=True).start()

        # connect specific data for current coin
        code = self.coins[self.current_coin]
        
        # connect chart data
        ws_chart = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{code}@kline_30m", on_message=lambda ws, msg: self.on_kline_message(self.current_coin, msg))
        self.websockets.append(ws_chart)
        threading.Thread(target=ws_chart.run_forever, daemon=True).start()

        # connect order book data
        ws_book = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{code}@depth20@1000ms", on_message=self.on_book_message)
        self.websockets.append(ws_book)
        threading.Thread(target=ws_book.run_forever, daemon=True).start()

        # connect trade history data
        ws_trade = websocket.WebSocketApp(f"wss://stream.binance.com:9443/ws/{code}@trade", on_message=self.on_trade_message)
        self.websockets.append(ws_trade)
        threading.Thread(target=ws_trade.run_forever, daemon=True).start()

    # function to handle price updates from websocket
    def on_ticker_message(self, symbol, msg): 
        if not self.is_running: return
        try:
            data = json.loads(msg)
            price = float(data['c'])
            change = float(data['p'])
            percent = float(data['P'])
            volume = float(data['v'])
            
            self.latest_prices[symbol] = price
            # update watchlist panel
            self.after(0, lambda: self.watchlist_panel.update_data(symbol, price, change, percent, volume))
        except: pass

    # function to handle graph updates from websocket
    def on_kline_message(self, symbol, msg): 
        try:
            data = json.loads(msg)
            k = data['k']
            new_candle = {'t': k['t'], 'o': float(k['o']), 'h': float(k['h']), 'l': float(k['l']), 'c': float(k['c']), 'v': float(k['v'])}
            
            chart_list = self.chart_data.get(symbol, [])
            if chart_list and chart_list[-1]['t'] == new_candle['t']: 
                chart_list[-1] = new_candle 
            else:
                chart_list.append(new_candle) 
                if len(chart_list) > 60: chart_list.pop(0)
        except: pass

    # function to handle order book updates from websocket
    def on_book_message(self, ws, msg): 
        try:
            data = json.loads(msg)
            self.after(0, lambda: self.orderbook_panel.update_data(self.current_coin, data['bids'], data['asks']))
        except: pass

    # function to handle trade history updates from websocket
    def on_trade_message(self, ws, msg): 
        try:
            data = json.loads(msg)
            price = float(data['p'])
            qty = float(data['q'])
            side = "SELL" if data['m'] else "BUY"
            time_str = datetime.now().strftime("%H:%M:%S")
            color = GREEN_COLOR if side == "BUY" else RED_COLOR
            total = price * qty
            clean_sym = self.current_coin.replace("/USDT", "")
            
            self.trade_list.insert(0, (time_str, clean_sym, side, price, qty, total, color))
        except: pass

    # function to change the current cryptocurrency
    def change_coin(self, value):
        self.current_coin = value
        self.trade_list = [] 
        self.load_historical_data()
        self.start_websockets() 

    # show a menu to select coins for watchlist
    def popup_watchlist_menu(self):
        menu = tk.Menu(self, tearoff=0)
        for name in self.coins:
            is_active = tk.BooleanVar(value=(name in self.active_coins))
            
            cmd = self.create_toggle_cmd(name, is_active)
            menu.add_checkbutton(label=name, onvalue=True, offvalue=False, variable=is_active, command=cmd)
            
        menu.tk_popup(self.winfo_pointerx(), self.winfo_pointery())

    def create_toggle_cmd(self, name, var):
        def callback():
            self.toggle_coin(name, var.get())
        return callback

    # add or remove coin from the watchlist
    def toggle_coin(self, name, state):
        if state and name not in self.active_coins: self.active_coins.append(name)
        elif not state and name in self.active_coins: self.active_coins.remove(name)
        
        if not self.active_coins: self.active_coins.append("BTC/USDT") 
        
        self.watchlist_panel.create_rows(self.active_coins)
        self.start_websockets()

    # automatically put current price in the box
    def auto_fill_price(self, side):
        price = self.latest_prices.get(self.current_coin, 0)
        self.control_panel.fill_price(price)

    # close all connections and exit the application
    def close_app(self):
        self.is_running = False
        for ws in self.websockets:
            try: ws.close()
            except: pass
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = CryptoApp()
    app.mainloop()