#!/usr/bin/env python3
"""  
Script for obtaining pricing data from osrs real time prices:
    https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices 
"""

import urllib.request
import json
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import pickle
from operator import attrgetter
import smtplib, ssl
from email.message import EmailMessage
import os
import numpy as np
import jsonpickle

# Keep urls global to access with any function
api_url = 'https://prices.runescape.wiki/api/v1/osrs'
latest_url = api_url + '/latest'
map_url = api_url + '/mapping'
five_url = api_url + '/5m'
hour_url = api_url + '/1h'
ts_url = api_url + '/timeseries'

email_msg = ""

# 1) Let user enable which data they want to see with output filters.
# 2) If data is enabled for a particular time frame, then enable 
#    parsing that time frame. /latest is exception
# 3) We cannot apply filters to data user does not want to see

# Class to let user enter range filter
class Range():
    def __init__(self, show=False, min=-2147483647, max=2147483647):
        self.show = show
        self.min = min
        self.max = max

    # Checks if value passes range filter
    def filter(self, value):

        # Do not filter if we aren't showing the data
        if (self.show != True):
            return True

        # Do not pass filter if no data exists
        if (value == None):
            return False    

        if (self.min <= value <= self.max):
            return True
        else:
            return False

class NoFilter():
    def __init__(self, show=False):
        self.show = show 

# Class to let user enter string contains filter
class Contains():
    def __init__(self, show=False, string=""):
        self.show = show
        self.string = string

    # Checks if string is contained in item name
    # If so, passes filter
    def filter(self, name):

        # Do not filter if not showing data
        if (self.show != True):
            return True

        if (self.string in name):
            return True
        else:
            return False  

class DisplayPlot():
    def __init__(self, show=False):
        self.show = show

# Determines what items get shown
class OutputFilters():
    def __init__(self):
        # Determines if any data is output
        self.used = False

        self.item_list = []

        self.bif = self.BasicItemFilters()
        self.lf = self.LatestFilters()
        self.a5mf = self.Avg5mFilters()
        self.a1hf = self.Avg1hFilters()
        self.s6hf = self.Series6hFilters()
        self.s12hf = self.Series12hFilters()
        self.s24hf = self.Series24hFilters()
        self.s1wf = self.Series1wFilters()
        self.s1mf = self.Series1mFilters()
        self.s1yf = self.Series1yFilters()

        # Init function is used in case it must be called manually
        # to update object whenver loaded from jsonpickle file
        self.init()

    # Must be called if loaded from json pickle, incase user makes any shanges to
    # the filters, since the init routine above won't be called.
    def init(self):
        # Do not show time range if user sets all data to false
        self.show_bif = self.are_any_shown(self.bif)
        self.show_lf = self.are_any_shown(self.lf)
        self.show_a5mf = self.are_any_shown(self.a5mf)
        self.show_a1hf = self.are_any_shown(self.a1hf)
        self.show_s6hf = self.are_any_shown(self.s6hf)
        self.show_s12hf = self.are_any_shown(self.s12hf)
        self.show_s24hf = self.are_any_shown(self.s24hf)
        self.show_s1wf = self.are_any_shown(self.s1wf)
        self.show_s1mf = self.are_any_shown(self.s1mf)
        self.show_s1yf = self.are_any_shown(self.s1yf)

        # Check if user has opted to show data for atleast one time range
        for attr in vars(self):
            # Skip non-booleans
            if (isinstance(getattr(self, attr), bool) != True):
                continue
            # If any data is to be shown, then this class is used
            # If not, program does not run
            if (getattr(self, attr) == True):
                self.used = True

    def are_any_shown(self, obj):
        for attr in vars(obj):
            inner_obj = getattr(obj, attr)    
            if (inner_obj.show == True):
                return True
        return False

    class BasicItemFilters():
        def __init__(self):
            self.item_name = Contains(show=True, string = "")
            self.item_id = Range(show=True)
            self.item_price = Range(show=True, min=200000, max=2000000)
            self.ge_limit = Range(show=True)

    class LatestFilters():
        def __init__(self):
            self.insta_sell_price = Range(show=False)           # Normal
            self.insta_sell_time_min = Range(show=False)        # Minutes
            self.insta_buy_price = Range(show=False)            # Normal
            self.insta_buy_time_min = Range(show=False)         # Minutes
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.margin_taxed = Range(show=False)               # Normal
            self.profit_per_limit = Range(show=False)           # Normal
            self.roi = Range(show=False)                        # Percent

    class Avg5mFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.avg_vol = Range(show=False)                    # Normal
            self.margin_taxed = Range(show=False)               # Normal
            self.profit_per_limit = Range(show=False)           # Normal
            self.roi_avg = Range(show=False)                    # Percent

    class Avg1hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.avg_vol = Range(show=False)                    # Normal
            self.margin_taxed = Range(show=False)               # Normal
            self.profit_per_limit = Range(show=False)           # Normal
            self.roi_avg = Range(show=False)                    # Percent

    class Series6hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=False)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = False)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                    # Percent
            self.insta_buy_change = Range(show=False)           # Normal
            self.insta_buy_change_percent = Range(show=False)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=False)    # Ratio
            self.insta_buy_cov = Range(show=False)              # Percent
            self.insta_sell_change = Range(show=False)          # Normal
            self.insta_sell_change_percent = Range(show=False)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=False)    # Ratio
            self.insta_sell_cov = Range(show=False)             # Percent
            self.price_change = Range(show=False)               # Normal
            self.price_change_percent = Range(show=False)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=False)     # Normal
            self.buy_vol_above_tunnel = Range(show=False)       # Normal
            self.tunnel_buy_opportunity = Range(show=False)     # Percent
            self.insta_sell_tunnel_price = Range(show=False)    # Normal
            self.sell_vol_below_tunnel = Range(show=False)      # Normal
            self.tunnel_sell_opportunity = Range(show=False)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=False)   # Normal
            self.tunnel_roi =  Range(show=False)                # Percent

    class Series12hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=True)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=True)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=True, min=200)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = True)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                   # Percent
            self.insta_buy_change = Range(show=True)           # Normal
            self.insta_buy_change_percent = Range(show=True)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=True)    # Ratio
            self.insta_buy_cov = Range(show=True)              # Percent
            self.insta_sell_change = Range(show=True)          # Normal
            self.insta_sell_change_percent = Range(show=True)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=True)    # Ratio
            self.insta_sell_cov = Range(show=True)              # Percent
            self.price_change = Range(show=False)               # Normal
            self.price_change_percent = Range(show=False)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=True)     # Normal
            self.buy_vol_above_tunnel = Range(show=True)       # Normal
            self.tunnel_buy_opportunity = Range(show=True)     # Percent
            self.insta_sell_tunnel_price = Range(show=True)    # Normal
            self.sell_vol_below_tunnel = Range(show=True)      # Normal
            self.tunnel_sell_opportunity = Range(show=True)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=True, min=150000)   # Normal
            self.tunnel_roi =  Range(show=True)                # Percent

    class Series24hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=False)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = False)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                    # Percent
            self.insta_buy_change = Range(show=False)           # Normal
            self.insta_buy_change_percent = Range(show=False)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=False)    # Ratio
            self.insta_buy_cov = Range(show=False)              # Percent
            self.insta_sell_change = Range(show=False)          # Normal
            self.insta_sell_change_percent = Range(show=False)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=False)    # Ratio
            self.insta_sell_cov = Range(show=False)             # Percent
            self.price_change = Range(show=False)               # Normal
            self.price_change_percent = Range(show=False)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=False)     # Normal
            self.buy_vol_above_tunnel = Range(show=False)       # Normal
            self.tunnel_buy_opportunity = Range(show=False)     # Percent
            self.insta_sell_tunnel_price = Range(show=False)    # Normal
            self.sell_vol_below_tunnel = Range(show=False)      # Normal
            self.tunnel_sell_opportunity = Range(show=False)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=False)   # Normal
            self.tunnel_roi =  Range(show=False)                # Percent

    class Series1wFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=False)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = True)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                    # Percent
            self.insta_buy_change = Range(show=False)           # Normal
            self.insta_buy_change_percent = Range(show=False)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=False)    # Ratio
            self.insta_buy_cov = Range(show=False)              # Percent
            self.insta_sell_change = Range(show=False)          # Normal
            self.insta_sell_change_percent = Range(show=False)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=False)    # Ratio
            self.insta_sell_cov = Range(show=False)             # Percent
            self.price_change = Range(show=True)               # Normal
            self.price_change_percent = Range(show=True)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=False)     # Normal
            self.buy_vol_above_tunnel = Range(show=False)       # Normal
            self.tunnel_buy_opportunity = Range(show=False)     # Percent
            self.insta_sell_tunnel_price = Range(show=False)    # Normal
            self.sell_vol_below_tunnel = Range(show=False)      # Normal
            self.tunnel_sell_opportunity = Range(show=False)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=False)   # Normal
            self.tunnel_roi =  Range(show=False)                # Percent

    class Series1mFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=False)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = False)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                    # Percent
            self.insta_buy_change = Range(show=False)           # Normal
            self.insta_buy_change_percent = Range(show=False)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=False)    # Ratio
            self.insta_buy_cov = Range(show=False)              # Percent
            self.insta_sell_change = Range(show=False)          # Normal
            self.insta_sell_change_percent = Range(show=False)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=False)    # Ratio
            self.insta_sell_cov = Range(show=False)             # Percent
            self.price_change = Range(show=False)               # Normal
            self.price_change_percent = Range(show=False)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=False)     # Normal
            self.buy_vol_above_tunnel = Range(show=False)       # Normal
            self.tunnel_buy_opportunity = Range(show=False)     # Percent
            self.insta_sell_tunnel_price = Range(show=False)    # Normal
            self.sell_vol_below_tunnel = Range(show=False)      # Normal
            self.tunnel_sell_opportunity = Range(show=False)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=False)   # Normal
            self.tunnel_roi =  Range(show=False)                # Percent

    class Series1yFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)              # Normal
            self.insta_buy_vol = Range(show=False)              # Normal
            self.insta_sell_avg = Range(show=False)             # Normal
            self.insta_sell_vol = Range(show=False)             # Normal
            self.price_avg = NoFilter(show=False)               # We use item_price as our price filter
            self.total_vol = Range(show=False)                  # Normal
            self.margin_taxed_avg = Range(show=False)           # Normal
            self.profit_per_limit_avg = Range(show=False)       # Normal
            self.plot = DisplayPlot(show = False)               # Plot
            
            # Changes and Percentages
            self.roi_avg = Range(show=False)                    # Percent
            self.insta_buy_change = Range(show=False)           # Normal
            self.insta_buy_change_percent = Range(show=False)   # Percent
            self.buy_over_sell_vol_ratio = Range(show=False)    # Ratio
            self.insta_buy_cov = Range(show=False)              # Percent
            self.insta_sell_change = Range(show=False)          # Normal
            self.insta_sell_change_percent = Range(show=False)  # Percent
            self.sell_over_buy_vol_ratio = Range(show=False)    # Ratio
            self.insta_sell_cov = Range(show=False)             # Percent
            self.price_change = Range(show=False)               # Normal
            self.price_change_percent = Range(show=False)       # Percent

            # Tunnel Data
            self.insta_buy_tunnel_price = Range(show=False)     # Normal
            self.buy_vol_above_tunnel = Range(show=False)       # Normal
            self.tunnel_buy_opportunity = Range(show=False)     # Percent
            self.insta_sell_tunnel_price = Range(show=False)    # Normal
            self.sell_vol_below_tunnel = Range(show=False)      # Normal
            self.tunnel_sell_opportunity = Range(show=False)    # Percent
            self.tunnel_margin_taxed = Range(show=False)        # Normal
            self.tunnel_profit_per_limit =  Range(show=False)   # Normal
            self.tunnel_roi =  Range(show=False)                # Percent


