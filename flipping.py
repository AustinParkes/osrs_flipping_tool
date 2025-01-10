#!/usr/bin/env python3
"""  
Script for obtaining pricing data from osrs real time prices:
    https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices 
"""

import urllib.request
import json
import time
from matplotlib import pyplot

# Keep urls global to access with any function
api_url = 'https://prices.runescape.wiki/api/v1/osrs'
latest_url = api_url + '/latest'
map_url = api_url + '/mapping'
five_url = api_url + '/5m'
hour_url = api_url + '/1h'
ts_url = api_url + '/timeseries'

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

class Plot():
    def __init__(self, show=False):
        self.show = show

#TODO: separate filters via timeranges.
# - can probably make some reusable classes (timeseries, avg)
# Determines what items get shown
class OutputFilters():
    def __init__(self):
        # Determines if any data is output
        self.used = False

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
            self.item_price = Range(show=True, min=190, max=210)
            self.ge_limit = Range(show=True, min=5000, max=25000)

    class LatestFilters():
        def __init__(self):
            self.insta_sell_price = Range(show=False)
            self.insta_sell_time_min = Range(show=False)
            self.insta_buy_price = Range(show=False)
            self.insta_buy_time_min = Range(show=False)
            self.price_avg = Range(show=False) # Do not modify
            self.margin_taxed = Range(show=False)
            self.profit_per_limit = Range(show=False)
            self.roi = Range(show=True)    

    class Avg5mFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.avg_vol = Range(show=False)
            self.margin_taxed = Range(show=False)
            self.profit_per_limit = Range(show=False)
            self.roi_avg = Range(show=False)        

    class Avg1hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.avg_vol = Range(show=False)
            self.margin_taxed = Range(show=False)
            self.profit_per_limit = Range(show=False)
            self.roi_avg = Range(show=False)  

    class Series6hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False) 
            self.plot = Plot(show = False)  

    class Series12hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False) 
            self.plot = Plot(show = False)

    class Series24hFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False) 
            self.plot = Plot(show = False)

    class Series1wFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False) 
            self.plot = Plot(show = False)

    class Series1mFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False) 
            self.plot = Plot(show = False)  

    class Series1yFilters():
        def __init__(self):
            self.insta_buy_avg = Range(show=False)
            self.insta_buy_vol = Range(show=False)
            self.insta_sell_avg = Range(show=False)
            self.insta_sell_vol = Range(show=False)
            self.price_avg = Range(show=False) # Do not use
            self.total_vol = Range(show=False)
            self.margin_taxed_avg = Range(show=False)
            self.profit_per_limit_avg = Range(show=False)
            self.price_change = Range(show=False)
            self.price_change_percent = Range(show=False)
            self.roi_avg = Range(show=False)           
            self.plot = Plot(show = False)                                                                                  


# Lowest level data
# TODO: Can initializing all Data() objects with Data()
# IF AND ONLY IF its useful. (They are initted to None currently)
class Data():
    def __init__(self, used=False, value=None, string=""):
        self.used = used
        self.value = value
        self.string = string

    # Create underline for data string
    def show_underline(self):
        line = ""
        string = self.string % (self.value)
        for c in string: 
            line = line + '-'
        
        print(line)

    # Show data string as is
    def show(self):
        if (self.used != True):
            return
        if (isinstance(self.value, int)):
            print(self.string % (com(self.value)))
        else:
            print(self.string % (self.value))

    # Show data string indented
    def showi(self):
        if (self.used != True):
            return
        if (isinstance(self.value, int)):
            print("  " + self.string % (com(self.value)))
        else:
            print("  " + self.string % (self.value))

    # Show data without newline
    def show_no_nl(self):        
        if (self.used == True):
            print(self.string % (self.value), end = "")


# Basic Item Data
class ItemData():
    def __init__(self):
        self.used = True

        # Basic item data
        self.id = None
        self.name = None
        self.ge_limit = None

        # Time range data objects
        self.ld = LatestData()
        self.avg_5m_data = AvgData()
        self.avg_1h_data = AvgData()
        self.series_6h_data = TimeSeriesData()
        self.series_12h_data = TimeSeriesData()
        self.series_24h_data = TimeSeriesData()
        self.series_1w_data = TimeSeriesData()
        self.series_1m_data = TimeSeriesData()
        self.series_1y_data = TimeSeriesData()
        
    def show(self):
        self.name.show()  
        self.name.show_underline() 
        self.id.show()
        self.ge_limit.show()     
        print("")

