#!/usr/bin/env python3
"""  
Script for obtaining pricing data from osrs real time prices:
    https://oldschool.runescape.wiki/w/RuneScape:Real-time_Prices 
"""

import urllib.request
import json
import time
import matplotlib.pyplot as plt

# Keep urls global to access with any function
api_url = 'https://prices.runescape.wiki/api/v1/osrs'
latest_url = api_url + '/latest'
map_url = api_url + '/mapping'
five_url = api_url + '/5m'
hour_url = api_url + '/1h'
ts_url = api_url + '/timeseries'

# Determines what items get shown (First Filter)
class InputFilters():
    def __init__(self):
        # Filters applied to 5m average
        self.min_price = None
        self.max_price = None

        # Filter applied to item itself
        self.ge_limit = None

        # Specific Filters
        self.daily_avg_vol = None

        # Time range to apply filters below to
        self.focus = None

        # Filters applied to the focused time range
        self.profit = None          # Currently applied to "profit per trade limit"


  
# Determines what data gets shown for a selected item (Second Filter)
class OutputFilters():
    def __init__(self):
        # Time ranges to show data for
        self.show_latest = None
        self.show_5m_avg = None
        self.show_1h_avg = None
        self.show_6h = None
        self.show_24h = None
        self.show_1w = None
        self.show_1m = None
        self.show_1y = None

        # Data to show
        # TODO: Add this in when we've figured out our data first ..

# Basic Item Data
class ItemData():
    def __init__(self):
        self.id = None
        self.name = None
        self.ge_limit = None

# 5m or 1h average data
class AvgData():
    def __init__(self):
        self.insta_buy_avg = None
        self.insta_buy_vol = None
        self.insta_sell_avg = None
        self.insta_sell_vol = None

        self.margin = None
        self.margin_taxed = None
        self.profit_per_item = None
        self.profit_per_limit = None

        # String Data
        self.header_s = ""
        self.insta_buy_avg_s = ""
        self.insta_buy_vol_s = ""
        self.insta_sell_avg_s = ""
        self.insta_sell_vol_s = ""
        self.margin_taxed_s = ""
        self.profit_per_item_s = ""
        self.profit_per_limit_s = ""
        self.main_string = ""    

# Latest Data
class LatestData():
    def __init__(self):
        self.blah = None



# Data for a timeseries
class TimeSeriesData():
    def __init__(self):
        self.price_change = None
        self.price_change_percent = None        
        
"""
filter_items()

Find items based on applied input filter 


 

"""
def filter_items():

    # Pass parameters to filters
    ifs = InputFilters()
    ifs.min_price = 190
    ifs.max_price = 205
    ifs.profit = 0
    ifs.ge_limit = 5000

    ofs = OutputFilters()
    ofs.show_latest = True
    ofs.show_5m_avg = True
    ofs.show_1h_avg = True
    ofs.show_6h = False
    ofs.show_24h = True
    ofs.show_1m = False
    ofs.show_1y = False

    # Get filter string
    # TODO: Turn into function
    min_price_c = format(ifs.min_price, ',d')
    max_price_c = format(ifs.max_price, ',d')
    profit_c = format(ifs.profit, ',d')
    ge_limit_c = format(ifs.ge_limit, ',d')    
    filterh_s =     "Filters:\n"
    ifs_s = "  Price Range (%s, %s) | Profit (%s) | GE Limit (%s)\n\n" % (min_price_c, max_price_c, profit_c, ge_limit_c)
    
    main_string = ""
    
    # Loop all items, apply filters, and print data if item passes through filters
    # - Loop 5 minute average data to apply initial filters
    for item_id in avg_5m_all['data']:   
        data = filter_item(item_id, ifs, ofs)
        main_string = data + main_string
    
    # Leave if no data returned from filter
    if (main_string == ""):
        return
        
    print(filterh_s + ifs_s + main_string)    
        
        
