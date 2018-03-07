"""
This script will be used to acquire State Assembly and Senate representative information from http://findyourrep.legislature.ca.gov/
Ideally this script would use a command argument to allow for usage in different states.
"""


from bs4 import BeautifulSoup
import mechanize
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import sys
import urllib, urllib2
import pandas as pd

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
def parse_address_info():
    df = get_input_file()

    for index, row in df.iterrows():
        try:
            name = row['Name']
            street = row['Street Address']
            city = row['City']
            zip = row['Zip']

            site_response = get_rep_info(name, street, city, zip)

            soup = BeautifulSoup(site_response, 'html.parser')

        except Exception, e:
            print e


#  Submit Address data to  http://findyourrep.legislature.ca.gov/
def get_rep_info(name=None, street=None, city=None, zip=None):
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

        element_present = EC.presence_of_element_located((By.ID, 'element_id'))
        timeout = 2
        # WebDriverWait(driver, timeout).until(element_present)
        sleep(4)
        response = driver.page_source

        return response

    except Exception, e:
        print e


# Concatenate input file data with website response data and produce output file


if __name__ == '__main__':
    parse_address_info()