# Latest Data
class LatestData():
    def __init__(self):
        self.used = False
        self.insta_sell_price = None
        self.insta_sell_time = None
        self.insta_sell_time_min = None
        self.insta_buy_price = None
        self.insta_buy_time = None
        self.insta_buy_time_min = None
        self.price_avg = None
        self.margin = None
        self.margin_taxed = None
        self.profit_per_limit = None
        self.roi = None
    
    def show(self):
        if (self.used == True):
            print("Latest:")
            show_obj_data(self)

# 5m or 1h average data
class AvgData():
    def __init__(self):
        self.used = False
        self.type = ""

        self.insta_buy_avg = None
        self.insta_buy_vol = None
        self.insta_sell_avg = None
        self.insta_sell_vol = None
        self.avg_vol = None
        self.price_avg = None
        self.margin_taxed = None
        self.profit_per_limit = None  
        self.roi_avg = None

    def show(self):
        if (self.used == True):
            print("%s Average:" % (self.type))
            show_obj_data(self)

# Data for a timeseries
class TimeSeriesData():
    def __init__(self):
        self.used = False
        self.type = ""

        # TODO: Where it total volume
        self.insta_buy_avg = None
        self.insta_buy_vol = None
        self.insta_sell_avg = None
        self.insta_sell_vol = None
        self.total_vol = None
        self.price_avg = None
        self.margin_avg = None
        self.margin_taxed_avg = None
        self.profit_per_limit_avg = None  
        self.roi_avg = None

        self.price_change = None
        self.price_change_percent = None   

        # Plot data
        self.plt = None     

    def show(self):
        if (self.used == True):
            print("Last %s:" % (self.type))
            show_obj_data(self)

# Show data for a time range's Data() objects
def show_obj_data(obj):
    for attr in vars(obj):
        #print(attr)
        data_obj = getattr(obj, attr)
        # Skip non-Data() objects
        if (isinstance(data_obj, Data) != True):
            continue
        data_obj.showi()
  
    print("")

def print_data(item_list):
    for item in item_list:

        # Print basic item data
        item.show()

        # Show latest data
        item.ld.show()

        # Show average last 5 minutes
        item.avg_5m_data.show()

        # Show average last 1 hour
        item.avg_1h_data.show()

        # Show last 6 hours
        item.series_6h_data.show()

        # Show last 12 hours
        item.series_12h_data.show()

        # Show last 24 hours
        item.series_24h_data.show()

        # Show last week
        item.series_1w_data.show()

        # Show last month
        item.series_1m_data.show()

        # Show last year
        item.series_1y_data.show()