# Lowest level data
class Data():
    def __init__(self, used=False, value=0, string=""):
        self.used = used
        self.value = value
        self.string = string

    # Create underline for data string
    def show_underline(self, file, use_email):
        global email_msg
        line = ""
        string = self.string % (self.value)
        for c in string: 
            line = line + '-'
        
        print(line)
        if (file):
            file.write(line + "\n")
        if (use_email):
            email_msg = email_msg + line + "\n"    

    # Show data string as is
    def show(self, file, use_email):
        global email_msg
        if (self.used != True):
            return
        
        # Turn float or int into string with commas
        if ('%.2f' in self.string):
            string = self.string.replace('%.2f', '%s')
            val = com(self.value, 'f')
        elif ('%d' in self.string):
            string = self.string.replace('%d', '%s')
            val = com(self.value, 'd')
        else:
            string = self.string
            val = self.value    

        print(string % (val))
        if (file):
            file.write(string % (val) + "\n")
        if (use_email):
            email_msg = email_msg + string % (val) + "\n"

    # Show data string indented
    def showi(self, file, use_email):
        global email_msg
        if (self.used != True):
            return

        # Turn float or int into string with commas
        if ('%.2f' in self.string):
            string = self.string.replace('%.2f', '%s')
            val = com(self.value, 'f')
        elif ('%d' in self.string):
            string = self.string.replace('%d', '%s')
            val = com(self.value, 'd')
        else:
            string = self.string
            val = self.value    

        print("  " + string % (val))
        if (file):
            file.write("  " + string % (val) + "\n")
        if (use_email):
            email_msg = email_msg + "  " + string % (val) + "\n"

# Stores additional program configurations
class ConfigData():
    def __init__(self):
        self.plot_filename = None
        self.save_plots = None

        self.data_filename = None

        self.is_sorting = False
        self.data_path = None
        self.time_obj = None
        self.data_obj = None
        self.data_val = None

        self.email_creds = None
        self.send_plots = None


# Data for a single item
class ItemData():
    def __init__(self):
        self.used = True

        # Basic item data
        self.id = None
        self.name = None
        self.item_price = None
        self.ge_limit = None

        # Time range data objects
        self.ld = LatestData("Latest Data")
        self.a5md = AvgData("Average Last 5 Minutes Data")
        self.a1hd = AvgData("Average Last 1 Hour Data")
        self.s6hd = TimeSeriesData("Series Last 6 Hours Data")
        self.s12hd = TimeSeriesData("Series Last 12 Hours Data")
        self.s24hd = TimeSeriesData("Series Last 24 Hours Data")
        self.s1wd = TimeSeriesData("Series Last 1 Week Data")
        self.s1md = TimeSeriesData("Series Last 1 Month Data")
        self.s1yd = TimeSeriesData("Series Last 1 Year Data")
        
    def show(self, file, use_email):
        global email_msg
        self.name.show(file, use_email)  
        self.name.show_underline(file, use_email) 
        self.id.show(file, use_email)
        self.ge_limit.show(file, use_email)     
        self.item_price.show(file, use_email)
        print("")
        if (file):
            file.write("\n")
        if (use_email):
            email_msg = email_msg + "\n"    

# Latest Data
class LatestData():
    def __init__(self, desc):
        self.used = False
        self.desc = desc
        self.insta_buy_price = Data()
        self.insta_buy_time = Data()
        self.insta_buy_time_min = Data()        
        self.insta_sell_price = Data()
        self.insta_sell_time = Data()
        self.insta_sell_time_min = Data()
        self.price_avg = Data()
        self.margin = Data()
        self.margin_taxed = Data()
        self.profit_per_limit = Data()
        self.roi = Data()
    
    def show(self, file, use_email):
        global email_msg
        if (self.used == True):
            print("Latest:")
            if (file):
                file.write("Latest:\n")
            if (use_email):
                email_msg = email_msg + "Latest:\n"
            show_obj_data(self, file, use_email)

# 5m or 1h average data
class AvgData():
    def __init__(self, desc):
        self.used = False
        self.type = ""
        self.desc = desc

        self.insta_buy_avg = Data()
        self.insta_buy_vol = Data()
        self.insta_sell_avg = Data()
        self.insta_sell_vol = Data()
        self.avg_vol = Data()
        self.price_avg = Data()
        self.margin_taxed = Data()
        self.profit_per_limit = Data()  
        self.roi_avg = Data()

    def show(self, file, use_email):
        global email_msg
        if (self.used == True):
            print("%s Average:" % (self.type))
            if (file):
                file.write("%s Average:" % (self.type) + "\n")
            if (use_email):
                email_msg = email_msg + "%s Average:" % (self.type) + "\n"
            show_obj_data(self, file, use_email)

# Data for a timeseries
class TimeSeriesData():
    def __init__(self, desc):
        self.used = False
        self.type = ""
        self.desc = desc

        # TODO: Eventually want to automate finding the ideal percentiles here
        # - Where their profit margin meets user's filter requirement
        # - There are sufficient offers beyond the boundary to buy/sell
        #     - Could base on buy/sell opportunity and just let user tune
        #       because intelligently automating this is challenging since
        #       items vary in their price fluctations a ton even if we can
        #       measure cov, price changes, etc.
        #       In other words .. what is sufficient? That is difficult to find
        #       so unless a new idea comes along to solve that, let user decide.
        #
        self.insta_buy_tunnel_percentile = 60
        self.insta_sell_tunnel_percentile = 40

        # Basic Data
        self.insta_buy_avg = Data()
        self.insta_buy_vol = Data()
        self.insta_sell_avg = Data()
        self.insta_sell_vol = Data()
        self.total_vol = Data()
        self.price_avg = Data()
        self.margin_taxed_avg = Data()
        self.profit_per_limit_avg = Data()  

        # Changes and percents
        self.roi_avg = Data()
        self.insta_buy_change = Data()
        self.insta_buy_change_percent = Data()
        self.buy_over_sell_vol_ratio = Data()
        self.insta_buy_cov = Data()         # Cofficient of Variance
        self.insta_sell_change = Data()
        self.insta_sell_change_percent = Data()
        self.sell_over_buy_vol_ratio = Data()
        self.insta_sell_cov = Data()        # Coefficient of Variance
        self.price_change = Data()
        self.price_change_percent = Data()
        
        # Tunnel Data
        self.insta_buy_tunnel_price = Data()
        self.buy_vol_above_tunnel = Data()
        self.tunnel_buy_opportunity = Data()
        self.insta_sell_tunnel_price = Data()
        self.sell_vol_below_tunnel = Data()
        self.tunnel_sell_opportunity = Data()
        self.tunnel_margin_taxed = Data()
        self.tunnel_profit_per_limit = Data()
        self.tunnel_roi = Data()
    
        # Plot data
        self.show_plot = False
        self.plot_title = None
        self.insta_buy_times = None
        self.insta_buy_prices = None
        #self.insta_buy_tunnel_price = None
        self.insta_sell_times = None
        self.insta_sell_prices = None
        #self.insta_sell_tunnel_price = None

    # Plot data (Does not show the plot)
    def plot(self):

        # Do not plot data if not showing plot
        if (self.show_plot == False):
            return

        fig, axes = plt.subplots()

        # Plot insta sell data
        axes.plot(self.insta_sell_times, self.insta_sell_prices, color = 'blue', label = 'Instant Sell Price')

        # Plot insta sell tunnel line
        axes.axhline(y = self.insta_sell_tunnel_price.value, color = 'blue', linestyle = '-')

        # Plot insta buy data
        axes.plot(self.insta_buy_times, self.insta_buy_prices, color='red', label = 'Instant Buy Price')

        # Plot insta buy tunnel line
        axes.axhline(y = self.insta_buy_tunnel_price.value, color = 'red', linestyle = '-')

        # Label time
        # TODO: Eventually show time normally ..
        axes.set_xlabel('Time (Unix Timestamp)')

        # Label price
        axes.set_ylabel('Price')

        # Give title as name of item
        axes.set_title(self.plot_title)

        # Show legend for plot labels
        axes.legend()

    def show(self, file, use_email):
        global email_msg
        if (self.used == True):
            print("Last %s:" % (self.type))
            if (file):
                file.write("Last %s:" % (self.type) + "\n")
            if (use_email):
                email_msg = email_msg + "Last %s:" % (self.type) + "\n"    
            show_obj_data(self, file, use_email)

