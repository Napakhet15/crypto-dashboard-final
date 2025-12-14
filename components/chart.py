# components/chart.py
import tkinter as tk
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.gridspec as gridspec
from utils.config import *

# class for showing graph on top right
class ChartPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=CARD_COLOR, padx=10, pady=10)
        self.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # setup matplotlib figure
        self.fig = Figure(figsize=(5, 3.2), dpi=100) 
        self.fig.patch.set_facecolor(CARD_COLOR)
        
        # split into 2 graphs (price and volume)
        gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1.2]) 
        self.ax1 = self.fig.add_subplot(gs[0])
        self.ax2 = self.fig.add_subplot(gs[1], sharex=self.ax1)
        
        # create canvas for tkinter
        self.canvas = FigureCanvasTkAgg(self.fig, self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # function to draw graph
    def draw_chart(self, chart_data, symbol): 
        if len(chart_data) < 2: return 
        
        self.ax1.clear()
        self.ax2.clear()
        self.fig.texts.clear()
        
        # use only last 40 data points
        data = chart_data[-40:] 
        indexes = range(len(data))
        
        times = []
        opens = []
        closes = []
        highs = []
        lows = []
        volumes = []

        #Loop through each data point
        for d in data:
            # Convert timestamp
            time_obj = datetime.fromtimestamp(d['t']/1000)
            times.append(time_obj.strftime('%H:%M'))
            
            # Store price and volume data
            opens.append(d['o'])
            closes.append(d['c'])
            highs.append(d['h'])
            lows.append(d['l'])
            volumes.append(d['v'])
        
        #Loop to determine colors (Green if Close >= Open, else Red)
        colors = []
        for i in range(len(data)):
            if closes[i] >= opens[i]:
                colors.append(GREEN_COLOR)
            else:
                colors.append(RED_COLOR)
        
        # draw price lines (Wicks)
        self.ax1.vlines(x=indexes, ymin=lows, ymax=highs, color=colors, linewidth=1)
        
        # Loop to draw candlestick bodies
        for i in range(len(data)):
            o = opens[i]
            c = closes[i]
            
            height = abs(c - o)
            lower = min(o, c)
            
            # If Open and Close prices are equal, set a minimum height for visibility
            if height == 0: 
                height = lower * 0.00001 
            
            self.ax1.bar(i, height, bottom=lower, color=colors[i], width=0.6) 
            
        # style the chart 1
        self.ax1.grid(color=MUTED_COLOR, linestyle=':', linewidth=0.5, alpha=0.2)
        self.ax1.set_facecolor(CARD_COLOR)
        self.ax1.tick_params(colors='white', bottom=False, labelbottom=False) 
        for spine in self.ax1.spines.values(): spine.set_color(MUTED_COLOR)

        # draw volume graph
        self.ax2.bar(indexes, volumes, color=colors, width=0.6, alpha=0.5)
        self.ax2.grid(color=MUTED_COLOR, linestyle=':', linewidth=0.5, alpha=0.2)
        self.ax2.set_facecolor(CARD_COLOR)
        
        # x-axis time label
        step = 5 
        self.ax2.set_xticks(list(indexes)[::step])
        self.ax2.set_xticklabels(times[::step])
        self.ax2.tick_params(colors='white', bottom=False, labelbottom=True)
        for spine in self.ax2.spines.values():
            spine.set_visible(True)
            spine.set_color(MUTED_COLOR)

        self.fig.tight_layout()
        self.fig.subplots_adjust(hspace=0.6) 
        
        # put text volume
        unit_name = symbol.split("/")[0]
        bbox = self.ax2.get_position()
        self.fig.text(0, bbox.y1 + 0.08, f"Volume ({unit_name})", color=TEXT_COLOR, fontsize=11, fontweight='bold', ha='left', va='bottom')
        
        self.canvas.draw()