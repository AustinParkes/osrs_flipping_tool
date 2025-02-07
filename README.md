# OSRS Flipping Tool
Allows users to find items based on an item filter.

## Mac-OS Installation (UNTESTED)
#### Update Homebrew and Upgrade Packages or Install Homebrew
Check if you have Homebrew:
`brew --version`
If you do, update and upgrade:
`brew update && brew upgrade`
If you don't then install it:
`/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`

#### Install git
ref: https://stackoverflow.com/questions/8957862/how-to-upgrade-git-to-latest-version-on-macos
Install:
`brew install git`
Create link to call from terminal:
`brew link --force git`

#### Get the Flipping Tool
Get with git:  
`git clone https://github.com/AustinParkes/osrs_flipping_tool`  
Go into directory:  
`cd osrs_flipping_tool`  
Make script executable:  
`chmod +x flipping.py`

#### Install python3 and pip
`brew install python`  

#### Install Python3 Packages
JSON Pickle (Filtering):  
`pip install jsonpickle`  
Matplotlib (Plotting):  
`pip install matplotlib`  

## Using Tool
#### Running Tool
Print Help Menu:  
`./flipping.py --help`  

To execute:  
`./flipping.py <arguments>`  
Executing without any arguments will likely result in exceeding the 500 item  
limit, so it is important you create and pass an item filter. 

Help Index:  
[Create and Use Filters](#### Create and Use Filters)  
[Sending Emails (gmail)](#### Sending Emails (gmail))  
[Plotting Data](#### Plotting Data)  
[Using Item Lists](#### Using Item Lists)  
[Using Single Item](#### Using Single Item)  
[Sorting Items](#### Sorting Items)  
[Saving Data to File](#### Saving Data to File)  

#### Create and Use Filters
You can apply filters so the tool will only return items matching that filter.  
Use existing filter file:  
`./flipping.py -F filter.pkl`  
or  
`./flipping.py --load-filter filter.pkl` 

Making a new filter:  
  Copy `blank_filter.pkl` to a new file name. Preferably choose a name that  
  helps you remember how it is filtering and add `.pkl` suffix so others  
  know it is a filter file.

  You can accomplish the same thing with:
`./flipping.py -f filter.pkl`  
or
`./flipping.py --save-filter filter.pkl`  

Time Range Headers:  
  Filter files contain **Time Range Headers**, or **headers** for short, which allow  
  you to apply filters for particular time ranges.  
  For example, a few headers:  
`bif`: Basic Item Filter (Not a time range, but still used for filtering items)  
`lf`: Latest Filter  
`a5mf`: Average 5 Minute Filter  
`s12hf`: Series 12 Hour Filter  

  Each header's full acronym name is shown below it so you can remember it better.   
  Example:  
    lf: `"py/object": "__main__.OutputFilters.LatestFilters",`  

Applying Filters:  
  Each header has filter options for you to edit. 
  For example, an item's price, `item_price` under `bif`, has 3 filter options:  
    `show`: Set to `True` to show data and apply filters. Set to `False` to **NOT**   
            show data and **NOT** apply filters.
    `min`: Minimum value required, in this case for `item_price`.  
           Default is lowest possible OSRS value.  
    `max`: Maximum value allowed, in this case for `item_price`  
           Default is highest possible OSRS value.  

    Only items whose `item_price` value falls between `min` and `max` will be shown,  
    discarding all others.  

Filtering by item name:
  To show items whose name contains a string, set `bif`'s `string` to the string you  
  want included in the name.  
 
  Example:   
  Setting `"string": "chaps"` will show all items with "chaps" in the name.  
  However, if other filters are set, this list may be smaller or non-existent  
  if the items do not pass the other filters.  

#### Sending Emails (gmail)
You can send all your outputted item data as an email including plots!

You must have a gmail account and create an app password to permit the tool
to access your gmail. This tool only uses it for authentication. 
If you don't trust this tool, read the code, or do not use this option.

1) Create app password: [App Password](https://support.google.com/accounts/answer/185833?   visit_id=638729061199434738-4233195689&p=InvalidSecondFactor&rd=1)  

2) Place app password in a file on the second line after your gmail name.  
    `user@gmail.com`
    `app_password`

3) Pass this file to the -e/--send-email command:  
`./flipping.py -e file_name.txt`  
or  
`./flipping.py --send-email file_name.txt`  

#### Plotting Data
You can plot your item data in two ways:  
1) Via PDF  
`./flipping.py -p plots.pdf`  
or  
`./flipping.py --save-plots plots.pdf`

2) Via Email  
(See [Sending Emails](#### Sending Emails (gmail)))  

**NOTE:** Your filter file must show plots for atleast one time range for plots to work.  
In other words, the tool must know which time range(s) to show plots for.    

#### Using Item Lists
You can use your own item list to show data for.

1) Place your items in a textfile, each item on their own line.
Example:
    `saradomin chaps`
    `zamorak chaps`
    `red d'hide chaps (t)`

2) Pass this file to the tool:
`./flipping.py -I items.txt`  
or  
`./flipping.py --load-items items.txt`   

**NOTE:** The item names DO NOT have to be case sensitive. (Capitalization does not matter)
**NOTE:** If you apply filters, they will still apply to those items.

#### Using Single Item
You can also just pass a single item name to the tool.
For example:
`./flipping.py -i "saradomin chaps"`  
or  
`./flipping.py --item "saradomin chaps"`  

**NOTE:** Items with spaces require double quotations.

#### Sorting Items
You can sort items (and their plots) based on any filter option with
a `min`/`max` range.

To view all sort options:
`./flipping.py -x`  
or  
`./flipping.py --sort-options`  

To apply a sort option: (Example)  
`./flipping.py -s ld.profit_per_limit`  
or  
`./flipping.py --sort ld.profit_per_limit`  

This will sort items from high to lowest `profit_per_limit` for `LatestData`

**NOTE:** You can only apply one sort option at a time.

#### Saving Data to File
You can easily save your item data to a file:
`./flipping.py -d item_data.txt`  
or  
`./flipping.py --save-data item_data.txt`  