# Show data for a time range's Data() objects
def show_obj_data(obj, file, use_email):
    global email_msg
    for attr in vars(obj):
        #print(attr)
        data_obj = getattr(obj, attr)
        # Print data for Data() objects
        if (isinstance(data_obj, Data) == True):
            data_obj.showi(file, use_email)

    print("")
    if (file):
        file.write("\n")
    if (use_email):
        email_msg = email_msg + "\n"    

def show_data(config, itd_list):

    # Open file if user is saving data to the file
    if (config.data_filename):
        data_file = open(config.data_filename, "a")
    else:
        data_file = None

    # Check if user sending use_email, by checking for saved credentials
    if (config.email_creds):
        use_email = True
    else:
        use_email = False

    # Sort item list based on a value if user has opted to.
    if (config.is_sorting == True):
        itd_list = sorted(itd_list, key=attrgetter(config.data_path))

    for item in itd_list:

        # Print basic item data
        # Note, item data is shown differently from other data. (It's hardcoded)
        # TODO: Email message creation is handled horribly - Clean up eventually.
        item.show(data_file, use_email)

        # Show latest data
        item.ld.show(data_file, use_email)

        # Show average last 5 minutes
        item.a5md.show(data_file, use_email)

        # Show average last 1 hour
        item.a1hd.show(data_file, use_email)

        # Show last 6 hours
        item.s6hd.show(data_file, use_email)
        item.s6hd.plot()

        # Show last 12 hours
        item.s12hd.show(data_file, use_email)
        item.s12hd.plot()

        # Show last 24 hours
        item.s24hd.show(data_file, use_email)
        item.s24hd.plot()

        # Show last week
        item.s1wd.show(data_file, use_email)
        item.s1wd.plot()

        # Show last month
        item.s1md.show(data_file, use_email)
        item.s1md.plot()

        # Show last year
        item.s1yd.show(data_file, use_email)
        item.s1yd.plot()

    # Close file if used.
    if (config.data_filename):
        data_file.close()    

    # Save plots to pdf
    if (config.save_plots == True):
        save_plots_pdf(config.plot_filename)

    # Send email if user has opted to
    # TODO: Email message is not being tailored correctly .. not showing in email right.
    # Was showing everything except last 12 hour data.
    if (use_email == True):
        creds = config.email_creds
        sender = creds[0]
        recip = creds[0]
        passw = creds[1]

        # Port for SSL
        port = 465

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Get subject and body of email
        msg = EmailMessage()
        msg['Subject'] = "OSRS Flipping Tool"
        msg.set_content(email_msg)

        # Attach pdf with plot data
        if (config.send_plots == True):
            pdf_data = get_plot_pdf_data(config)
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='graph_data.pdf')

        # Login to gmail server and send email
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(sender, passw)
            server.sendmail(sender, recip, msg.as_string())

def get_plot_pdf_data(config):

    # Use existing pdf if user saved one. Otherwise, must create
    # a new pdf to send over email
    if (config.save_plots == True):
        with open(config.plot_filename, 'rb') as fp:
            pdf_data = fp.read()
    else:
        save_plots_pdf("temp.pdf")
        with open("temp.pdf", 'rb') as fp:
            pdf_data = fp.read()

        # Remove file once we have the data    
        os.remove("temp.pdf")

    return pdf_data

def save_plots_pdf(filename):
    p = PdfPages(filename)

    # get_fignums Return list of existing  
    # figure numbers 
    fig_nums = plt.get_fignums()   
    figs = [plt.figure(n) for n in fig_nums] 
    
    # iterating over the numbers in list 
    for fig in figs:  
        
        # and saving the files 
        fig.savefig(p, format='pdf')

    p.close()

# Check if user has opted to show plot for any of the 
# time series
def are_plots_used(ofs):
    
    if (ofs.s6hf.plot.show == True):
        return True

    if (ofs.s12hf.plot.show == True):
        return True

    if (ofs.s24hf.plot.show == True):
        return True

    if (ofs.s1wf.plot.show == True):
        return True

    if (ofs.s1mf.plot.show == True):
        return True

    if (ofs.s1yf.plot.show == True):
        return True                

    return False    

def convert_items_to_ids(item_list):
    id_list = []

    for item in item_list:
        id = find_item_id(item)
        id_list.append(id)

    return id_list

def show_sort_options():
    sort_data = ItemData()
    for obj_name in vars(sort_data):
        obj_data = getattr(sort_data, obj_name)
        if (isinstance(obj_data, LatestData) != True and \
            isinstance(obj_data, AvgData) != True and \
            isinstance(obj_data, TimeSeriesData) != True):
            continue
        
        print(obj_data.desc)
        for data_name in vars(obj_data):
            data = getattr(obj_data, data_name)
            if (isinstance(data, Data) != True):
                continue

            print("  " + obj_name + '.' + data_name)

        print("")     

def check_sort_options(ofs, config, sort_args):
    sort_option = sort_args
    opts = sort_option.split('.')
    time_name_d = opts[0]
    time_name_f = time_name_d[:-1] + 'f'
    sort_data = opts[1]
    exists = False
    for filter_name in vars(ofs):
        # Skip until we get a match
        if (time_name_f != filter_name):
            continue
        time_obj_f = getattr(ofs, filter_name)
        for data_name in vars(time_obj_f):
            # Skip until we get a match
            if (data_name != sort_data):
                continue
            exists = True
            # Check if data is used by filter
            data_f = getattr(time_obj_f, data_name)
            if (data_f.show != True):
                print("Sort option %s passed, but user has not opted to show this data" % (sort_option))
                return False

            # Save heiarchal objects for sorting later
            config.is_sorting = True
            data_path = sort_option + '.value'
            config.data_path = data_path

    if (exists == False):
        print("Invalid sort option: %s. See --sort-options" % (sort_option))
        return False
    
    # User gave a valid sort option
    return True

"""
filter_items()

Find items based on applied filters
"""
# TODO: Might want to turn some of the argument
# blobs into functions for neatness.
def filter_items(args):
    
    itd_list = []
    id_list = []

    config = ConfigData()

    # Show sort options
    if (args.sort_options):
        show_sort_options()      
        return

    # Do not let user load and save filter at same time
    if (args.load_filter and args.save_filter):
        print("Attempting to save and load filter simultaneously. Quitting.")

    # Check if user is loading existing filter as object
    if (args.load_filter):
        with open(args.load_filter, 'r') as f:
            #ofs = pickle.load(f) 
            r = f.read()
        ofs = jsonpickle.decode(r)
        ofs.init()
    else:        
        ofs = OutputFilters()
        if (ofs.used == False):
            print("User has opted to show no data. Quitting.")
            quit(1)

    # Check if user gave valid sort option.
    if (args.sort):
        can_sort = check_sort_options(ofs, config, args.sort)
        if (can_sort == False):
            quit(1)

    # Check if user is saving program's filter
    if (args.save_filter):
        s = jsonpickle.encode(ofs, indent=3)
        with open(args.save_filter, 'w') as f:
        #    pickle.dump(ofs, f)
            s = jsonpickle.encode(ofs, indent=3)
            f.write(s)
            return  

    # Ensure plot filters are used with --send-email or --save-plots
    # Otherwise, do not use at all.
    show_plots = are_plots_used(ofs)
    if ((args.save_plots or args.send_email) and show_plots == False):
        print("--save-plots and/or --save-email option given, but no filters are set to show plots.")
        quit(1)
    elif (show_plots == True and (args.save_plots == None and args.send_email == None)):
        print("Filter(s) set to show plots, but neither --save-plots or --save-email option not given.")
        quit(1)

    # User wants to save plots to pdf
    if (show_plots == True and args.save_plots):
        config.plot_filename = args.save_plots
        config.save_plots = True

    # User wants to send plots over email as pdf
    if (show_plots == True and args.send_email):
        config.send_plots = True

    # Check if user sending data to gmail
    if (args.send_email):
        with open(args.send_email, 'r') as file:
            email_creds = [line.strip() for line in file]
            config.email_creds = email_creds

    # Check if user is using items from a file list
    if (args.load_items):
        with open(args.load_items, 'r') as file:
            item_list = [line.strip() for line in file]
            id_list = convert_items_to_ids(item_list)

    # Check if user is saving data to a file
    if (args.save_data):
        config.data_filename = args.save_data

    # Find /latest items that pass basic filter
    id_list = apply_basic_filter(ofs, id_list)
    num_items = len(id_list)
    if (num_items > 500):
        print("%d Items passed basic filter.\nNot exceeding 200 items during testing" % (num_items))
        quit()

    # Return items that pass filter and return their data
    for item_id in id_list:
        itd = filter_item(item_id, ofs)
        if (itd.used == True):
            itd_list.append(itd)

    # Show all data user has opted to show
    show_data(config, itd_list)

    return
        
