#####################################################################################
#
#
#
#
#####################################################################################

### Function Imports
from functions import scrape_data
from functions import clean_data
from functions import get_auction_data
from functions import get_BIN_data
from functions import get_avg_price
from functions import avg_price_cond
from functions import avg_price_month

### Gather User Input for Search Parameters
keyword = input("What frame would you like to search for: ")

if keyword == 'vintage':
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=oakley+" + keyword + "&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"
        print(url)
else:
        formatted_keyword = keyword.replace(" ", "+")
        url = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=oakley+" + formatted_keyword + "&_sacat=0&rt=nc&LH_Sold=1&LH_Complete=1"
        print(url)

### Run Scraper
scraped_data = scrape_data(url)
#print(scraped_data)

### Clean Data
cleaned_data = clean_data(scraped_data)

### Determine which data to extract
sale_option = input("Would you like to use (1) auction data or (2) buy it now data: ")

if sale_option == "1":
        auction_data = get_auction_data(cleaned_data)
        print("Avg Sold Price for all pairs is: $" + str(get_avg_price(auction_data))) 
        print(avg_price_cond(auction_data))
        print(avg_price_month(auction_data))
        
if sale_option == "2":
        BIN_data = get_BIN_data(cleaned_data)
        print("Avg Sold Price for all pairs is: $" + str(get_avg_price(BIN_data))) 
        print(avg_price_cond(BIN_data))
        print(avg_price_month(BIN_data))