"""
filter_items()

Find items based on applied filters
"""
def filter_items():

    item_list = []

    # Represents the data a user wants to show
    ofs = OutputFilters()
    if (ofs.used == False):
        print("User has opted to show no data. Quitting.")
        quit(1)

    # Find /latest items that pass basic filter
    num_items = get_num_filtered_items(ofs)
    if (num_items > 200):
        print("Not exceeding 200 items during testing")
        quit()

    # Return items that pass filter and return their
    # data
    for item_id in latest_all['data']:   
        itd = filter_item(item_id, ofs)
        if (itd.used):
            item_list.append(itd)

    print_data(item_list)

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
    itd.ge_limit = Data(True, limit, "GE Buy Limit: %s")

    # Get latest data. Go to next item if no data
    # We MUST get this for filtering, even if latest data is not shown.
    latest_data = get_latest_data(itd, int(item_id), ofs)
    if itd.used == False:
        return itd

    # Filter by item price
    f = bif.item_price.filter(latest_data.price_avg.value)
    if (f == False):
        itd.used = False
        return itd

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

    # Format our string
    """
    underline = make_name_underline(name)    
    id_str = " (%s)" % (item_id)   
    name_string = name + id_str + '\n' + underline
    
    # Get Item's Trade details
    item_s = "Trade Details:\n"
    avg_daily_vol_s = "  Trade Volume (Avg Daily): %s\n" % (avg_daily_vol_c)
    vol_24h_s = "  Trade Volume (24h): %s\n" % (total_24h_vol_c)
    limit_s = "  Trade Limit: %s\n" % (limit_c)
    """

    # Get 5 minutes average data
    if (ofs.show_a5mf == True):
        itd.avg_5m_data = get_average_data(itd, int(item_id), ofs, "5m")

    # Get 1 hour average data
    if (ofs.show_a1hf == True):
        itd.avg_1h_data = get_average_data(itd, int(item_id), ofs, "1h")

    # TODO: 6, 12, 24h can be consolidated.
    # Get last 6h data
    if (ofs.show_s6hf == True):
        itd.series_6h_data = get_timeseries_data(itd, int(item_id), ofs, "5m", 72)

    # Get last 12h data
    if (ofs.show_s12hf == True):
        itd.series_12h_data = get_timeseries_data(itd, int(item_id), ofs, "5m", 144)

    # Get last 24h data
    if (ofs.show_s24hf == True):
        itd.series_24h_data = get_timeseries_data(itd, int(item_id), ofs, "5m", 288)

    # Get last 1 week data
    if (ofs.show_s1wf == True):
        itd.series_1w_data = get_timeseries_data(itd, int(item_id), ofs, "1h", 168)
    
    # Get last 1 month data
    if (ofs.show_s1mf == True):
        itd.series_1m_data = get_timeseries_data(itd, int(item_id), ofs, "6h", 112)

    # Get last 1 year data
    if (ofs.show_s1yf == True):
        itd.series_1y_data = get_timeseries_data(itd, int(item_id), ofs, "24h", 364)

    return itd

"""
get_num_filtered_items()

Get number of items that pass basic filters
"""
def get_num_filtered_items(ofs):

    # Basic item filter
    bif = ofs.bif

    num_filtered = 0
    for item_id in latest_all['data']:
        # Find item in item_map 
        item_entry = find_item_entry(int(item_id))
        if item_entry == None:
            continue
        name = item_entry['name'] 

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

        # Filter item price
        f = bif.item_price.filter(latest_data.price_avg.value)
        if (f == False):
            continue

        num_filtered = num_filtered + 1

    return num_filtered    