"""
filter_item():

Apply filters to an item and return item data string
"""
def filter_item(item_id, ofs):

    itd = ItemData()

    # Basic item filter
    bif = ofs.bif

    # Find item in item_map 
    item_entry = find_item_entry(int(item_id))
    if item_entry == None:
        itd.used = False
        return itd

    # Get item name and filter by name
    name = item_entry['name'] 
    f = bif.item_name.filter(name)
    if (f == False):
        itd.used = False
        return itd

    # Get ge buy limit if it exists
    if 'limit' in item_entry:
        limit = item_entry['limit']
    else:
        limit = None    
          
    # Filter by ge buy limit
    f = bif.ge_limit.filter(limit)
    if (f == False):
        itd.used = False
        return itd
    
    # Passed initial limit filter, get basic item data
    itd.id = Data(True, item_id, "Id: %s")
    itd.name = Data(True, name, "Name: %s")
    itd.ge_limit = Data(True, limit, "GE Buy Limit: %d")

    # Get latest data. Go to next item if no data
    # We MUST get this for filtering, even if latest data is not shown.
    latest_data = get_latest_data(itd, int(item_id), ofs)
    if itd.used == False:
        return itd

    itd.item_price = Data(True, int(latest_data.price_avg.value), "Price: %d")

    itd.ld = latest_data

    # TODO: move this to timeseries function instead
    # Get 24h data for last year
    """
    item_24h = get_json(ts_url, item_id=int(item_id), timestep="24h")
    
    # Get daily trade volume
    high_24h_vol = item_24h['data'][0]['highPriceVolume']
    low_24h_vol = item_24h['data'][0]['lowPriceVolume']
    total_24h_vol = high_24h_vol + low_24h_vol      
    total_24h_vol_c = format(total_24h_vol, ',d')
    
    # Get average daily trade volume for last year
    high_yr_vol = 0
    low_yr_vol = 0
    h_count = 0
    l_count = 0
    for item in item_24h['data']:
        h_vol = item['highPriceVolume']
        if (h_vol != None):
            h_count = h_count + 1
            high_yr_vol = high_yr_vol + h_vol
    
        l_vol = item['lowPriceVolume']
        if (l_vol != None):
            l_count = l_count + 1        
            low_yr_vol = low_yr_vol + l_vol
  
    high_yr_vol = int(high_yr_vol / h_count)
    low_yr_vol = int(low_yr_vol / l_count)
    avg_daily_vol = high_yr_vol + low_yr_vol
    avg_daily_vol_c = format(avg_daily_vol, ',d')
    """    

    # Get 5 minutes average data
    if (ofs.show_a5mf == True):
        itd.a5md = get_average_data(itd, int(item_id), ofs, "5m")
        if (itd.used == False):
            return itd

    # Get 1 hour average data
    if (ofs.show_a1hf == True):
        itd.a1hd = get_average_data(itd, int(item_id), ofs, "1h")
        if (itd.used == False):
            return itd

    # TODO: 6, 12, 24h can be consolidated.
    # Get last 6h data
    if (ofs.show_s6hf == True):
        itd.s6hd = get_timeseries_data(itd, int(item_id), ofs, "5m", 72)
        if (itd.used == False):
            return itd

    # Get last 12h data
    if (ofs.show_s12hf == True):
        itd.s12hd = get_timeseries_data(itd, int(item_id), ofs, "5m", 144)
        if (itd.used == False):
            return itd

    # Get last 24h data
    if (ofs.show_s24hf == True):
        itd.s24hd = get_timeseries_data(itd, int(item_id), ofs, "5m", 288)
        if (itd.used == False):
            return itd

    # Get last 1 week data
    if (ofs.show_s1wf == True):
        itd.s1wd = get_timeseries_data(itd, int(item_id), ofs, "1h", 168)
        if (itd.used == False):
            return itd

    # Get last 1 month data
    if (ofs.show_s1mf == True):
        itd.s1md = get_timeseries_data(itd, int(item_id), ofs, "6h", 112)
        if (itd.used == False):
            return itd

    # Get last 1 year data
    if (ofs.show_s1yf == True):
        itd.s1yd = get_timeseries_data(itd, int(item_id), ofs, "24h", 364)
        if (itd.used == False):
            return itd

    return itd

"""
apply_basic_filter()

Apply basic item filters and return list of items that pass through
"""
def apply_basic_filter(ofs, user_id_list):

    # Basic item filter
    bif = ofs.bif

    filtered_id_list = []

    # If list isn't empty, user has supplied their own list of items
    if user_id_list == []:
        data = latest_all['data']
    else:
        data = user_id_list    

    for item_id in data:
        # Find item in item_map 
        item_entry = find_item_entry(int(item_id))
        if item_entry == None:
            continue
        name = item_entry['name'] 

        #print(item_id)

        # Check if item limit exists
        if 'limit' in item_entry:
            limit = item_entry['limit']
        else:
            limit = 0
            
        # Check if ge limit passes filter    
        f = bif.ge_limit.filter(limit)
        if (f == False):
            continue
        
        # Get basic item data, fill in all just to be safe
        itd = ItemData()
        itd.id = Data(False, int(item_id), "")
        itd.name = Data(False, name, "")
        itd.ge_limit = Data(False, limit, "")    

        # Get latest data just for filtering price data
        latest_data = get_latest_data(itd, int(item_id), ofs)
        if (itd.used == False):
            continue

        filtered_id_list.append(item_id)

    return filtered_id_list   

def get_ideal_low_margin(data_ts, num_entries, num_steps, min_list, percentile):

    if (len(min_list) == 0):
        return 0

    # Find the min closest to a given percentile and preferably above
    # (e.g. percentile of .2 means 20% of the time, there is an opportunity
    #  to buy)
    num_items = 0
    num_lower = 0
    lowest_perc = 1
    highest_perc_below = 0
    closest_i = None
    closest_i_below = None
    for i in min_list:
        for x in range(num_entries, num_entries-num_steps, -1):
            item = data_ts[x]
            if (item['avgLowPrice'] == None):
                continue
            num_items = num_items + 1
            if (item['avgLowPrice'] < data_ts[i]['avgLowPrice']):
                num_lower = num_lower + 1

        # Compute local min closest to percentile above and below.
        perc = num_lower/num_items
        num_lower = 0
        num_items = 0
        if (perc >= percentile and closest_i == None):
            lowest_perc = perc
            closest_i = i
        elif (perc >= percentile and closest_i != None):
            if (perc < lowest_perc):
                lowest_perc = perc
                closest_i = i

        if (perc < percentile and closest_i_below == None):
            highest_perc_below = perc
            closest_i_below = i
        elif (perc < percentile and closest_i_below != None):
            if (perc > highest_perc_below):
                highest_perc_below = perc
                closest_i_below = i
    
    # TODO:
    # May eventually want to return more than the index .. we will see :)
    if closest_i != None:
        return closest_i
    else:
        return closest_i_below  
    

def get_ideal_high_margin(data_ts, num_entries, num_steps, max_list, percentile):
    
    if (len(max_list) == 0):
        return 0

    # Find the mmax closest to a given percentile and preferably below
    # (e.g. percentile of .2 means 20% of the time, there is an opportunity
    #  to sell)
    num_items = 0
    num_higher = 0
    highest_perc = 0
    lowest_perc_above = 1
    closest_i = None
    closest_i_above = None
    for i in max_list:
        for x in range(num_entries, num_entries-num_steps, -1):
            item = data_ts[x]
            if (item['avgHighPrice'] == None):
                continue
            num_items = num_items + 1
            if (item['avgHighPrice'] > data_ts[i]['avgHighPrice']):
                num_higher = num_higher + 1

        # Compute local max closest to percentile above and below.
        perc = num_higher/num_items
        num_higher = 0
        num_items = 0

        if (perc >= percentile and closest_i == None):
            highest_perc = perc
            closest_i = i
        elif (perc >= percentile and closest_i != None):
            if (perc < highest_perc):
                highest_perc = perc
                closest_i = i

        if (perc < percentile and closest_i_above == None):
            lowest_perc_above = perc
            closest_i_above = i
        elif (perc < percentile and closest_i_above != None):
            if (perc > lowest_perc_above):
                lowest_perc_above = perc
                closest_i_above = i

    # TODO:
    # May eventually want to return more than the index .. we will see :)
    if closest_i != None:
        return closest_i
    else:
        return closest_i_above     

