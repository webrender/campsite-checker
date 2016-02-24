## campsite-checker

This is a python script which attempts to automate the process of reserving sites on recreation.gov.  It is especially made for sought-after campsites which have limited booking windows.

### Dependencies
  * OS X or *nix variant
  * Python
  * Selenium
  * Firefox

If you're unfamiliar with the above tools and using OS X: You already have a version of Python preinstalled. You can install Selenium by opening a Terminal window and entering the following command: `sudo easy_install selenium`

### Running the script

Open up checker.py and fill in the fields on lines 12-19. See below for how to find site\_id and park\_id values from the recreation.gov website.

Once you've configured the script, open up a Terminal window and enter the command `python checker.py` to run the script.

Reccomended use pattern is to begin the script shortly before reservations are due to open, with a low number of retries. Recreation.gov network usage is monitored and you risk account termination if you just leave this running all day.

### Finding park\_id and site\_id

Find the campsite you wish to book on recreation.gov - do not enter selected dates. Go to the 'Site List' page, and hover over the 'Enter Date' button by the site you are interested in.  In the lower left of your browser, you will see a URL like the following:

`http://www.recreation.gov/camping/Wawona/r/campsiteDetails.do?contractCode=NRSO&siteId=204305&parkId=70924`

The site ID and park ID are the numbers specified at the end of the URL.