"""
filter_item():

Apply filters to an item and return item data.
   
"""
def filter_item(item_id, ifs, ofs):

    item = avg_5m_all['data'][item_id]

    # TODO:
    # Re-writing get_average_data to return data via its class
    # so its more modular.

    avg_5m_ib = item['avgHighPrice']
    avg_5m_is = item['avgLowPrice']

    #high_5m_vol = item['highPriceVolume']
    #low_5m_vol = item['lowPriceVolume']
    
    if (avg_5m_is == None):
        return ""
    
    if (avg_5m_ib == None):
        return ""    
    
    margin = avg_5m_ib - avg_5m_is
    tax_margin = int((avg_5m_ib*.99) - avg_5m_is)
    
    # Ensure item is in desired price range
    if (avg_5m_is < ifs.min_price or avg_5m_is > ifs.max_price):
        return ""
      
    # Ensure item fits desired profit
    if (tax_margin < ifs.profit):
        return ""

    # Find item in item_map 
    item_entry = find_item_entry(int(item_id))
    name = item_entry['name'] 
       
    if 'limit' in item_entry:
        limit = item_entry['limit']
    else:
        limit = 9999999       
          
    # Ensure item has atleast the desired buy limit
    if (limit < ifs.ge_limit):
        return ""
    
    # Passed initial filters, get basic item data
    itd = ItemData()
    itd.id = int(item_id)
    itd.name = name
    itd.ge_limit = limit    

    # Get 24h data for last year
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
        

    # Get trade limit
    item_entry = find_item_entry(int(item_id))   
    
    if 'limit' in item_entry:
        limit = item_entry['limit']
        limit_c = format(limit, ',d')
    else:
        limit_c = "Not Listed"  
        limit = 0

    # Format our string
    underline = make_name_underline(name)    
    id_str = " (%s)" % (item_id)   
    name_string = name + id_str + '\n' + underline
    
    # Get Item's Trade details
    item_s = "Trade Details:\n"
    avg_daily_vol_s = "  Trade Volume (Avg Daily): %s\n" % (avg_daily_vol_c)
    vol_24h_s = "  Trade Volume (24h): %s\n" % (total_24h_vol_c)
    limit_s = "  Trade Limit: %s\n" % (limit_c)
    
    # Get latest data
    if (ofs.show_latest == True):
        data_latest = get_latest_string(latest_all, int(item_id), ofs) 
    else:
        data_latest = ""

    # Get 5 minute average data
    if (ofs.show_5m_avg == True):
        data_5m_avg = get_average_data(itd, avg_5m_all, int(item_id), ofs, "5m") 
    else:
        data_5m_avg = ""
  
    # Get 1 hour average data
    if (ofs.show_1h_avg == True):
        data_1h_avg = get_average_data(itd, avg_1h_all, int(item_id), ofs, "1h")
    else:
        data_1h_avg = ""    

    # Get data for a full day for this item
    # TODO: class returned will include our strings :)
    if (ofs.show_24h == True):
        data_24h = get_timeseries_data(int(item_id), ifs, ofs, "5m", 288)
    else:
        data_24h = None
    
    fmt_string = name_string + item_s + vol_24h_s + avg_daily_vol_s + limit_s + data_5m_avg + data_latest + data_1h_avg
    
    return fmt_string + '\n'

