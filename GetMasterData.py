import json
import logging
import time

import requests
import waybackpy
from bs4 import BeautifulSoup
from lxml import html
from waybackpy import exceptions

IMPDS_BASE_URL = 'http://impds.nic.in/portal?'
monthly_stats = []

def write_json(new_data, filename):
    with open(filename, 'w') as file:
        json.dump(new_data, file, indent=4)

def getSaleData(month,year):
    logging.info('====Inside getSaleData === for month ' + month.zfill(2) + year)
    sale_state = []
    monthly_sale_date = []
    monthly_stat = {}
    url = IMPDS_BASE_URL 
    params = {"month": month, "year": year}

    s = BeautifulSoup(requests.get(url, params=params).text, 'lxml')

    #Get Monthly Summary Stats
    navbar = s.find_all('div',attrs={'class':'metro-nav-block1'})
    monthly_stat['states_joined'] = navbar[0].find('span').text.strip()
    monthly_stat['ration_cards'] =  navbar[1].find('span').text.strip()
    monthly_stat['total_beneficiaries'] =  navbar[2].find('span').text.strip()
    monthly_stat['total_txn'] =  navbar[3].find('span').text.strip()
    monthly_stat['pmgkay_txn'] = navbar[3].text.strip().split('(PMGKAY-')[1].split(')')[0]
    monthly_stat['wheat_in_kg'] = navbar[4].find('span').text.strip()
    monthly_stat['rice_in_kg'] = navbar[5].find('span').text.strip()
    monthly_stat['pmgkay_wheat_in_kg'] = navbar[6].find('span').text.strip()
    monthly_stat['pmgkay_rice_in_kg'] = navbar[7].find('span').text.strip()
    monthly_stat['year_month'] = year + month.zfill(2)

    # #For each col in home state
    # for row in s.find_all('thead')[0].find_all('tr')[1].find_all('th'):
    #     home_state.append(row.text)

    #For each row in sale state
    for row in s.find_all('tbody')[0].find_all('tr'):
        current_sale_state = row.find('th').text
        sale_state.append(current_sale_state)
        cells = row.find_all('td')
        for cell in cells:
            if bool(cell.find('a')):
                sale_data = {}
                sale_data['sale_state'] = current_sale_state
                sale_data['home_state'] = cell.find('a')['href'].split('home_state=')[1].upper()
                sale_data['quantity'] = cell.find('a').text
                sale_data['year_month'] = year + month.zfill(2)
                monthly_sale_date.append(sale_data)
    logging.debug(monthly_sale_date)
    monthly_stats.append(monthly_stat)
    return monthly_sale_date

def main():
    logging.basicConfig(filename='./ONORCData' + time.strftime("%Y%m%d-%H%M%S") +
                        '.log', format='%(asctime)s %(message)s', level=logging.INFO)

    overall_sale_data = []
    for year in range(2019,2022):
        for month in range(1,13):
            if((year == 2019 and month <=6) or (year == 2021 and month >=8)):
                continue
            overall_sale_data.append(getSaleData(str(month),str(year)))
    overall_sale_data = [sale_data for monthly_sale_data in overall_sale_data for sale_data in monthly_sale_data]  

    write_json(overall_sale_data, './data/overall_sale_data.json')
    write_json(monthly_stats,'./data/monthly_stats.json' )

if __name__ == "__main__":
    main()
