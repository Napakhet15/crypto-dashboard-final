# components/controls.py
import tkinter as tk
from tkinter import messagebox
from utils.config import *

# class for button buy and sell
class ControlPanel(tk.Frame):
    def __init__(self, parent, on_buy, on_sell, on_watchlist):
        super().__init__(parent, bg=BG_COLOR)
        self.pack(fill=tk.X, pady=(0, 10))
        self.grid_columnconfigure(1, weight=1) 

        bt_area = tk.Frame(self, bg=BG_COLOR)
        bt_area.grid(row=0, column=0, sticky="w")
        
        tk.Button(bt_area, text="BUY LONG", bg=GREEN_COLOR, fg="white", font=FONT_BOLD, width=12, command=on_buy).pack(side=tk.LEFT, padx=5)
        tk.Button(bt_area, text="SELL SHORT", bg=RED_COLOR, fg="white", font=FONT_BOLD, width=12, command=on_sell).pack(side=tk.LEFT, padx=5)
        tk.Button(bt_area, text="+ Watchlist", bg="#4F46E5", fg="white", font=FONT_BOLD, width=12, command=on_watchlist).pack(side=tk.LEFT, padx=5)

        # input box on right side
        form = tk.Frame(self, bg=CARD_COLOR, padx=15, pady=5)
        form.grid(row=0, column=2, sticky="e")
        
        tk.Label(form, text="Price:", fg=MUTED_COLOR, bg=CARD_COLOR).pack(side=tk.LEFT, padx=(0, 5))
        self.price_entry = tk.Entry(form, width=10, bg="#374151", fg="white", insertbackground="white")
        self.price_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(form, text="Qty:", fg=MUTED_COLOR, bg=CARD_COLOR).pack(side=tk.LEFT, padx=(10, 5))
        self.qty_entry = tk.Entry(form, width=8, bg="#374151", fg="white", insertbackground="white")
        self.qty_entry.pack(side=tk.LEFT, padx=5)
        
        self.total_label = tk.Label(form, text="Total: $0.00", fg=GREEN_COLOR, bg=CARD_COLOR, font=FONT_MAIN, width=15)
        self.total_label.pack(side=tk.LEFT, padx=10)
        
        tk.Button(form, text="Confirm", bg="#6B7280", fg="white", command=self.confirm_order).pack(side=tk.LEFT, padx=5)
        
        # check when typing to calculate
        self.price_entry.bind("<KeyRelease>", self.calculate_total)
        self.qty_entry.bind("<KeyRelease>", self.calculate_total)

    def confirm_order(self):
        messagebox.showinfo("Order", "Order Submitted")

    # calculate total money = price * quantity
    def calculate_total(self, event=None):
        try:
            p = float(self.price_entry.get())
            q = float(self.qty_entry.get())
            self.total_label.config(text=f"Total: ${p*q:,.2f}", fg=GREEN_COLOR)
        except: self.total_label.config(text="Invalid", fg=RED_COLOR)

    # put price automatically
    def fill_price(self, price):
        self.price_entry.delete(0, tk.END)
        self.price_entry.insert(0, f"{price:.2f}")
        self.calculate_total()