def get_timeseries_data(itd, item_id, ofs, timestep, num_steps):

    if (num_steps < 0 or num_steps > 364):
        print("Timeseries steps must be from 0 to 364")
        quit(1)

    # Ensure timestep is a valid option
    if (timestep != "5m" and timestep != "1h" and timestep != "6h" and timestep != "24h"):
        print("Invalid timestep provided")
        quit(1)

    tsd = TimeSeriesData()  

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
                                                      
    plt = pyplot

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
    first_insta_buy_vol = get_earliest_ts_data(data_ts, "highPriceVolume", num_entries, num_steps)
    first_insta_sell_vol = get_earliest_ts_data(data_ts, "lowPriceVolume", num_entries, num_steps)
    
    # Get most recent data
    curr_insta_buy_time = get_current_ts_data(data_ts, "timestamp", num_entries, num_steps)
    curr_insta_buy_avg = get_current_ts_data(data_ts, "avgHighPrice", num_entries, num_steps)
    curr_insta_sell_avg = get_current_ts_data(data_ts, "avgLowPrice", num_entries, num_steps)
    curr_insta_buy_vol = get_current_ts_data(data_ts, "highPriceVolume", num_entries, num_steps)
    curr_insta_sell_vol = get_current_ts_data(data_ts, "lowPriceVolume", num_entries, num_steps)

    # Get price change over entire time period
    if (curr_insta_buy_avg == None or curr_insta_sell_avg == None or\
        first_insta_buy_avg == None or first_insta_sell_avg == None):
        price_change = None
        price_change_percent = None
    else:
        first_insta_price_avg = (first_insta_sell_avg + first_insta_buy_avg)/2     
        curr_insta_price_avg = (curr_insta_sell_avg + curr_insta_buy_avg)/2
        price_change = curr_insta_price_avg - first_insta_price_avg
        price_change_percent = int((price_change / first_insta_price_avg)*100) 


    count = 0
    buy_count = 0
    sell_count = 0
    insta_sell_vol = 0
    insta_buy_vol = 0
    total_insta_sell_price = 0
    total_insta_buy_price = 0
    min_insta_sell_price = 0xffffffff
    max_insta_buy_price = 0
    min_list = []
    max_list = []
    insta_sell_prices = []
    insta_buy_prices = []
    insta_sell_times = []
    insta_buy_times = []
    for i in range(num_entries, num_entries-num_steps, -1):
        entry = data_ts[i]

        # Track total volumes
        insta_sell_vol = insta_sell_vol + entry['lowPriceVolume']
        insta_buy_vol = insta_buy_vol + entry['highPriceVolume']
        
        # Get insta sell price data
        if (entry['avgLowPrice'] != None):
            insta_sell_price = entry['avgLowPrice']
            insta_sell_prices.append(insta_sell_price)
            insta_sell_times.append(entry['timestamp'])
            total_insta_sell_price = total_insta_sell_price + insta_sell_price
            sell_count = sell_count + 1
            if (min_insta_sell_price > insta_sell_price):
                min_insta_sell_price = insta_sell_price
                min_isp_ts = entry['timestamp']
                min_isp_vol = entry['lowPriceVolume']
            # Get all local minima into a list
            get_minima(min_list, data_ts, num_entries, num_steps, i)

        # Get insta buy price data
        if (entry['avgHighPrice'] != None):
            insta_buy_price = entry['avgHighPrice']
            insta_buy_prices.append(insta_buy_price)
            insta_buy_times.append(entry['timestamp'])
            total_insta_buy_price = total_insta_buy_price + insta_buy_price
            buy_count = buy_count + 1
            if (max_insta_buy_price < insta_buy_price):
                max_insta_buy_price = insta_buy_price
                max_ibp_ts = entry['timestamp']
                max_ibp_vol= entry['highPriceVolume']
            # Get all local maxima into a list
            get_maxima(max_list, data_ts, num_entries, num_steps, i)
 
    # Get total trade volume
    total_vol = insta_sell_vol + insta_buy_vol

    # Get average volume for each timestep
    avg_vol = int(total_vol/num_steps)
    avg_insta_sell_vol = int(insta_sell_vol/num_steps)
    avg_insta_buy_vol = int(insta_buy_vol/num_steps)

    # Get average insta buy/sell prices for each timestep
    insta_sell_avg = int(total_insta_sell_price/sell_count)
    insta_buy_avg = int(total_insta_buy_price/buy_count)
    price_avg = (insta_buy_avg + insta_sell_avg)/2

    # Get average margin and taxed margin
    margin_avg = insta_buy_avg - insta_sell_avg
    margin_taxed_avg = int((insta_buy_avg*.99 - insta_sell_avg))

    # Get average profit per buy limit
    profit_per_limit_avg = margin_taxed_avg * itd.ge_limit.value

    # Get average return on invesment
    roi_avg = int((margin_taxed_avg / insta_sell_avg)*100)

    # Get our buying price based on the sell data
    low_i = get_ideal_low_margin(data_ts, num_entries, num_steps, min_list, .2)

    # Get our selling price based on the buy data
    high_i = get_ideal_high_margin(data_ts, num_entries, num_steps, max_list, .2) 

    item = find_item_entry(item_id)

    # TODO: Make function to returning plot data
    plt.plot(insta_sell_times, insta_sell_prices, color = 'blue', label = 'Instant Sell Price')

    # Plot low margin
    if (low_i != 0):
        plt.axhline(y = data_ts[low_i]['avgLowPrice'], color = 'blue', linestyle = '-')

    plt.plot(insta_buy_times, insta_buy_prices, color='red', label = 'Instant Buy Price')

    # Plot high margin
    if (high_i != 0):
        plt.axhline(y = data_ts[high_i]['avgHighPrice'], color = 'blue', linestyle = '-')

    # naming the x axis
    plt.xlabel('Time (Unix Timestamp)')
    # naming the y axis
    plt.ylabel('Price')

    # giving a title to my graph
    plt.title(item['name'])

    plt.legend()

    tsd.insta_buy_avg = Data(opt.insta_buy_avg.show, insta_buy_avg, "Insta Buy Price (Average): %s")
    tsd.insta_buy_vol = Data(opt.insta_buy_vol.show, insta_buy_vol, "Insta Buy Volume: %s")
    tsd.insta_sell_avg = Data(opt.insta_sell_avg.show, insta_sell_avg, "Insta Sell Price (Average): %s")
    tsd.insta_sell_vol = Data(opt.insta_sell_vol.show, insta_sell_vol, "Insta Sell Volume: %s")
    tsd.total_vol = Data(opt.total_vol.show, total_vol, "Total Volume: %s")
    tsd.price_avg = Data(opt.price_avg.show, price_avg, "Price (Average): %s")
    tsd.margin_taxed_avg = Data(opt.margin_taxed_avg.show, margin_taxed_avg, "Margin (Average Taxed): %s")
    tsd.profit_per_limit_avg = Data(opt.profit_per_limit_avg.show, profit_per_limit_avg, "Profit Per Limit (Average): %s")
    tsd.roi_avg = Data(opt.roi_avg.show, roi_avg, "ROI (Average): %d%")
    tsd.price_change = Data(opt.price_change.show, price_change, "Price Change: %s")
    tsd.price_change_percent = Data(opt.price_change_percent.show, price_change_percent, "Price Change %: %s%")
    tsd.plt = plt
    
    return tsd

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
get_all_item_data()

