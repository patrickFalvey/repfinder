"""
This script will be used to acquire State Assembly and Senate representative information from http://findyourrep.legislature.ca.gov/
The input file name will be used as a command line argument when running the script.

Example: 'python app.py test.xlsx'
"""


from bs4 import BeautifulSoup, SoupStrainer
import mechanize
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import urllib, urllib2
import pandas as pd
import numpy as np
import seaborn as sns
from multiprocessing import Pool

URL = r"http://findyourrep.legislature.ca.gov/"


# Parse input file rows into Street Address, City and Zip data
def get_input_file():
    try:
        input_file_name = sys.argv[1]
    except AttributeError:
        sys.exit('You must enter an input file name when running this script\n'
                 'Example: python app.py test.xlsx')

    try:
        data_frame = pd.read_excel("input/" + input_file_name)
        return data_frame
    except Exception, e:
        sys.exit(e)


# Parse input file rows into Street Address, City and Zip data
def parse_address_info(dataframe=None):
    df = dataframe

    if df:
        for index, row in df.iterrows():
            if row['State'] == 'CA':
                try:
                    street = row['Street']
                    city = row['City']
                    zip = row['Zip']
                    line = {}

                    site_response = get_rep_info(street, city, zip)

                    soup = BeautifulSoup(site_response, "html5lib")
                    for link in soup.find('div', id='tabResults'):
                        if link.contents:
                            try:
                                if 'Assembly (District' in link.contents[0]:
                                    df.loc[index, 'Assembly District'] = link.contents[0][-3:-1]
                                    print link.contents[0][-3:-1]
                            except:
                                pass

                            try:
                                if 'Senate (District' in link.contents[0]:
                                    df.loc[index, 'Senate District'] = link.contents[0][-3:-1]
                                    print link.contents[0][-3:-1]
                            except:
                                pass

                            try:
                                if len(link.contents) > 1 and 'Assembly Member ' in link.contents[1].get_text():
                                    df.loc[index, 'Assembly Member'] = link.contents[1].get_text().split('Assembly Member ')[1]
                                    print link.contents[1].get_text().split('Assembly Member ')[1]
                                    print row['Assembly Member']
                            except:
                                pass

                            try:
                                if len(link.contents) > 1 and 'Senator ' in link.contents[1].get_text():
                                    df.loc[index, 'State Senator'] = link.contents[1].get_text().split('Senator ')[1]
                                    print link.contents[1].get_text().split('Senator ')[1]
                            except:
                                pass

                except Exception, e:
                    print e

                df.append(line, ignore_index=True)

    writer = pd.ExcelWriter("output/output" + sys.argv[1])
    df.to_excel(writer, 'Sheet 1')
    writer.save()


#  Submit Address data to  http://findyourrep.legislature.ca.gov/
def get_rep_info(street=None, city=None, zip=None):
    try:
        driver = webdriver.Chrome()
        driver.get(URL)
        street_field = driver.find_element_by_id("street")
        city_field = driver.find_element_by_id("city")
        zip_field = driver.find_element_by_id("ZIP")
        locate_button = driver.find_element_by_id("locate")

        # Assign values to form fields
        street_field.send_keys(street)
        city_field.send_keys(city)
        zip_field.send_keys(zip)

        # Submit form
        locate_button.click()

        sleep(2)
        response = driver.page_source

        return response

    except Exception, e:
        print e


# Concatenate input file data with website response data and produce output file


if __name__ == '__main__':
    parse_address_info()