def get_timeseries_data(item_id, ifs, ofs, timestep, num_steps):

    if (num_steps < 0 or num_steps > 364):
        print("Timeseries steps must be from 0 to 364")
        quit(1)

    # Ensure timestep is a valid option
    if (timestep != "5m" and timestep != "1h" and timestep != "6h" and timestep != "24h"):
        print("Invalid timestep provided")
        quit(1)

    print(item_id)

    tsd = TimeSeriesData()        
            
    # Get timestep data (365 datapoints, higher numbers are more recent)    
    data_ts = get_json(ts_url, item_id=item_id, timestep=timestep)
    data_ts = data_ts['data']
    
    # Get earliest and most recent data
    first_insta_buy_time = get_earliest_ts_data(data_ts, "timestamp", num_steps)
    first_insta_buy_avg = get_earliest_ts_data(data_ts, "avgHighPrice", num_steps)
    first_insta_sell_avg = get_earliest_ts_data(data_ts, "avgLowPrice", num_steps)
    first_insta_buy_vol = get_earliest_ts_data(data_ts, "highPriceVolume", num_steps)
    first_insta_sell_vol = get_earliest_ts_data(data_ts, "lowPriceVolume", num_steps)
    
    curr_insta_buy_time = get_current_ts_data(data_ts, "timestamp")
    curr_insta_buy_avg = get_current_ts_data(data_ts, "avgHighPrice")
    curr_insta_sell_avg = get_current_ts_data(data_ts, "avgLowPrice")
    curr_insta_buy_vol = get_current_ts_data(data_ts, "highPriceVolume")
    curr_insta_sell_vol = get_current_ts_data(data_ts, "lowPriceVolume")

    if (first_insta_sell_avg == None or curr_insta_sell_avg == None or\
        first_insta_buy_avg == None or first_insta_sell_avg == None):
        ts_price_change = None
        ts_price_change_percent = None
    else:
        first_insta_price_avg = (first_insta_sell_avg + first_insta_buy_avg)/2     
        curr_insta_price_avg = (curr_insta_sell_avg + curr_insta_buy_avg)/2
        ts_price_change = curr_insta_price_avg - first_insta_price_avg
        ts_price_change_percent = (ts_price_change / first_insta_price_avg)*100 
    
    count = 0
    buy_count = 0
    sell_count = 0
    total_insta_sell_vol = 0
    total_insta_buy_vol = 0
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
    for i in range(364, 364-num_steps, -1):
        entry = data_ts[i]

        # Track total volumes
        total_insta_sell_vol = total_insta_sell_vol + entry['lowPriceVolume']
        total_insta_buy_vol = total_insta_buy_vol + entry['highPriceVolume']
        
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
            get_minima(min_list, data_ts, num_steps, i)

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
            get_maxima(max_list, data_ts, num_steps, i)
 
    # Get total trade volume
    total_vol = total_insta_sell_vol + total_insta_buy_vol

    # Get average volume for each timestep
    avg_vol = int(total_vol/num_steps)
    avg_insta_sell_vol = int(total_insta_sell_vol/num_steps)
    avg_insta_buy_vol = int(total_insta_buy_vol/num_steps)

    # Get average insta buy/sell prices for each timestep
    avg_insta_sell_price = int(total_insta_sell_price/sell_count)
    avg_insta_buy_price = int(total_insta_buy_price/buy_count)

    # Get our buying price based on the sell data
    low_i = get_ideal_low_margin(data_ts, num_steps, min_list, .2)

    # Get our selling price based on the buy data
    high_i = get_ideal_high_margin(data_ts, num_steps, max_list, .2) 

    # Display graph of insta-buy/sell data with line across the
    # most common high/low insta buy/sell prices to verify/visualize findings 

    item = find_item_entry(item_id)
    plt.plot(insta_sell_times, insta_sell_prices, color = 'blue', label = 'Instant Sell Price')
    plt.axhline(y = data_ts[low_i]['avgLowPrice'], color = 'blue', linestyle = '-')

    plt.plot(insta_buy_times, insta_buy_prices, color='red', label = 'Instant Buy Price')
    plt.axhline(y = data_ts[high_i]['avgHighPrice'], color = 'blue', linestyle = '-')

    # naming the x axis
    plt.xlabel('Time (Unix Timestamp)')
    # naming the y axis
    plt.ylabel('Price')

    # giving a title to my graph
    plt.title(item['name'])

    plt.legend()

    # function to show the plot
    plt.show()    

    tsd.price_change = ts_price_change
    tsd.price_change_percent = ts_price_change_percent      
    quit(1)
    
    return tsd

def get_ideal_low_margin(data_ts, num_steps, min_list, percentile):

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
        for x in range(364, 364-num_steps, -1):
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
    

def get_ideal_high_margin(data_ts, num_steps, max_list, percentile):
    
    if (len(max_list) ==0):
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
        for x in range(364, 364-num_steps, -1):
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

def get_minima(min_list, data_ts, num_steps, i):

    closest_left = 0
    closest_right = 0    

    # Find next non-null recent (left) insta sell indice
    j = i+1
    while (j <= 364): 
        if (data_ts[j]['avgLowPrice'] != None):
            closest_left = data_ts[j]['avgLowPrice']
            break
        if (j == 364):
            closest_left = None
        j = j+1
            
    # Find next non-null early (right) insta sell indice
    j = i-1
    while (j >= (364-num_steps)):
        if (data_ts[j]['avgLowPrice'] != None):
            closest_right = data_ts[j]['avgLowPrice']
            break
        if (j == (364-num_steps)):
            closest_right = None
        j = j-1

    # Edge case where there is no adjacent data
    if (closest_left == None and closest_right == None):
        min_list.append(i)
        return

    # Case where we are on the first index
    if (i == 364):
        if (data_ts[364]['avgLowPrice'] < closest_right):
            min_list.append(364)
        return

    # Case where we are on the last index
    if (i == (364-num_steps)):
        if (data[364-num_steps]['avgLowPrice'] < closest_left):
            min_list.append(364-num_steps)
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