Returns flipping data for all items in item list

Other Ideas:
- Return highest and lowest trade over last hour
- Return last 24hr, week, and month averages

"""
def get_all_item_data(item_list):
    main_string = ""
    for item_id in item_list:
        data = get_item_data(item_id, latest = True, avg_5m = True, \
                             avg_1h = True)
        main_string = main_string + data
        
    return main_string

"""
get_item_data()

Return all flipping data for an item

# TODO: This really needs updated
"""
def get_item_data(item_id, *args, **kwargs):

    # TODO: Get rid of this when get_time_series_data is adapted
    ofs = OutputFilters(True, True, True, True, None)

    if (item_id < 0):
        print("item_id must be 0 or greater")
        quit(1)
    
    get_latest = kwargs.get('latest', None)
    get_avg5m = kwargs.get('avg_5m', None)
    get_avg1h = kwargs.get('avg_1h', None)
    
    item_entry = find_item_entry(item_id)
    name = item_entry['name']
    underline = make_name_underline(name)
    
    id_str = " (%s)" % (item_id)
    name_string = name + id_str + '\n' + underline
    item_string = ""
    
    if (get_latest == False and get_avg5m == False and get_avg1h == False):
        main_string = name_string
        main_string = main_string + "  Not retrieving data\n"
        return main_string

    # Get Item data
    item_entry = find_item_entry(item_id)     
    if 'limit' in item_entry:
        limit = item_entry['limit']
    else:
        limit = 0 
        
    # Get daily trade volume
    item_24h = get_json(ts_url, item_id=int(item_id), timestep="24h")
    high_vol = item_24h['data'][0]['highPriceVolume']
    low_vol = item_24h['data'][0]['lowPriceVolume']
    total_vol = high_vol + low_vol      
    total_vol_c = format(total_vol, ',d')

    # Get trade limit
    item_entry = find_item_entry(int(item_id))   
    
    if 'limit' in item_entry:
        limit = item_entry['limit']
        limit_c = format(limit, ',d')
    else:
        limit_c = "Not Listed"      
    
    itd = ItemData()
    itd.id = item_id
    itd.name = name
    itd.ge_limit = limit

    trade_s = "Trade Details:\n"
    vol_s = "  Trade Volume (24h): %s\n" % (total_vol_c)
    limit_s = "  Trade Limit: %s\n" % (limit_c)
    
    # Get latest data
    if get_latest == True:
        latest_data = get_latest_data(itd, item_id, ofs)
        item_string = item_string + latest_data.main_string
    
    # Get last 5m average data
    if get_avg5m == True:
        avg_data_5m = get_average_data(itd, item_id, "5m", ofs)
        item_string = item_string + avg_data_5m.main_string
    
    # Get last 1h average data
    if get_avg1h == True:
        avg_data_1h = get_average_data(itd, item_id, "1h", ofs)
        item_string = item_string + avg_data_1h.main_string

    main_string = name_string + trade_s + vol_s + limit_s + item_string
    
    # Get data for a full day for this item
    data_24h = get_timeseries_data(item_id, ofs, "5m", 288)

    return main_string + '\n'
    
  
"""
get_latest_data()

