# -*- coding: utf-8 -*-
"""
Created on Thu Jun  5 14:45:20 2025
@author: emanuele.chini
definition of the class ptf (portafolio of ETFs)

"""

import pandas as pd
import numpy as np
import re
import time
import string
#pip install selenium

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import requests
import datetime
import pickle


class ptfs:                  # define class ptf (= portfolio of ETFs and portfolio of stocks)
   ## check that the input is a dictionary with valid ISINs as keys and quantities as values
    def __init__(self, PTF_dict:dict):
        if set(PTF_dict.keys()) != {"ETF", "EQUITY"}:
            raise ValueError("PTF_dict must contain only the keys 'ETF' and 'EQUITY'")
        # define the attributes of the class
        self.data      = PTF_dict
        self.isinETF_quantity_dict = self.data['ETF'] 
        self.isinEQ_quantity_dict =  self.data['EQUITY']
        self.isin_quantity_dict = self.isinETF_quantity_dict| self.isinEQ_quantity_dict

        self.isinsETF = list(self.isinETF_quantity_dict.keys())
        self.isinsEQ  = list(self.isinEQ_quantity_dict.keys())

        invalid_isins = [isin for isin in self.isin_quantity_dict.keys() if not ptfs.is_valid_isin(isin)]
        if invalid_isins:
           raise ValueError(f"Invalid ISIN(s) found: {invalid_isins}")
  
    
    ## function that checks if an ISIN is a valid ISIN
    @staticmethod
    def is_valid_isin(isin: str) -> bool:
        if len(isin) != 12:
            return False
    
        if not isin[:2].isalpha() or not isin[:2].isupper():
            return False
    
        if not all(c.isalnum() for c in isin):
            return False
    
        # Convert letters to numbers: A=10, B=11, ..., Z=35
        def convert_char(c):
            if c.isdigit():
                return c
            return str(10 + string.ascii_uppercase.index(c))
    
        transformed = ''.join(convert_char(c) for c in isin[:-1])  # Exclude check digit
        digits = ''
        for char in transformed:
            digits += char
    
        # Apply Luhn algorithm
        # Reverse the digits for easier indexing
        reversed_digits = digits[::-1]
        total = 0
        for i, d in enumerate(reversed_digits):
            n = int(d)
            if i % 2 == 0:
                n *= 2
                if n > 9:
                    n -= 9
            total += n
    
        check_digit = (10 - (total % 10)) % 10
        return str(check_digit) == isin[-1]



    ## collect non-static info from justETF (e.g. price) for equity and ETF
    def ns_info__EQ_ET(self,  t=1):
        """
        isins:  List of isins of ETFs (that are present in just ETF)
        t=1:    Sleep t seconds to allow page to start loading (optional but can help flaky loads)

        output is a dataframe containing for each ETF the currency, price, date,
        daily change abs, daily_change_pct, spread, low_52w, High_52w
        @author: emanuele.chini
        """

        # Setup Chrome WebDriver
        options = Options()
        options.add_argument("--start-maximized")
        options.add_argument("--headless") # comment if you want to open the browser 
        #driver = webdriver.Chrome(service=Service(), options=options)


        #options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
             service=Service("/usr/lib/chromium-browser/chromedriver"),
             options=options
             )

        
        # Navigate to justETF homepage to set cookies
        url = "https://www.justetf.com/en/"
        driver.get(url)
        
        # allow cookies
        wait = WebDriverWait(driver, 10)
        allow_all_button = wait.until(EC.element_to_be_clickable(
            (By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll")
        ))
        allow_all_button.click()
        
        # open each ETF page and collect info
        results = {}
        for isin in self.isinsETF:
            url = f"https://www.justetf.com/en/etf-profile.html?isin={isin}"
            try:
                driver.get(url)
                time.sleep(t)    # otherwise is too fasrt
                elements = driver.find_element(By.ID, "realtime-quotes")
                results[isin] = elements.text
            except:
                results[isin]=''

        for isin in self.isinsEQ:
            url = f"https://www.justetf.com/en/stock-profiles/{isin}"
            try:
                driver.get(url)
                time.sleep(t)    # otherwise is too fasrt
                elements = driver.find_element(By.ID, "realtime-quotes")
                results[isin] = elements.text
            except:
                results[isin]=''

        # Close the WebDriver          
        driver.quit()

        # parse the results        
        rows = []
        for isin, info in results.items():
            lines = info.split('\n')
            
            try:
                currency_price = lines[0].split()
                currency = currency_price[0]
                price = float(currency_price[1])
                
        
                date_str = re.search(r'\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}', lines[1]).group(0)
                date = pd.to_datetime(date_str, format='%d/%m/%Y %H:%M:%S')
                
                
                #daily_change_abs, daily_change_pct = lines[2].split('|')
                #daily_change_abs = float(daily_change_abs.replace('+', '').replace(',', '.'))
                #daily_change_pct = float(daily_change_pct.replace('+', '').replace('%', '').replace(',', '.'))
                
                #spread = float(lines[5].replace('%', '').replace(',', '.'))
                
                #low_52w = float(lines[7].replace(',', '.'))
                #high_52w = float(lines[8].replace(',', '.'))
            
                rows.append({
                    'ISIN': isin,
                    'currency': currency,
                    'price': price,
                    'date': date,
                    #'daily_change_abs': daily_change_abs,
                    #'daily_change_pct': daily_change_pct,
                    #'spread': spread,
                    #'low_52w': low_52w,
                    #'high_52w': high_52w
                })
            except:
                rows.append({
                    'ISIN': isin,
                    'currency':  np.nan,
                    'price': np.nan,
                    'date':  np.nan,
                    #'daily_change_abs': np.nan,
                    #'daily_change_pct': np.nan,
                    #'spread': np.nan,
                    #'low_52w': np.nan,
                    #'high_52w': np.nan
                })
                    
        
        df = pd.DataFrame(rows)
        #df['price_adj_spread'] = df['price']-df['spread']/2
        return(df)


    

# Main execution when script runs directly
def main():
# We record the price and quantity for each holding in the portfolio.
# This allows tracking changes in the quantity of any security over time
# (via updates to portfolio.xlsx), and prevents artificial jumps in total value
# when new assets are added.
# The output is a time-series of each holding’s quantity and price. 
    ptf        = pd.read_excel('portfolio.xlsx') # upload the ptf 
    ptf_ETF    = ptf[ptf.TYPE.isin(["ETF"   ])][["ISIN", "q"]].groupby("ISIN").sum().to_dict()['q']        # take the ETF
    ptf_EQUITY = ptf[ptf.TYPE.isin(["EQUITY"])][["ISIN", "q"]].groupby("ISIN").sum().to_dict()['q']        # take the equity
    #ptf_ETF_EQ = ptf[ptf.TYPE.isin(["ETF","EQUITY"])][["ISIN", "q"]]
    My_ptf = {'EQUITY': ptf_EQUITY,
               'ETF':   ptf_ETF
              }
    T = datetime.datetime.now().strftime("%I:%M %p %m/%d/%Y")
    ptf_info = ptfs(My_ptf).ns_info__EQ_ET()                                                               # retrieve the equinfo
    ptf['price'] = ptf['ISIN'].map(dict(ptf_info[['ISIN','price']].values))
    #ptf_ETF_EQ['$VALUE'] = ptf_ETF_EQ.q*(ptf_ETF_EQ.price)
    data = ptf[['ISIN','q','price']]                                                               # take the prices and quantities 
    data['t'] = T
    # upload the TS file with the new data
    try:
        with open('time_series.pkl', 'rb') as f:
            data_old = pickle.load(f)
        data = pd.concat([data_old,data])
        with open('time_series.pkl', 'wb') as f:
            pickle.dump(data, f)
    except:
        with open('time_series.pkl', 'wb') as f:
            pickle.dump(data, f)
    


if __name__ == '__main__':
    main()  # Just run it
    # Script exits with code 0 automatically when don