def get_maxima(max_list, data_ts, num_steps, i):

    closest_left = 0
    closest_right = 0    

    # Find next non-null recent (left) insta buy indice
    j = i+1
    while (j <= 364): 
        if (data_ts[j]['avgHighPrice'] != None):
            closest_left = data_ts[j]['avgHighPrice']
            break
        if (j == 364):
            closest_left = None
        j = j+1
            
    # Find next non-null early (right) insta buy indice
    j = i-1
    while (j >= (364-num_steps)):
        if (data_ts[j]['avgHighPrice'] != None):
            closest_right = data_ts[j]['avgHighPrice']
            break
        if (j == (364-num_steps)):
            closest_right = None
        j = j-1

    # Edge case where there is no adjacent data
    if (closest_left == None and closest_right == None):
        max_list.append(i)
        return

    # Case where we are on first index 
    if (i == 364 and data_ts[364]['avgHighPrice'] != None):
        if (data_ts[364]['avgHighPrice'] > closest_right):
            max_list.append(364)
        return

    # Case where we are on last index
    if (i == (364-num_steps) and data[364-num_steps]['avgHighPrice'] != None):
        if (data[364-num_steps]['avgHighPrice'] > closest_left):
            max_list.append(364-num_steps)
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


def get_earliest_ts_data(data_ts, key, num_steps):
  
    data = None
    for i in range(0, 5):
        if (data_ts[364-num_steps+i][key] != None):
            data = data_ts[364-num_steps+i][key]
            break
  
    return data    
    
def get_current_ts_data(data_ts, key):
  
    data = None
    for i in range(0, 5):
        if (data_ts[364-i][key] != None):
            data = data_ts[364-i][key]
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

Return all flipping data for an item as a string.
"""
def get_item_data(item_id, *args, **kwargs):

    # TODO: Get rid of this when get_time_series_data is adapted
    ifs = InputFilters(200000, 2000000, 10000, 1)
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
        limit = 9999999    
        
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
        latest_string = get_latest_string(latest_all, item_id, ofs)
        item_string = item_string + latest_string
    
    # Get last 5m average data
    if get_avg5m == True:
        avg_5m_string = get_average_data(itd, avg_5m_all, item_id, "5m", ofs)
        item_string = item_string + avg_5m_string
    
    # Get last 1h average data
    if get_avg1h == True:
        avg_1h_string = get_average_data(itd, avg_1h_all, item_id, "1h", ofs)
        item_string = item_string + avg_1h_string

    main_string = name_string + trade_s + vol_s + limit_s + item_string
    
    # Get data for a full day for this item
    data_24h = get_timeseries_data(item_id, ifs, ofs, "5m", 288)

    return main_string + '\n'
    
  
"""
get_latest_string()

Format a string for the /latest data
"""
def get_latest_string(latest_all, item_id, ofs):

    if (str(item_id)) not in latest_all['data']:
        fmt_string = "latest:\n"
        fmt_string = fmt_string + "  No data\n"
        return fmt_string

    latest = latest_all['data'][str(item_id)]
    
    high = latest['high']
    high_time = latest['highTime']
    low = latest['low']
    low_time = latest['lowTime']
    
    now = time.time()
    high_diff_min = int((now - high_time)/60)
    low_diff_min = int((now - low_time)/60)
    
    margin = high - low
    tax_margin = int((high*.99) - low)
    
    low_c = format(low, ',d')
    high_c = format(high, ',d')
    tax_margin_c = format(tax_margin, ',d')
    margin_c = format(margin, ',d')
    profit_10_s_c = format(tax_margin*10, ',d')
    
    latest_s =      "latest:\n"
    low_s =         "  Low: %s | Time: %d min ago\n" % (low_c, low_diff_min)
    high_s =        "  High: %s | Time: %d min ago\n" % (high_c, high_diff_min)
    margin_s =      "  Taxed Margin: %s | Margin: %s\n" % (tax_margin_c, margin_c)
    profit_10_s =   "  Profit from 10: %s\n" % (profit_10_s_c)
    
    fmt_string = latest_s + low_s + high_s + margin_s + profit_10_s
    
    return fmt_string

"""
get_average_data()

