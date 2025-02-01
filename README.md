# OSRS Flipping Tool
Allows users to find items based on an item filter.

## Mac-OS Installation
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

#### Get the Tool
`git clone https://github.com/AustinParkes/osrs_flipping_tool`

#### Install/upgrade python3???

#### Install pip
ref: https://stackoverflow.com/questions/17271319/how-do-i-install-pip-on-macos-or-os-x
Install pip for Python3:
`python3 -m ensurepip --upgrade`

#### Install Python3 Packages
`pip install jsonpickle`

## Using Tool
#### Create and using filters
1) Copy `blank_filter.pkl` to a new file name. Preferably choose a name that
   helps you remember how it is filtering and add `.pkl` suffix so others
   know it is a filter file.

2) In this file exists **Time Range Headers** or **headers** for short.
   For example, a few headers:
`bif`: Basic Item Filter (Not a time range, but still used for filtering items)
`lf`: Latest Filter
`a5mf`: Average 5 Minute Filter
`s12hf`: Series 12 Hour Filter

 - All headers have a `py/object` header beneath them displaying the full acronym so
   you can remember what time range they represent.
   Example -> lf: `"py/object": "__main__.OutputFilters.LatestFilters",`

3) Using Filters:
  - Each header has filter options to determine what items get shown.
 For example, an item's price, `item_price` under `bif`, has 3 filter options:
    `show`: Set to `True` to show data and apply filters. Set to `False` to **NOT** 
            show data and **NOT** apply filters.
    `min`: Minimum value required, in this case for `item_price`.
           Default is lowest possible OSRS value.
    `max`: Maximum value allowed, in this case for `item_price`
           Default is highest possible OSRS value.

  - Only items' whose `item_price` value falls between `min` and `max` will be shown,
    discarding all others.

4) Loading filters into tool with the `-F/--load-filter` command:
`-F filter.pkl`
or
`--load-filter filter.pkl`


#### Sending Emails (gmail)
You must create an app password to send gmails to yourself.

1) Create app password: [App Password](https://support.google.com/accounts/answer/185833?visit_id=638729061199434738-4233195689&p=InvalidSecondFactor&rd=1)

2) Place app password in a file on the second line after your gmail name.
`   user@gmail.com
    app_password`

3) Pass this file to the -e/--send-email command:
`-e file_name.txt`
or
`--send-email file_name.txt`
