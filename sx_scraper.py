import requests
from bs4 import BeautifulSoup
import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

season = input('Enter Season: ')
race = int(input('Enter Round: '))

URL_450_MAIN = f'https://www.supercrosslive.com/results/current/{season}/S{season[-2:]}{race * 5:02d}/S1F1PRESS.html'
URL_250_MAIN = f'https://www.supercrosslive.com/results/current/{season}/S{season[-2:]}{race * 5:02d}/S2F1PRESS.html'

page_450_main = requests.get(URL_450_MAIN)
page_250_main = requests.get(URL_250_MAIN)

soup_450_main = BeautifulSoup(page_450_main.content, 'html.parser')
soup_250_main = BeautifulSoup(page_250_main.content, 'html.parser')

race_info_450 = soup_450_main.find_all('h4', {'class': 'header-class'})
race_info_250 = soup_250_main.find_all('h4', {'class': 'header-class'})

main_450 = soup_450_main.find('table')
main_250 = soup_250_main.find('table')

nums_450_main = [num.text for num in main_450.find_all('td', {'data-title': '#'})]
riders_450_main = [rider.text for rider in main_450.find_all('td', {'data-title': 'Rider'})]
bikes_450_main = [bike.text for bike in main_450.find_all('td', {'data-title': 'Bike'})]
nums_250_main = [num.text for num in main_250.find_all('td', {'data-title': '#'})]
riders_250_main = [rider.text for rider in main_250.find_all('td', {'data-title': 'Rider'})]
bikes_250_main = [bike.text for bike in main_250.find_all('td', {'data-title': 'Bike'})]

max_name = len(max(
    max(riders_450_main, key=len),
    max(riders_250_main, key=len)
))

for info in race_info_450[:4]:
    print(info.text)

print(f'\n{race_info_450[4].text}')
print(f'Pos\tNum\tRider{" " * (max_name - len("Rider"))}\tBike')
for place, (num, rider, bike) in enumerate(zip(nums_450_main, riders_450_main, bikes_450_main), start=1):
    print(f'{place}\t{num}\t{rider}{" " * (max_name - len(rider))}\t{bike.split()[0]}')
    
print(f'\n{race_info_250[4].text}')
print(f'Pos\tNum\tRider{" " * (max_name - len("Rider"))}\tBike')
for place, (num, rider, bike) in enumerate(zip(nums_250_main, riders_250_main, bikes_250_main), start=1):
    print(f'{place}\t{num}\t{rider}{" " * (max_name - len(rider))}\t{bike.split()[0]}')

