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


# URL_450_MAIN = f'https://www.supercrosslive.com/results/current/{season}/S{season[-2:]}{race * 5:02d}/S1F1PRESS.html'
# URL_250_MAIN = f'https://www.supercrosslive.com/results/current/{season}/S{season[-2:]}{race * 5:02d}/S2F1PRESS.html'

# page_450_main = requests.get(URL_450_MAIN)
# page_250_main = requests.get(URL_250_MAIN)

# soup_450_main = BeautifulSoup(page_450_main.content, 'html.parser')
# soup_250_main = BeautifulSoup(page_250_main.content, 'html.parser')

# race_info_450 = soup_450_main.find_all('h4', {'class': 'header-class'})
# race_info_250 = soup_250_main.find_all('h4', {'class': 'header-class'})

# main_450 = soup_450_main.find('table')
# main_250 = soup_250_main.find('table')

# nums_450_main = [num.text for num in main_450.find_all('td', {'data-title': '#'})]
# riders_450_main = [rider.text for rider in main_450.find_all('td', {'data-title': 'Rider'})]
# bikes_450_main = [bike.text for bike in main_450.find_all('td', {'data-title': 'Bike'})]
# nums_250_main = [num.text for num in main_250.find_all('td', {'data-title': '#'})]
# riders_250_main = [rider.text for rider in main_250.find_all('td', {'data-title': 'Rider'})]
# bikes_250_main = [bike.text for bike in main_250.find_all('td', {'data-title': 'Bike'})]

# max_name = len(max(
#     max(riders_450_main, key=len),
#     max(riders_250_main, key=len)
# ))

# for info in race_info_450[:4]:
#     print(info.text)

# print(f'\n{race_info_450[4].text}')
# print(f'Pos\tNum\tRider{" " * (max_name - len("Rider"))}\tBike')
# for place, (num, rider, bike) in enumerate(zip(nums_450_main, riders_450_main, bikes_450_main), start=1):
#     print(f'{place}\t{num}\t{rider}{" " * (max_name - len(rider))}\t{bike.split()[0]}')
    
# print(f'\n{race_info_250[4].text}')
# print(f'Pos\tNum\tRider{" " * (max_name - len("Rider"))}\tBike')
# for place, (num, rider, bike) in enumerate(zip(nums_250_main, riders_250_main, bikes_250_main), start=1):
#     print(f'{place}\t{num}\t{rider}{" " * (max_name - len(rider))}\t{bike.split()[0]}')

def create_race(conn, race):
    """
    Create a new race into the races table
    :param conn:
    :param race:
    :return: project id
    """
    sql = ''' INSERT INTO Races(Series,Year,Round,Date,Name,City,State)
              VALUES(?,?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, race)
    conn.commit()
    # return cur.lastrowid

def get_next_race():
    sx_seasons = range(2014, 2022)  # supercross seasons from 2013 thru 2021
    sx_rounds = range(1, 18)  # there are 17 rounds in a supercross season 

    for season in sx_seasons:
        for race in sx_rounds:
            # print(season, race)
            URL = f'https://www.supercrosslive.com/results/current/{season}/S{str(season)[-2:]}{race * 5:02d}/S1F1PRESS.html'
            
            page = requests.get(URL)
            if page.status_code == 200:
                soup = BeautifulSoup(page.content, 'html.parser')
                race_info = soup.find_all('h4', {'class': 'header-class'})
                date = ' '.join(race_info[3].text.split()[4:])
                name = race_info[1].text
                city_i = race_info[2].text.find('-')
                print(city_i)
                city = ''.join(race_info[2].text[city_i + 2:-4])
                state = race_info[2].text.split()[-1]

                yield "SX", season, race, date, name, city, state


def main():
    database = "moto-stats.db"

    # create a database connection
    conn = create_connection(database)
    print('Connected!')
    # for race in get_next_race():
    #     print(race)
    with conn:
        # populate races

        for race in get_next_race():
            create_race(conn, race)
            print('Race Added: ', race)


if __name__ == '__main__':
    main()