def get_minima(min_list, data_ts, num_entries, num_steps, i):

    closest_left = 0
    closest_right = 0    

    # Find next non-null recent (left) insta sell indice
    j = i+1
    while (j <= num_entries): 
        if (data_ts[j]['avgLowPrice'] != None):
            closest_left = data_ts[j]['avgLowPrice']
            break
        if (j == num_entries):
            closest_left = None
        j = j+1
            
    # Find next non-null early (right) insta sell indice
    j = i-1
    while (j >= (num_entries-num_steps)):
        if (data_ts[j]['avgLowPrice'] != None):
            closest_right = data_ts[j]['avgLowPrice']
            break
        if (j == (num_entries-num_steps)):
            closest_right = None
        j = j-1

    # Edge case where there is no adjacent data
    if (closest_left == None and closest_right == None):
        min_list.append(i)
        return

    # Case where we are on the first index
    if (i == num_entries):
        if (data_ts[num_entries]['avgLowPrice'] < closest_right):
            min_list.append(num_entries)
        return

    # Case where we are on the last index
    if (i == (num_entries-num_steps)):
        if (data_ts[num_entries-num_steps]['avgLowPrice'] < closest_left):
            min_list.append(num_entries-num_steps)
        return

    # Case where there is no left data
    if (closest_left == None and closest_right != None):
        if (data_ts[i]['avgLowPrice'] < closest_right):
            min_list.append(i)
        return

    # Case where there is no right data
    if (closest_left != None and closest_right == None):
        if (data_ts[i]['avgLowPrice'] < closest_left):
            min_list.append(i)
        return

    # Case where there is left and right data
    if (closest_left > data_ts[i]['avgLowPrice'] < closest_right):
        min_list.append(i)
        return

def get_maxima(max_list, data_ts, num_entries, num_steps, i):

    closest_left = 0
    closest_right = 0    

    # Find next non-null recent (left) insta buy indice
    j = i+1
    while (j <= num_entries): 
        if (data_ts[j]['avgHighPrice'] != None):
            closest_left = data_ts[j]['avgHighPrice']
            break
        if (j == num_entries):
            closest_left = None
        j = j+1
            
    # Find next non-null early (right) insta buy indice
    j = i-1
    while (j >= (num_entries-num_steps)):
        if (data_ts[j]['avgHighPrice'] != None):
            closest_right = data_ts[j]['avgHighPrice']
            break
        if (j == (num_entries-num_steps)):
            closest_right = None
        j = j-1

    # Edge case where there is no adjacent data
    if (closest_left == None and closest_right == None):
        max_list.append(i)
        return

    # Case where we are on first index 
    if (i == num_entries and data_ts[num_entries]['avgHighPrice'] != None):
        if (data_ts[num_entries]['avgHighPrice'] > closest_right):
            max_list.append(num_entries)
        return

    # Case where we are on last index
    if (i == (num_entries-num_steps) and data_ts[num_entries-num_steps]['avgHighPrice'] != None):
        if (data_ts[num_entries-num_steps]['avgHighPrice'] > closest_left):
            max_list.append(num_entries-num_steps)
        return

    # Edge Case where there is no left data
    if (closest_left == None and closest_right != None):
        if (data_ts[i]['avgHighPrice'] > closest_right):
            max_list.append(i)
        return

    # Edge Case where there is no right data
    if (closest_left != None and closest_right == None):
        if (data_ts[i]['avgHighPrice'] > closest_left):
            max_list.append(i)
        return

    # Case where there is left and right data
    if (closest_left < data_ts[i]['avgHighPrice'] > closest_right):
        max_list.append(i)
        return


def get_earliest_ts_data(data_ts, key, num_entries, num_steps):
  
    data = None
    for i in range(0, num_steps-1):
        if (data_ts[num_entries-num_steps+i][key] != None):
            data = data_ts[num_entries-num_steps+i][key]
            break
  
    return data    
    
def get_current_ts_data(data_ts, key, num_entries, num_steps):
  
    data = None
    for i in range(0, num_steps-1):
        if (data_ts[num_entries-i][key] != None):
            data = data_ts[num_entries-i][key]
            break
  
    return data          
  
"""
get_latest_data()

Format a string for the /latest data
"""
def get_latest_data(itd, item_id, ofs):

    ld = LatestData("")

    # Latest filter
    lf = ofs.lf

    # Check if item does not exist in latest data
    if (str(item_id)) not in latest_all['data']:
        itd.used = False
        return ld

    # Check if user has opted to show latest data
    if (ofs.show_lf == True):
        ld.used = True

    latest = latest_all['data'][str(item_id)]
    
    # Get item's main data
    insta_buy_price = latest['high']
    insta_buy_time = latest['highTime']
    insta_sell_price = latest['low']
    insta_sell_time = latest['lowTime']
    
    # INSTA BUY/SELL DATA IS A REQUIREMENT for latest data

    # Check if there is insta buy data
    if (insta_buy_price == None):
        itd.used = False
        return ld
        
    # Check if there is insta sell data
    if (insta_sell_price == None):
        itd.used = False
        return ld

    # Check if insta buy passes filter
    f = lf.insta_buy_price.filter(insta_buy_price)
    if (f == False):
        itd.used = False
        return ld

    # Check if insta sell passes filter
    f = lf.insta_sell_price.filter(insta_sell_price)
    if (f == False):
        itd.used = False
        return ld

    price_avg = int((insta_sell_price + insta_buy_price)/2)

    # Check if price avg passes filter
    # Note: We use item price from basic filter for our price filter
    f = ofs.bif.item_price.filter(price_avg)
    if (f == False):
        itd.used = False
        return ld

    # Get last buy/sell time in minutes
    now = time.time()
    insta_buy_time_min = int((now - insta_buy_time)/60)
    insta_sell_time_min = int((now - insta_sell_time)/60)

    # Check if insta buy time passes filter
    f = lf.insta_buy_time_min.filter(insta_buy_time_min)
    if (f == False):
        itd.used = False
        return ld

    # Check if insta sell time passes filter
    f = lf.insta_sell_time_min.filter(insta_sell_time_min)
    if (f == False):
        itd.used = False
        return ld

    # Get margins and profit and roi
    margin_taxed = int((insta_buy_price*.99) - insta_sell_price)

    # Check if margin taxed passes filter
    f = lf.margin_taxed.filter(margin_taxed)
    if (f == False):
        itd.used = False
        return ld

    profit_per_limit = margin_taxed * itd.ge_limit.value

    # Check if profit per limit passes filter
    f = lf.profit_per_limit.filter(profit_per_limit)
    if (f == False):
        itd.used = False
        return ld

    roi = (margin_taxed / insta_sell_price)*100

    # Check if roi passes filter
    f = lf.roi.filter(roi)
    if (f == False):
        itd.used = False
        return ld

    # Store latest data
    ld.insta_sell_price = Data(lf.insta_sell_price.show, insta_sell_price, "Insta Sell Price: %d")
    ld.insta_sell_time_min = Data(lf.insta_sell_time_min.show, insta_sell_time_min, "Insta Sell Time: %d Min Ago")    
    ld.insta_buy_price = Data(lf.insta_buy_price.show, insta_buy_price, "Insta Buy Price: %d")
    ld.insta_buy_time_min = Data(lf.insta_buy_time_min.show, insta_buy_time_min, "Insta Buy Time: %d Min Ago")
    ld.price_avg = Data(lf.price_avg.show, price_avg, "Average Price: %d") 
    ld.margin_taxed = Data(lf.margin_taxed.show, margin_taxed, "Margin (Taxed): %d")
    ld.profit_per_limit = Data(lf.profit_per_limit.show, profit_per_limit, "Profit Per Limit: %d")
    ld.roi = Data(lf.roi.show, roi, "ROI: %.2f%%")

    return ld

