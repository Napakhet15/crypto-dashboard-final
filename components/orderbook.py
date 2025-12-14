# components/orderbook.py
import tkinter as tk
from utils.config import *

# class for buy and sell list (bottom left)
class OrderBookPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CARD_COLOR, padx=15, pady=15)
        self.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(self, text="Order Book (Live)", fg=TEXT_COLOR, bg=CARD_COLOR, font=FONT_BOLD).pack(anchor="w", pady=(0, 10))
        
        # create header for table
        header = tk.Frame(self, bg=CARD_COLOR)
        header.pack(fill=tk.X, pady=(0, 5))
        self.column_widths = [8, 14, 14, 8] 
        titles = ["Symbol", "Price", "Amount", "Side"]
        
        for i, title in enumerate(titles):
            tk.Label(header, text=title, fg=MUTED_COLOR, bg=CARD_COLOR, width=self.column_widths[i], anchor="w", font=FONT_MAIN).pack(side=tk.LEFT, padx=5)

        # frame container for data rows
        self.data_container = tk.Frame(self, bg=CARD_COLOR)
        self.data_container.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.data_container, text="Waiting...", fg=MUTED_COLOR, bg=CARD_COLOR).pack(pady=20)

    # update new data to table
    def update_data(self, symbol, bids, asks):
        # remove old data
        for widget in self.data_container.winfo_children(): 
            widget.destroy()
            
        short_name = symbol.replace("/USDT", "")

        # function to create one row
        def add_row(price, qty, side, color):
            row = tk.Frame(self.data_container, bg=CARD_COLOR)
            row.pack(fill=tk.X, pady=1)
            try: 
                price_text = f"{float(price):,.2f}"
                qty_text = f"{float(qty):.4f}"
            except: 
                price_text, qty_text = str(price), str(qty)
            
            # add label to each column
            tk.Label(row, text=short_name, fg=MUTED_COLOR, bg=CARD_COLOR, width=self.column_widths[0], anchor="w").pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=price_text, fg=color, bg=CARD_COLOR, width=self.column_widths[1], anchor="w").pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=qty_text, fg=TEXT_COLOR, bg=CARD_COLOR, width=self.column_widths[2], anchor="w").pack(side=tk.LEFT, padx=5)
            tk.Label(row, text=side, fg=color, bg=CARD_COLOR, width=self.column_widths[3], anchor="w").pack(side=tk.LEFT, padx=5)

        # show sell list (top 7)
        current_asks = asks[:7][::-1] 
        while len(current_asks) < 7: current_asks.insert(0, ["Wait", "0.0"]) 
        for p, q in current_asks: add_row(p, q, "SELL", RED_COLOR)

        # show buy list (top 7)
        current_bids = bids[:7]
        while len(current_bids) < 7: current_bids.append(["Wait", "0.0"])
        for p, q in current_bids: add_row(p, q, "BUY", GREEN_COLOR)