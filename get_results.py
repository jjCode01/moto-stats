import re
from typing import Any

import requests
from bs4 import BeautifulSoup

RESULTS_URL = "https://www.supercrosslive.com/results/current/"
URL_POSTFIX = {
    250: "S2F1PRESS.html",  # official 250 results
    450: "S1F1PRESS.html",  # official 450 results
    # 250: "S2F1RES.html",  # provisional 250 results
    # 450: "S1F1RES.html",  # provisional 450 results
}


def scrape_results(season: int, race_num: int, bike: int = 450) -> dict | None:
    """Scrape supercross race results from supercrosslive.com

    Args:
        season (int): Year of race
        race_num (int): Round Number
        bike (int, optional): Bike size, 250 or 450. Defaults to 450.

    Raises:
        ValueError: Invalid bike size

    Returns:
        dict | None: Race information and results
    """
    if bike not in (250, 450):
        raise ValueError(f"'bike' argument must be 250 or 450; got {bike}")

    official_results_url = f"{_race_url(season, race_num)}/{URL_POSTFIX[bike]}"

    page = requests.get(official_results_url, timeout=5)
    if page.status_code != 200:
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    race_info = soup.find_all("h4", {"class": "header-class"})
    result_table = soup.find("table")

    return {
        "Season": season,
        "Round": race_num,
        "Name": race_info[1].text,
        "City": _get_city(race_info[2].text),
        "State": _get_state(race_info[2].text),
        "Date": _get_date(race_info[3].text),
        "Results": _get_results(result_table.find_all("tr")[1:]),  # type: ignore
    }


def _get_city(val: str) -> str:
    city = re.search(r"(?<=\s-\s).+(?=,\s[A-Z]{2}$)", val)
    if city:
        return city.group()
    return ""


def _get_date(val: str) -> str:
    date = re.search(r"[JFMASOND]{1}[a-z].+\s\d{1,2},\s\d{4}$", val)
    if date:
        return date.group()
    return ""


def _get_element_text(val) -> str:
    if not val:
        return ""
    return val.text


def _get_results(rows: list) -> list[dict[str, Any]]:
    cols = [
        "#",
        "Rider",
        "Hometown",
        "Bike",
        "Qual",
        "Holeshot",
        "Laps Led",
        "Position",
        "Points",
    ]
    return [
        {col: _get_element_text(row.find("td", {"data-title": col})) for col in cols}
        for row in rows
    ]


def _get_state(val: str) -> str:
    state = re.search(r"(?<=,\s)[A-Z]{2}$", val)
    if state:
        return state.group()
    return ""


def _race_url(season: int, race_num: int) -> str:
    return f"{RESULTS_URL}{season}/S{str(season)[-2:]}{race_num * 5:02d}"


if __name__ == "__main__":
    race = scrape_results(2019, 1, 450)
    if race:
        print(f"Round {race['Round']} - {race['Name']}")
        print(race["Date"])
        print(f"{race['City']}, {race['State']}")
        for result in race["Results"]:
            print(f"{result['Position']}\t{result['Rider']}")

    else:
        print("Race not found")