"""
get_average_data()

Get data for 5m or 1h average
"""
def get_average_data(itd, item_id, ofs, avg_type):
    
    ad = AvgData("")
    ad.type = avg_type

    # Determine time range we are using.
    if (avg_type == "5m"):
        avg_all = avg_5m_all
        opt = ofs.a5mf
        if (ofs.show_a5mf == True):
            ad.used = True
    elif (avg_type == "1h"):
        avg_all = avg_1h_all
        opt = ofs.a1hf
        if (ofs.show_a1hf == True):
            ad.used = True
    else:
        print("Invalid time range for average data: %s" % (avg_type))
        quit(1)

    # TODO: Provide a string at least letting user know that no data was found.
    # Current behavior is to be blank
    # Format string if no data found for item
    if (str(item_id)) not in avg_all['data']:
        ad.used = False
        return ad

    avg = avg_all['data'][str(item_id)] 
      
    insta_buy_avg = avg['avgHighPrice']
    insta_buy_vol = avg['highPriceVolume']
    insta_sell_avg = avg['avgLowPrice']
    insta_sell_vol = avg['lowPriceVolume']  

    # Check if there is insta buy data
    if (insta_buy_vol == 0 or insta_buy_avg == None):
        ad.used = False     
        return ad
        
    # Check if there is insta sell data
    if (insta_sell_vol == 0 or insta_sell_avg == None):
        ad.used = False             
        return ad  
    
    # Check if insta buy avg passes filter
    f = opt.insta_buy_avg.filter(insta_buy_avg)
    if (f == False):
        itd.used = False
        return ad

    # Check if insta buy vol passes filter
    f = opt.insta_buy_vol.filter(insta_buy_vol)
    if (f == False):
        itd.used = False
        return ad  

    # Check if insta sell avg passes filter
    f = opt.insta_sell_avg.filter(insta_sell_avg)
    if (f == False):
        itd.used = False
        return ad  

    # Check if insta sell vol passes filter
    f = opt.insta_sell_vol.filter(insta_sell_vol)
    if (f == False):
        itd.used = False
        return ad

    avg_vol = insta_sell_vol + insta_buy_vol

    # Check if avg vol passes filter
    f = opt.avg_vol.filter(avg_vol)
    if (f == False):
        itd.used = False
        return ad

    price_avg = int((insta_buy_avg + insta_sell_avg)/2)

    # Check if price avg passes filter
    # Note: We use item price from basic filter for our price filter
    f = ofs.bif.item_price.filter(price_avg)
    if (f == False):
        itd.used = False
        return ad

    # Get margin, profit, roi
    margin_taxed = int((insta_buy_avg*.99) - insta_sell_avg)

    # Check if margin taxed passes filter
    f = opt.margin_taxed.filter(margin_taxed)
    if (f == False):
        itd.used = False
        return ad

    profit_per_limit = margin_taxed * itd.ge_limit.value

    # Check if margin taxed passes filter
    f = opt.profit_per_limit.filter(profit_per_limit)
    if (f == False):
        itd.used = False
        return ad

    roi_avg = (margin_taxed / insta_sell_avg)*100

    # Check if roi passes filter
    f = opt.roi_avg.filter(roi_avg)
    if (f == False):
        itd.used = False
        return ad

    ad.insta_buy_avg = Data(opt.insta_buy_avg.show, insta_buy_avg, "Average Insta Buy Price: %d")
    ad.insta_buy_vol = Data(opt.insta_buy_vol.show, insta_buy_vol, "Average Insta Buy Vol: %d")
    ad.insta_sell_avg = Data(opt.insta_sell_avg.show, insta_sell_avg, "Average Insta Sell Price: %d")
    ad.insta_sell_vol = Data(opt.insta_sell_vol.show, insta_sell_vol, "Average Insta Sell Vol: %d")
    ad.avg_vol = Data(opt.avg_vol.show, avg_vol, "Average Volume: %d")
    ad.price_avg = Data(opt.price_avg.show, price_avg, "Average Price: %d")
    ad.margin_taxed = Data(opt.margin_taxed.show, margin_taxed, "Average Margin (Taxed): %d")
    ad.profit_per_limit = Data(opt.profit_per_limit.show, profit_per_limit, "Average Profit Per Limit: %d")
    ad.roi_avg = Data(opt.roi_avg.show, roi_avg, "Average ROI: %.2f%%")

    return ad
    
