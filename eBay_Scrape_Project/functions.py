#####################################################################################
#
#
#
#
#####################################################################################


### Library Imports
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import time


### Complete eBay Scraper -> title, condition, price, sold_date, num_bids, buy_it_now, best_offer
def scrape_data(url):
    # Set up Chrome WebDriver
    driver = webdriver.Chrome(executable_path="/Users/mburley/chromedriver/chromedriver-mac-x64/chromedriver")  # Replace with the path to your chromedriver

    # Open the eBay page
    driver.get(url)

    # Wait for the content to load
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "s-item__info")))

    data = []
    prev_page_number = 0

    while True:
        # Get the page source after waiting for dynamic content
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html5lib')

        print(f"Extracting page: {driver.current_url}")

        for product in soup.select(".s-item"):
            title_element = product.select_one(".s-item__title span")
            title = title_element.text.strip() if title_element else None

            condition_element = product.select_one(".s-item__subtitle")
            condition = condition_element.text.strip() if condition_element else None

            price_element = product.select_one(".s-item__price")
            price = price_element.text.strip() if price_element else None

            sold_date_element = product.select_one(".s-item__title--tag")
            sold_date = sold_date_element.text.strip() if sold_date_element else None

            bids_element = product.select_one(".s-item__bids")
            num_bids = bids_element.text.strip() if bids_element else None

            buy_it_now_element = product.select_one(".s-item__purchase-options")
            buy_it_now_text = buy_it_now_element.text.strip() if buy_it_now_element else None
            buy_it_now_condition = "Buy It Now" in buy_it_now_text or "or Best Offer" in buy_it_now_text if buy_it_now_text else False

            best_offer_element = product.select_one(".s-item__purchase-options")
            best_offer_text = best_offer_element.text.strip() if best_offer_element else None
            best_offer = "Yes" if best_offer_text and "Best offer accepted" in best_offer_text else "No"

            buy_it_now = "Yes" if buy_it_now_condition else "No"

            data.append({
                "title": title,
                "condition": condition,
                "price": price,
                "sold_date": sold_date,
                "num_bids": num_bids,
                "buy_it_now": buy_it_now,
                "best_offer": best_offer
            })

        try:
            # Click the next page button
            driver.find_element(By.CLASS_NAME, 'pagination__next').click()

            # Wait for the new page to load
            time.sleep(3)  # Adjust the sleep duration as needed

            # Extract the current page number
            current_page_number = int(driver.current_url.split("_pgn=")[1].split("&")[0])

            # Break if the page number does not change
            if current_page_number == prev_page_number:
                break

            prev_page_number = current_page_number

        except NoSuchElementException:
            # Break if no next page button is found
            break

    # Save to CSV
    df = pd.DataFrame(data=data)
    df.to_csv("ebay_products_selenium.csv", index=False)

    # Close the WebDriver
    driver.quit()

    return df


### Load in and Clean Scraped Data
def clean_data(df):
    # Convert the 'sold_date' column to string
    df['sold_date'] = df['sold_date'].astype(pd.StringDtype())

    # Covert the sold_date col to the correct format
    df['sold_date'] = df['sold_date'].replace(['Sold', 'Item'], '', regex=True)
    df['sold_date'] = pd.to_datetime(df['sold_date'])

    df = df.dropna(subset=['sold_date'])

    # Remove '$' and remove rows with a price < 25
    df['price'] = df['price'].astype(pd.StringDtype())
    df['price'] = pd.to_numeric(df['price'].str.replace('[^\d.]', '', regex=True), errors='coerce')
    df = df[df['price'] >= 30]

    # Convert num_bids Col to an int and remove the 'bids' from each row    
    df['num_bids'] = df['num_bids'].astype(str)
    df['num_bids'] = pd.to_numeric(df['num_bids'].str.replace(r'\D', ''), errors='coerce').astype(pd.Int64Dtype())

    # Convert All Other Cols to Strings
    df['title'] = df['title'].astype(pd.StringDtype())
    df['condition'] = df['condition'].astype(pd.StringDtype())
    df['buy_it_now'] = df['buy_it_now'].astype(pd.StringDtype())
    df['best_offer'] = df['best_offer'].astype(pd.StringDtype())

    return df


### Function to get Auction data
def get_auction_data(df):

    auction_df = df.dropna()

    return auction_df


### Function to get Buy It Now data
def get_BIN_data(df):

    BIN_df = df.loc[(df['buy_it_now'] == 'Yes') | (df['best_offer'] == 'Yes')]

    return BIN_df


### Funtion to compute Avg Sold Price
def get_avg_price(df):

    avg_price = df['price'].mean()
    
    return avg_price


### Funtion to compute Avg Sold Price
def avg_price_cond(df):

    cond_avg_price = df.groupby('condition')['price'].mean()
    
    return cond_avg_price


def avg_price_month(df):

    avg_price_by_month = df.groupby(df['sold_date'].dt.strftime('%B'))['price'].mean().sort_values(ascending = False)
    
    return avg_price_by_month
