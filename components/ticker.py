# components/ticker.py
import tkinter as tk
from utils.config import *

# class for show list of coins on top left
class WatchlistPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CARD_COLOR, padx=15, pady=15)
        self.pack(fill=tk.X, pady=(0, 20))
        self.price_labels = {} # dictionary to save label for update later

    # create row for each coin in list
    def create_rows(self, coin_list):
        # delete old items
        for widget in self.winfo_children():
            widget.destroy()
        self.price_labels.clear()

        for symbol in coin_list:
            row = tk.Frame(self, bg=CARD_COLOR)
            row.pack(fill=tk.X, pady=6)
            
            # show symbol name
            tk.Label(row, text=symbol, fg=MUTED_COLOR, bg=CARD_COLOR, font=FONT_BOLD, width=8, anchor="w").pack(side=tk.LEFT, anchor="n", pady=2)
            
            right_panel = tk.Frame(row, bg=CARD_COLOR)
            right_panel.pack(side=tk.RIGHT, fill=tk.X, expand=True)

            la_price = tk.Label(right_panel, text="...", fg=TEXT_COLOR, bg=CARD_COLOR, font=("Segoe UI", 14, "bold"), anchor="e")
            la_price.pack(side=tk.TOP, fill=tk.X)

            # frame for show volume and percent
            stats_frame = tk.Frame(right_panel, bg=CARD_COLOR)
            stats_frame.pack(side=tk.TOP, fill=tk.X)

            la_volume = tk.Label(stats_frame, text="", fg=MUTED_COLOR, bg=CARD_COLOR, font=("Segoe UI", 9), width=10, anchor="e")
            la_volume.pack(side=tk.RIGHT)

            la_change = tk.Label(stats_frame, text="", fg=GREEN_COLOR, bg=CARD_COLOR, font=("Segoe UI", 10, "bold"), width=20, anchor="e")
            la_change.pack(side=tk.RIGHT, padx=(0, 10))

            # save label to variable 
            self.price_labels[symbol] = (la_price, la_change, la_volume)

    # update new data to label
    def update_data(self, symbol, price, change, percent, volume):
        if symbol not in self.price_labels: return
        
        la_p, la_c, la_v = self.price_labels[symbol]
        
        # update price text
        la_p.config(text=f"${price:,.2f}")
        
        # check color green or red
        color = GREEN_COLOR if percent >= 0 else RED_COLOR
        la_p.config(fg=TEXT_COLOR)
        
        # update change text and volume
        la_c.config(text=f"{change:+.2f} ({percent:+.2f}%)", fg=color)
        la_v.config(text=f"Vol: {volume/1000:,.0f}K")