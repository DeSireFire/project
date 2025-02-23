# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 17:33:27 2021

@author: guoxuan

scriping fdic summary of market share report 
- market share by different location 
- hhi  by different location

 It turns out to calcualte HHI by myself 
 database has some problem
-------------
1. State->County->City->Zip 
2. Metropolitan Statistical Area (MSA)



"""

import os

current_path=os.path.dirname(os.path.abspath('__file__'))

import sys

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
    
import time, re
from datetime import date, timedelta,datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException,TimeoutException
import selenium.common.exceptions as S_exceptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import pandas as pd





page_load_flag = ".tdHeaderSOD"

COL_mkt_share = ["Date",	"Year",	"MSA_name",	"Institution_Rank",	"Institution_Name",	"CERT",	
                    "State(Hqtrd)",	"Bank_Class",	"State/Federal_Charter",	"outmkt_num_offices",
                    	"outmkt_Depoits($000)",	"inmkt_num_offices",
                    	"inmkt_Depoits($000)","inmkt_mkt_share"]
COL_HHI = ["Date",	"Year",	"MSA_name",	"Num_Institutions",	"Total_Assets",	
           "Num_Offices",	"Depoits($000)","HHI"]


def choose_selections(driver, element_id, select_year):
    driver.find_element(By.ID, element_id).click()
    el = driver.find_element(By.ID, element_id) 
    for option in el.find_elements_by_tag_name('option'):
        if select_year in option.text :
            option.click()

def open_page(driver,url):
    # only firefox is OK !!! 
    try:
        driver.set_page_load_timeout(5)
        driver.get(url)
    except TimeoutException as ex:
        check=driver.find_element_by_css_selector(page_load_flag)
        if not check :
            print("problem with the page, restart it")
            driver.quit()
    
    return driver

def initial_driver(driver_path):        
    profile=webdriver.firefox.firefox_profile.FirefoxProfile()
#    # 1 - Allow all images
#    # 2 - Block all images
#    # 3 - Block 3rd party images 
    profile.set_preference("permissions.default.image", 2)
    options = FirefoxOptions()
    # options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options,firefox_profile=profile,executable_path=driver_path)        

    return driver


def open_table(driver,year,msa_index):
    ### 1. open the link 
    driver=open_page(driver,base_url)
    
    ### 2. navigate to the market share part 
    pro_forma=driver.find_element_by_id("tdTabDepositMarketShare")
    pro_forma.click()
    
    ### 3. select MSA option
    msa_selection = driver.find_element_by_css_selector("#divtdTabDepositMarketShare tr:nth-child(2) > td > label")
    msa_selection.click()
    
    ### 4. select year MSA part PFMSADepositDate
    year_selection = Select(driver.find_element_by_id('MSMSADepositDate'))
    year_selection.select_by_value(year)
    
    ### 3. msa area get PFMSASelected
    msa_selection = Select(driver.find_element(By.NAME, "MSMSASelected"))
    msa_selection.deselect_all()
    msa_selection.select_by_index(msa_index)
    
    ### 4. generate the report 
    driver.find_element_by_id("SubmitButton").click() 
    
    return driver 


def save_table(driver,Year,Date):
    ## creat the new empty dataframe
    (df_mkt_share, df_HHI) = create_dataframe()
    ## check the total assets part 
    asset_selection = Select(driver.find_element_by_name('sAssetsAsOf'))
    asset_selection.select_by_value("December 31, " + Year)
    
    ## navigate to the table 
    table = driver.find_element_by_xpath("//table[3]")
    table_raw_data = table.find_elements_by_tag_name("TR")
    
    if table != '':
    
        ### table info
        table_msa_info = table_raw_data[3].text
        ## header part  not important 
        # header_list = table_raw_data[4].find_elements_by_tag_name("TH")
        
        ## content part market share
        n_row = len(table_raw_data)
        for i in range(7,n_row-2):
            id_i = i-7
            row_data = [Date,Year,table_msa_info,str(id_i)]
            content_list = table_raw_data[i].find_elements_by_tag_name("TD")
            temp_row_data = [ele.text for ele in content_list]
            row_data.extend(temp_row_data)
            df_mkt_share.loc[id_i] = row_data
            id_i = id_i + 1
            
            

    
    else:
        df_mkt_share.loc[0] =  [Date,Year,table_msa_info,"0"] + ["-" for x in range(0,10)]

    
    return df_mkt_share


def create_dataframe():
    df_mkt_share = pd.DataFrame(columns= COL_mkt_share)
    return df_mkt_share




if __name__ == '__main__':
    
    
    df_mkt_share = create_dataframe()
    file_path = "D:\\github\\project\\web_spider\\fdic\\"
    file_name1 = "sum_market_share2_MSA"
    flag = 1
    if flag == 1:
        df_mkt_share.to_csv(file_path+file_name1+'.csv', sep='\t', encoding='utf-8',mode='a',index=False)
        

    '''
    --------------------------------------------------------------------------
    This script works on MSA over years 
    
    '''
    
    ## set up Year 
    Year_list = list(range(2000, 2011))
    Year_list = [str(x) for x in Year_list]
    Date_list = ["06-30-" + x for x in Year_list ]
    
    base_url = "https://www7.fdic.gov/sod/sodMarketBank.asp?barItem=2"
    driver_path="..//geckodriver.exe"
    
    
    driver=initial_driver(driver_path)
    
    ## loop over years and MSAs 
    ### start from year 
    for year_i in range(0,len(Year_list)):
        year = Year_list[year_i]
        Date = Date_list[year_i]
        ### over msa total 392 
        print("working on year "+ year)
        for msa_index in range(0,392):            
            ## open the table 
            driver = open_table(driver,year,msa_index)    
            ## save the data
            df_mkt_share_t = save_table(driver,year,Date)
            
            # save to the dataframe
            df_mkt_share=df_mkt_share.append(df_mkt_share_t,ignore_index=True)
            
       
            if msa_index % 50 == 0:
                time.sleep(5)
        
    df_mkt_share.to_csv(file_path+file_name1+'.csv', sep='\t', encoding='utf-8',index=False,mode='a', header=False)
    df_mkt_share = create_dataframe()