Format a string for the /latest data
"""
def get_latest_data(itd, item_id, ofs):

    ld = LatestData()

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
    
    # Check if there is insta buy data
    if (insta_buy_price == None):
        ld.used = False       
        return ld
        
    # Check if there is insta sell data
    if (insta_sell_price == None):
        ld.used = False           
        return ld  

    price_avg = (insta_sell_price + insta_buy_price) / 2

    # Get last buy/sell time in minutes
    now = time.time()
    insta_buy_time_min = int((now - insta_buy_time)/60)
    insta_sell_time_min = int((now - insta_sell_time)/60)
    
    # Get margins and profit and roi
    margin = insta_buy_price - insta_sell_price
    margin_taxed = int((insta_buy_price*.99) - insta_sell_price)

    profit_per_limit = margin_taxed * itd.ge_limit.value
    roi = int((margin_taxed / insta_sell_price)*100)


    # Store latest data
    ld.insta_sell_price = Data(lf.insta_sell_price.show, insta_sell_price, "Insta Sell Price: %s")
    ld.insta_sell_time_min = Data(lf.insta_sell_time_min.show, insta_sell_time_min, "Insta Sell Time: %s Min Ago")    
    ld.insta_buy_price = Data(lf.insta_buy_price.show, insta_buy_price, "Insta Buy Price: %s")
    ld.insta_buy_time_min = Data(lf.insta_buy_time_min.show, insta_buy_time_min, "Insta Buy Time: %s Min Ago")
    ld.price_avg = Data(lf.price_avg.show, price_avg, "Average Price: %s") 
    ld.margin_taxed = Data(lf.margin_taxed.show, margin_taxed, "Margin (Taxed): %s")
    ld.profit_per_limit = Data(lf.profit_per_limit.show, profit_per_limit, "Profit Per Limit: %s")
    ld.roi = Data(lf.roi.show, roi, "ROI: %s%%")

    return ld

"""
get_average_data()

Get data for 5m or 1h average
"""
def get_average_data(itd, item_id, ofs, avg_type):
    
    ad = AvgData()
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
    
    avg_vol = insta_sell_vol + insta_buy_vol
    price_avg = (insta_buy_avg + insta_sell_avg)/2

    # Get margin, profit, roi
    margin_taxed = int((insta_buy_avg*.99) - insta_sell_avg)
    profit_per_limit = margin_taxed * itd.ge_limit.value
    roi_avg = int((margin_taxed / insta_sell_avg)*100)

    ad.insta_buy_avg = Data(opt.insta_buy_avg.show, insta_buy_avg, "Average Insta Buy Price: %s")
    ad.insta_buy_vol = Data(opt.insta_buy_vol.show, insta_buy_vol, "Average Insta Buy Vol: %s")
    ad.insta_sell_avg = Data(opt.insta_sell_avg.show, insta_sell_avg, "Average Insta Sell Price: %s")
    ad.insta_sell_vol = Data(opt.insta_sell_vol.show, insta_sell_vol, "Average Insta Sell Vol: %s")
    ad.avg_vol = Data(opt.avg_vol.show, avg_vol, "Average Volume: %s")
    ad.price_avg = Data(opt.price_avg.show, price_avg, "Average Price: %s")
    ad.margin_taxed = Data(opt.margin_taxed.show, margin_taxed, "Average Margin (Taxed): %s")
    ad.profit_per_limit = Data(opt.profit_per_limit.show, profit_per_limit, "Average Profit Per Limit: %s")
    ad.roi_avg = Data(opt.roi_avg.show, roi_avg, "Average ROI: %s%")

    return ad
    
"""
com()

Return comma separated string given an integer
"""
def com(integer):
    return format(integer, ',d')

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

    #item_id = find_item_id("bandos chaps")
    #print(item_id)
    
    #item_list = [item_id]
    #item_data = get_all_item_data(item_list)
    #print(item_data)
    
    filter_items()
    
    

if __name__ == "__main__":
    main()
    
    
    
    