Get data for 5m or 1h average
"""
def get_average_data(itd, avg_all, item_id, ofs, avg_type):
    
    ad = AvgData()

    if (str(item_id)) not in avg_all['data']:
        fmt_string = "Last %s:\n" % (avg_type)
        fmt_string = fmt_string + "  No data\n"
        return fmt_string
        
    avg = avg_all['data'][str(item_id)] 
      
    ad.insta_buy_avg = avg['avgHighPrice']
    ad.insta_buy_vol = avg['highPriceVolume']
    ad.insta_sell_avg = avg['avgLowPrice']
    ad.insta_sell_vol = avg['lowPriceVolume']  

    # Check if there is insta buy data
    if (ad.insta_buy_vol == 0 or ad.insta_buy_avg == None):
        fmt_string = "Last %s:\n" % (avg_type)
        fmt_string = fmt_string + "  No insta buy data\n"
        return fmt_string
        
    # Check if there is insta sell data
    if (ad.insta_sell_vol == 0 or ad.insta_sell_avg == None):
        fmt_string = "Last %s:\n" % (avg_type)
        fmt_string = fmt_string + "  No insta sell data\n"        
        return fmt_string   
    
    ad.margin = ad.insta_buy_avg - ad.insta_sell_avg
    ad.margin_taxed = int((ad.insta_buy_avg*.99) - ad.insta_sell_avg)
    ad.profit_per_limit = ad.margin_taxed * itd.ge_limit

    # Get string data    
    ad.header_s = "Last %s\n" % (avg_type)
    ad.insta_sell_avg_s = "  Avg Insta Sell Price: %s" % (com(ad.insta_sell_avg))
    ad.insta_sell_vol_s = " | Insta Sell Volume: %s\n" % (com(ad.insta_sell_vol))
    ad.insta_buy_avg_s = "  Avg Insta Buy Price: %s" % (com(ad.insta_buy_avg))
    ad.insta_buy_vol_s = " | Insta Buy Volume: %s\n" % (com(ad.insta_buy_vol))
    ad.margin_taxed_s = "  Taxed Margin: %s\n" % (com(ad.margin_taxed))
    ad.profit_per_limit_s = "  Profit Per Limit: %s\n" % (com(ad.profit_per_limit))
    
    ad.main_string = ad.header_s + ad.insta_sell_avg_s + ad.insta_sell_vol_s + \
ad.insta_buy_avg_s + ad.insta_buy_vol_s + ad.margin_taxed_s + ad.profit_per_limit_s

    # TODO: Now we return "ad" and make it work
    print(ad.main_string)

    insta_buy_avg_c = format(ad.insta_buy_avg, ',d')
    insta_buy_vol_c = format(ad.insta_buy_vol, ',d')
    insta_sell_avg_c = format(ad.insta_sell_avg, ',d')
    insta_sell_vol_c = format(ad.insta_sell_vol, ',d')
    tax_margin_c = format(ad.margin_taxed, ',d')
    margin_c = format(ad.margin, ',d')
    profit_10_c = format(ad.margin_taxed*10, ',d')   
    avg_s =         "Last %s:\n" % (avg_type)
    insta_sell_avg_s =     "  Avg Low: %s | Low Volume: %s\n" % (insta_sell_avg_c, insta_sell_vol_c)
    insta_buy_avg_s =    "  Avg High: %s | High Volume: %s\n" % (insta_buy_avg_c, insta_buy_vol_c)
    margin_s =      "  Taxed Margin: %s | Margin: %s\n" % (tax_margin_c, margin_c)
    profit_10_s =   "  Profit from 10: %s\n" % (profit_10_c)  

    fmt_string = avg_s + insta_sell_avg_s + insta_buy_avg_s + margin_s + profit_10_s
    
    return fmt_string
    
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
    
    print("Could not find item for item id: %d" % (item_id))
    quit(1) 

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
make_name_underline

Returns a line for every character in item name
"""    
def make_name_underline(name):
    line = ""
    for c in name: 
        line = line + '-'
    
    return line + '\n'    
    

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
    
    
    
    