def get_timeseries_data(itd, item_id, ofs, timestep, num_steps):

    if (num_steps < 0 or num_steps > 364):
        print("Timeseries steps must be from 0 to 364")
        quit(1)

    # Ensure timestep is a valid option
    if (timestep != "5m" and timestep != "1h" and timestep != "6h" and timestep != "24h"):
        print("Invalid timestep provided")
        quit(1)

    buy_count = 0
    sell_count = 0
    insta_sell_vol = 0
    insta_buy_vol = 0
    total_insta_sell_price = 0
    total_insta_buy_price = 0
    max_insta_sell_price = 0
    min_insta_sell_price = 0xffffffff
    max_insta_buy_price = 0
    min_insta_buy_price = 0xffffffff
    min_list = []
    max_list = []
    insta_sell_prices = []
    insta_buy_prices = []
    insta_buy_vols = []
    insta_sell_vols = []
    insta_sell_times = []
    insta_buy_times = []

    tsd = TimeSeriesData("")  

    # TODO: 6 & 12 can be gotten from 24.
    # Get time range user options
    # 6 Hours
    if (timestep == "5m" and num_steps == 72):
        opt = ofs.s6hf
        tsd.type = "6 Hours"
        if (ofs.show_s6hf == True):
            tsd.used = True
    # 12 Hours
    if (timestep == "5m" and num_steps == 144):
        opt = ofs.s12hf
        tsd.type = "12 Hours"
        if (ofs.show_s12hf == True):
            tsd.used = True
    # 24 Hours
    if (timestep == "5m" and num_steps == 288):
        opt = ofs.s24hf
        tsd.type = "24 Hours"
        if (ofs.show_s24hf == True):
            tsd.used = True
    # 1 Week
    if (timestep == "1h" and num_steps == 168):
        opt = ofs.s1wf
        tsd.type = "Week"
        if (ofs.show_s1wf == True):
            tsd.used = True
    # 1 Month
    if (timestep == "6h" and num_steps == 112):
        tsd.type = "Month"
        opt = ofs.s1mf
        if (ofs.show_s1mf == True):
            tsd.used = True
    # 1 Year
    if (timestep == "24h" and num_steps == 364):
        opt = ofs.s1yf
        tsd.type = "Year"
        if (ofs.show_s1yf == True):
            tsd.used = True

    # Get timestep data (365 datapoints, higher numbers are more recent)    
    data_ts = get_json(ts_url, item_id=item_id, timestep=timestep)
    data_ts = data_ts['data']

    # Get the number of time series entries. If there are less entries
    # than the number of steps, then adjust it.
    num_entries = len(data_ts) - 1
    if (num_entries < num_steps):
        num_steps = num_entries

    # Get earliest data
    first_insta_buy_time = get_earliest_ts_data(data_ts, "timestamp", num_entries, num_steps)
    first_insta_buy_avg = get_earliest_ts_data(data_ts, "avgHighPrice", num_entries, num_steps)
    first_insta_sell_avg = get_earliest_ts_data(data_ts, "avgLowPrice", num_entries, num_steps)
    
    # Get most recent data
    curr_insta_buy_time = get_current_ts_data(data_ts, "timestamp", num_entries, num_steps)
    curr_insta_buy_avg = get_current_ts_data(data_ts, "avgHighPrice", num_entries, num_steps)
    curr_insta_sell_avg = get_current_ts_data(data_ts, "avgLowPrice", num_entries, num_steps)

    # If there is no first or last data then don't use tsd, but may 
    # use other time frames (e.g. latest)
    # TODO: Let user know there is no data for this.
    if (curr_insta_buy_avg == None or curr_insta_sell_avg == None or\
        first_insta_buy_avg == None or first_insta_sell_avg == None):
        price_change = None
        price_change_percent = None
        tsd.used = False
        return tsd

    # Get insta buy change data
    insta_buy_change = curr_insta_buy_avg - first_insta_buy_avg
    insta_buy_change_percent = (insta_buy_change/first_insta_buy_avg)*100

    # Get insta sell change data
    insta_sell_change = curr_insta_sell_avg - first_insta_sell_avg
    insta_sell_change_percent = (insta_sell_change/first_insta_sell_avg)*100

    # Get average price change data
    first_insta_price_avg = (first_insta_sell_avg + first_insta_buy_avg)/2     
    curr_insta_price_avg = (curr_insta_sell_avg + curr_insta_buy_avg)/2
    price_change = int(curr_insta_price_avg - first_insta_price_avg)
    price_change_percent = (price_change / first_insta_price_avg)*100

    # Check if price change passes filter
    f = opt.price_change.filter(price_change)
    if (f == False):
        itd.used = False
        return tsd

    # Check if price change percent passes filter
    f = opt.price_change_percent.filter(price_change_percent)
    if (f == False):
        itd.used = False
        return tsd

    # Loop entries from most recent to earliest
    # TODO: Why do I loop this direction???? It plots correctly still .. 
    for i in range(num_entries, num_entries-num_steps, -1):
        entry = data_ts[i]

        # Get insta sell price data
        if (entry['avgLowPrice'] != None):
            insta_sell_price = entry['avgLowPrice']
            insta_sell_prices.append(insta_sell_price)
            insta_sell_times.append(entry['timestamp'])
            total_insta_sell_price = total_insta_sell_price + insta_sell_price
            insta_sell_vols.append(entry['lowPriceVolume'])
            insta_sell_vol = insta_sell_vol + entry['lowPriceVolume']
            sell_count = sell_count + 1
            # Get highest sell price
            if (max_insta_sell_price < insta_sell_price):
                max_insta_sell_price = insta_sell_price
                max_isp_ts = entry['timestamp']
            # Get lowest sell price
            if (min_insta_sell_price > insta_sell_price):
                min_insta_sell_price = insta_sell_price
                min_isp_ts = entry['timestamp']
            # Get all local minima into a list
            #get_minima(min_list, data_ts, num_entries, num_steps, i)

        # Get insta buy price data
        if (entry['avgHighPrice'] != None):
            insta_buy_price = entry['avgHighPrice']
            insta_buy_prices.append(insta_buy_price)
            insta_buy_times.append(entry['timestamp'])
            total_insta_buy_price = total_insta_buy_price + insta_buy_price
            insta_buy_vols.append(entry['highPriceVolume'])
            insta_buy_vol = insta_buy_vol + entry['highPriceVolume']
            buy_count = buy_count + 1
            # Get highest buy price
            if (max_insta_buy_price < insta_buy_price):
                max_insta_buy_price = insta_buy_price
                max_ibp_ts = entry['timestamp']
            # Get lowest buy price
            if (min_insta_buy_price > insta_buy_price):
                min_insta_buy_price = insta_buy_price
                min_ibp_ts = entry['timestamp']
            # Get all local maxima into a list
            #get_maxima(max_list, data_ts, num_entries, num_steps, i)
 
    # Get total trade volume
    total_vol = insta_sell_vol + insta_buy_vol
    f = opt.total_vol.filter(total_vol)
    if (f == False):
        itd.used = False
        return tsd

    # Get buy over sell volume ratio
    buy_over_sell_vol_ratio = insta_buy_vol / insta_sell_vol

    # Get sell over buy volume ratio
    sell_over_buy_vol_ratio = insta_sell_vol / insta_buy_vol

    # Get average volume for each timestep
    # TODO: Make the avg vol a filter item?
    #avg_vol = int(total_vol/num_steps)
    #avg_insta_sell_vol = int(insta_sell_vol/num_steps)
    #avg_insta_buy_vol = int(insta_buy_vol/num_steps)

    if (sell_count == 0):
        itd.used = False
        return tsd

    # Check if insta sell avg passes filter
    insta_sell_avg = int(total_insta_sell_price/sell_count)
    f = opt.insta_sell_avg.filter(insta_sell_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Check if insta sell vol passes filter
    f = opt.insta_sell_vol.filter(insta_sell_vol)
    if (f == False):
        itd.used = False
        return tsd

    if (buy_count == 0):
        itd.used = False
        return tsd

    # Check if insta buy avg passes filter
    insta_buy_avg = int(total_insta_buy_price/buy_count)
    f = opt.insta_buy_avg.filter(insta_buy_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Check if insta buy vol passes filter
    f = opt.insta_sell_vol.filter(insta_buy_vol)
    if (f == False):
        itd.used = False
        return tsd

    # Check if price avg passes filter
    # Note: We use item price from basic filter for our price filter
    price_avg = (insta_buy_avg + insta_sell_avg)/2
    f = ofs.bif.item_price.filter(price_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Check if margin taxed avg passes filter
    margin_taxed_avg = int((insta_buy_avg*.99 - insta_sell_avg))
    f = opt.margin_taxed_avg.filter(margin_taxed_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Check if profit per limit avg passes filter
    profit_per_limit_avg = margin_taxed_avg * itd.ge_limit.value
    f = opt.profit_per_limit_avg.filter(profit_per_limit_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Check if roi avg passes filter
    roi_avg = (margin_taxed_avg / insta_sell_avg)*100
    f = opt.roi_avg.filter(roi_avg)
    if (f == False):
        itd.used = False
        return tsd

    # Get our buying price based on the sell data
    #low_i = get_ideal_low_margin(data_ts, num_entries, num_steps, min_list, .2)

    # Get our selling price based on the buy data
    #high_i = get_ideal_high_margin(data_ts, num_entries, num_steps, max_list, .2) 

    # Get insta buy tunnel price
    insta_buy_tunnel_price = int(np.percentile(insta_buy_prices, tsd.insta_buy_tunnel_percentile))
    f = opt.insta_buy_tunnel_price.filter(insta_buy_tunnel_price)
    if (f == False):
        itd.used = False
        return tsd

    # Get insta sell tunnel price
    insta_sell_tunnel_price = int(np.percentile(insta_sell_prices, tsd.insta_sell_tunnel_percentile))
    f = opt.insta_sell_tunnel_price.filter(insta_sell_tunnel_price)
    if (f == False):
        itd.used = False
        return tsd

    # Get buy volume above buy tunnel
    buy_vol_above_tunnel = get_buy_vol_above_tunnel(insta_buy_prices, insta_buy_vols, insta_buy_tunnel_price)
    f = opt.buy_vol_above_tunnel.filter(buy_vol_above_tunnel)
    if (f == False):
        itd.used = False
        return tsd

    # Get sell volume below tunnel
    sell_vol_below_tunnel = get_sell_vol_below_tunnel(insta_sell_prices, insta_sell_vols, insta_sell_tunnel_price)
    f = opt.sell_vol_below_tunnel.filter(sell_vol_below_tunnel)
    if (f == False):
        itd.used = False
        return tsd    

    # Get tunnel buy opportunity percent
    tunnel_buy_opportunity = (sell_vol_below_tunnel / insta_sell_vol)*100
    f = opt.tunnel_buy_opportunity.filter(tunnel_buy_opportunity)
    if (f == False):
        itd.used = False
        return tsd   

    # Get tunnel sell opportunity percent
    tunnel_sell_opportunity = (buy_vol_above_tunnel / insta_buy_vol)*100
    f = opt.tunnel_sell_opportunity.filter(tunnel_sell_opportunity)
    if (f == False):
        itd.used = False
        return tsd

    # Get tunnel margin taxed
    tunnel_margin_taxed = int((insta_buy_tunnel_price*.99) - insta_sell_tunnel_price)
    f = opt.tunnel_margin_taxed.filter(tunnel_margin_taxed)
    if (f == False):
        itd.used = False
        return tsd

    # Get tunnel profit per limit
    # TODO: Some values are insanely large .. what is up with that?
    tunnel_profit_per_limit = tunnel_margin_taxed * itd.ge_limit.value
    f = opt.tunnel_profit_per_limit.filter(tunnel_profit_per_limit)
    if (f == False):
        itd.used = False
        return tsd

    # Get tunnel return on investment
    tunnel_roi = (tunnel_profit_per_limit / insta_sell_tunnel_price)*100
    f = opt.tunnel_roi.filter(tunnel_roi)
    if (f == False):
        itd.used = False
        return tsd    

    # Get standard deviation for buy and sell data 
    insta_buy_std = np.std(insta_buy_prices)
    insta_sell_std = np.std(insta_sell_prices)

    # Get insta buy coefficient of variance
    insta_buy_cov = (insta_buy_std/insta_buy_avg)*100
    f = opt.insta_buy_cov.filter(insta_buy_cov)
    if (f == False):
        itd.used = False
        return tsd

    # Get insta sell coefficient of variance
    insta_sell_cov = (insta_sell_std/insta_sell_avg)*100
    f = opt.insta_sell_cov.filter(insta_sell_cov)
    if (f == False):
        itd.used = False
        return tsd

    # Only plot if used has opted to 
    # TODO: Plot to show dots at each data point within the lines
    if (opt.plot.show == True):
        tsd.show_plot = True
        item = find_item_entry(item_id)

        # Get plot data
        tsd.plot_title = item['name'] + " " + '(' + tsd.type + ')'

        # Get insta buy data
        tsd.insta_buy_times = insta_buy_times
        tsd.insta_buy_prices = insta_buy_prices

        # Get insta buy tunnel line
        tsd.insta_buy_tunnel_price = insta_buy_tunnel_price

        # Get insta sell data
        tsd.insta_sell_times = insta_sell_times
        tsd.insta_sell_prices = insta_sell_prices

        # Get insta sell tunnel line
        tsd.insta_sell_tunnel_price = insta_sell_tunnel_price


    tsd.insta_buy_avg = Data(opt.insta_buy_avg.show, insta_buy_avg, "Insta Buy Price (Average): %d")
    tsd.insta_buy_vol = Data(opt.insta_buy_vol.show, insta_buy_vol, "Insta Buy Volume: %d")
    tsd.insta_sell_avg = Data(opt.insta_sell_avg.show, insta_sell_avg, "Insta Sell Price (Average): %d")
    tsd.insta_sell_vol = Data(opt.insta_sell_vol.show, insta_sell_vol, "Insta Sell Volume: %d")
    tsd.total_vol = Data(opt.total_vol.show, total_vol, "Total Volume: %d")
    tsd.price_avg = Data(opt.price_avg.show, price_avg, "Price (Average): %d")
    tsd.margin_taxed_avg = Data(opt.margin_taxed_avg.show, margin_taxed_avg, "Margin (Average Taxed): %d")
    tsd.profit_per_limit_avg = Data(opt.profit_per_limit_avg.show, profit_per_limit_avg, "Profit Per Limit (Average): %d")

    tsd.roi_avg = Data(opt.roi_avg.show, roi_avg, "ROI (Average): %.2f%%")
    tsd.insta_buy_change = Data(opt.insta_buy_change.show, insta_buy_change, "Insta Buy Change: %d")
    tsd.insta_buy_change_percent = Data(opt.insta_buy_change_percent.show, insta_buy_change_percent, "Insta Buy Change Percent: %.2f%%")
    tsd.buy_over_sell_vol_ratio = Data(opt.buy_over_sell_vol_ratio.show, buy_over_sell_vol_ratio, "Buy/Sell Vol Ratio: %.2f")
    tsd.insta_buy_cov = Data(opt.insta_buy_cov.show, insta_buy_cov, "Insta Buy CoV: %.2f%%")
    tsd.insta_sell_change = Data(opt.insta_sell_change.show, insta_sell_change, "Insta Sell Change: %d")
    tsd.insta_sell_change_percent = Data(opt.insta_sell_change_percent.show, insta_sell_change_percent, "Insta Sell Change Percent: %.2f%%")
    tsd.sell_over_buy_vol_ratio = Data(opt.sell_over_buy_vol_ratio.show, sell_over_buy_vol_ratio, "Sell/Buy Vol Ratio: %.2f")
    tsd.insta_sell_cov = Data(opt.insta_sell_cov.show, insta_sell_cov, "Insta Sell CoV: %.2f%%")
    tsd.price_change = Data(opt.price_change.show, price_change, "Price Change: %d")
    tsd.price_change_percent = Data(opt.price_change_percent.show, price_change_percent, "Price Change Percent: %.2f%%")

    tsd.insta_buy_tunnel_price = Data(opt.insta_buy_tunnel_price.show, insta_buy_tunnel_price, "Insta Buy Tunnel Price: %d")
    tsd.buy_vol_above_tunnel = Data(opt.buy_vol_above_tunnel.show, buy_vol_above_tunnel, "Buy Volume Above Tunnel: %d")
    tsd.tunnel_buy_opportunity = Data(opt.tunnel_buy_opportunity.show, tunnel_buy_opportunity, "Tunnel Buy Opportunity: %.2f%%")
    tsd.insta_sell_tunnel_price = Data(opt.insta_sell_tunnel_price.show, insta_sell_tunnel_price, "Insta Sell Tunnel Price: %d")
    tsd.sell_vol_below_tunnel = Data(opt.sell_vol_below_tunnel.show, sell_vol_below_tunnel, "Sell Volume Below Tunnel: %d")
    tsd.tunnel_sell_opportunity = Data(opt.tunnel_sell_opportunity.show, tunnel_sell_opportunity, "Tunnel Sell Opportunity: %.2f%%")
    tsd.tunnel_margin_taxed = Data(opt.tunnel_margin_taxed.show, tunnel_margin_taxed, "Tunnel Margin Taxed: %d")
    tsd.tunnel_profit_per_limit = Data(opt.tunnel_profit_per_limit.show, tunnel_profit_per_limit, "Tunnel Profit Per Limit: %d")
    tsd.tunnel_roi = Data(opt.tunnel_roi.show, tunnel_roi, "Tunnel ROI: %.2f%%")

    return tsd

def get_buy_vol_above_tunnel(insta_buy_prices, insta_buy_vols, insta_buy_tunnel_price):
    
    # Ensure lists of same size
    num_trades = len(insta_buy_prices)
    if (num_trades != len(insta_buy_vols)):
        print("Length of buy prices and buy volumes does not match.")
        quit(1)

    # Average volume and price should coincide at same indices
    buy_vol_above_tunnel = 0
    for i in range(0, num_trades):
        avg_price = insta_buy_prices[i]

        # Count buy volume above tunnel
        if (avg_price >= insta_buy_tunnel_price):
            buy_vol_above_tunnel = buy_vol_above_tunnel + insta_buy_vols[i]


    return buy_vol_above_tunnel


def get_sell_vol_below_tunnel(insta_sell_prices, insta_sell_vols, insta_sell_tunnel_price):
    
    # Ensure lists of same size
    num_trades = len(insta_sell_prices)
    if (num_trades != len(insta_sell_vols)):
        print("Length of sell prices and sell volumes does not match.")
        quit(1)

    # Average volume and price should coincide at same indices
    sell_vol_below_tunnel = 0
    for i in range(0, num_trades):
        avg_price = insta_sell_prices[i]

        # Count buy volume above tunnel
        if (avg_price <= insta_sell_tunnel_price):
            sell_vol_below_tunnel = sell_vol_below_tunnel + insta_sell_vols[i]


    return sell_vol_below_tunnel


"""
com()

Return comma separated string given an intger or float
"""
def com(value, type):
    if (type == 'd'):
        return format(value, ',d')
    if (type == 'f'):
        return format(value, ',.2f')    

"""
find_item_entry()

Finds item entry in map given its id
"""
def find_item_entry(item_id):
    for item in item_map:
        if (item['id'] == item_id):        
            return item
    
    #print("Could not find item for item id: %d" % (item_id))

    return None

def find_item_name(item_id):
    item = find_item_entry(item_id)
    return item['name']

"""
find_item_id()

Finds an item's id given a name
"""    
def find_item_id(name):

    # Ensure first letter is uppercase
    name = name.capitalize()    
           
    # Ensure other letters are lowercase
    name = name[0] + name[1:].lower()
    
    for item in item_map:
        if (item['name'] == name):
            return item['id']
            
    print("Could not find name for item name: %s" % (name))
    quit(1) 
    

"""
get_json()

Get json table from API url passing optional arguments:
item_id: Retrieves data for a particular item
timestamp: Return 5m or 1h prices at this timestamp
timestep: Required for obtaining timeseries. Timestep of the series (5m, 1h, 6h, 24h)
          To a max up 365 data points          
"""
def get_json(url, *args, **kwargs):
    item_id = kwargs.get('item_id', None)
    timestamp = kwargs.get('timestamp', None)
    timestep = kwargs.get('timestep', None)
    
    # Perform error checking and add optional query parameters
    num_opt_args = 0
    if (item_id is not None):
        num_opt_args = num_opt_args + 1
        if (item_id < 0):
            print("item_id must be 0 or greater")
            quit(1)
            
        if num_opt_args == 1:
            url = url + '?id=' + str(item_id)
        elif num_opt_args > 1:
            url = url + '&id=' + str(item_id)
    
    if (timestamp is not None):
        num_opt_args = num_opt_args + 1
        if (timestamp < 0):
            print("timestamp must be 0 or greater")
            quit(1)    

        if num_opt_args == 1:
            url = url + '?timestamp=' + str(timestamp)
        elif num_opt_args > 1:
            url = url + '&timestamp=' + str(timestamp)
    
    if (timestep is not None):
        num_opt_args = num_opt_args + 1
        if (timestep != "5m" and timestep != "1h" and timestep != "6h" and timestep != "24h"):
            print("timestep must be 5m, 1h, 6h, or 24h")
            quit(1)

        if num_opt_args == 1:
            url = url + '?timestep=' + timestep
        elif num_opt_args > 1:
            url = url + '&timestep=' + timestep

    req = urllib.request.Request(url, 
                                 data=None, 
                                 headers= {'User-Agent': 'Testing Flipping Tool',
                                           'From': 'austinjp99@gmail.com' }) 

    with urllib.request.urlopen(req) as response: 
      body = response.read()  
      
    return json.loads(body)
    


def main():

    # Get all data now, so we do not have to loop later.
    global item_map, latest_all, avg_5m_all, avg_1h_all

    item_map = get_json(map_url)
    latest_all = get_json(latest_url)
    avg_5m_all = get_json(five_url)
    avg_1h_all = get_json(hour_url)

    parser = argparse.ArgumentParser(description='OSRS Flipping Tool')
    parser.add_argument('-p', '--save-plots',
                        help='Save plots to PDF.',
                        metavar=('<file_name>.pdf'),
                        dest='save_plots')	

    parser.add_argument('-F', '--load-filter',
                        help='Load existing filter file (.pkl)',
                        metavar=('<file_name>.pkl'),
                        dest='load_filter')	

    # TODO: Add argument to show a .pkl file's contents (filters or arguments)
    parser.add_argument('-f', '--save-filter',
                        help='Save programs current filter to file (.pkl)',
                        metavar=('<file_name>.pkl'),
                        dest='save_filter')
    
    parser.add_argument('-a', '--save-program',
                        help='Save programs arguments for easy repeated use.\nArguments will not be saved if program is unsuccessful.',
                        metavar=('<file_name>.pkl'),
                        dest='save_args')    

    parser.add_argument('-A', '--load-program',
                        help='Load program arguments from a previous run.',
                        metavar=('<file_name>.pkl'),
                        dest='load_args')    

    parser.add_argument('-I', '--load-items',
                        help='Load item list from a file. Each item should be on its own line.',
                        metavar=('<file_name>.txt'),
                        dest='load_items')

    parser.add_argument('-x', '--sort-options',
                        help='Show data options to sort items by',
                        action='store_true',
                        dest='sort_options')    

    parser.add_argument('-s', '--sort',
                        help='Sort items based on a sort option. See --sort-options for a list of options',
                        metavar=('<sort option>'),
                        dest='sort')                        

    parser.add_argument('-d', '--save_data',
                        help='Save outputted item data to a file',
                        metavar=('<file_name>'),
                        dest='save_data')      

    parser.add_argument('-e', '--send-email',
                        help='Send data to gmail',
                        metavar=('File containing username and app password on separate lines'),
                        dest='send_email')                         

    args = parser.parse_args()

    filter_items(args)
    

if __name__ == "__main__":
    main()
    
