# components/history.py
import tkinter as tk
from utils.config import *

# class for history trade on the right
class TradeHistoryPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CARD_COLOR, height=220)
        self.pack(fill=tk.X, pady=(0, 20))
        self.pack_propagate(False) 
        
        tk.Label(self, text="Recent Transactions", fg=TEXT_COLOR, bg=CARD_COLOR, font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=15, pady=10)
        
        self.table_frame = tk.Frame(self, bg=CARD_COLOR, padx=15)
        self.table_frame.pack(fill=tk.BOTH, expand=True)

        self.headers = ["Time", "Symbol", "Side", "Price", "Amount", "Total ($)"]
        
        # setup column size
        for i in range(len(self.headers)):
            self.table_frame.grid_columnconfigure(i, weight=1, uniform="group1")

        # create header
        for i, header in enumerate(self.headers):
            tk.Label(self.table_frame, text=header, fg=MUTED_COLOR, bg=CARD_COLOR, 
                     font=("Segoe UI", 11, "bold"), anchor="w").grid(row=0, column=i, sticky="ew", pady=(0, 5))

    # add new data to table
    def update_trades(self, trade_list):
        # delete old rows
        for widget in self.table_frame.winfo_children():
            info = widget.grid_info()
            if 'row' in info and int(info['row']) > 0:
                widget.destroy()
        
        # loop to make label
        for i, (time, sym, side, price, amount, total, color) in enumerate(trade_list):
            row_index = i + 1
            values = [time, sym, side, f"{price:,.2f}", f"{amount:.4f}", f"{total:,.2f}"]
            
            for col_index, val in enumerate(values):
                # check color for buy or sell
                text_color = color if col_index == 2 else (MUTED_COLOR if col_index==0 or col_index==5 else TEXT_COLOR)
                
                tk.Label(self.table_frame, text=val, fg=text_color, bg=CARD_COLOR, 
                         font=("Segoe UI", 11), anchor="w").grid(row=row_index, column=col_index, sticky="ew")