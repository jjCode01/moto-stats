from datetime import datetime
import re
import sys
from typing import Any

from bs4 import BeautifulSoup, Tag
import requests
from rich.console import Console
from rich.table import Table, Column


FIRST_YEAR = 2013
NUM_OF_RACES = 17
RESULTS_URL = "https://www.supercrosslive.com/results/current/"
URL_POSTFIX = {
    "OF": {  # official results
        250: "S2F1PRESS.html",
        450: "S1F1PRESS.html",
    },
    "PR": {  # provisional results
        250: "S2F1RES.html",
        450: "S1F1RES.html",
    },
    "PT": {  # points standing
        250: "S2F1POINTS.html",
        450: "S1F1POINTS.html",
    },
}
RACE_STATS = [
    "Position",
    "#",
    "Rider",
    "Hometown",
    "Bike",
    "Qual",
    "Holeshot",
    "Laps Led",
    "Points",
]

SEASON_STATS = [
    "Position",
    "#",
    "Rider",
    "Hometown",
    "Total Points",
    *list(range(1, 18)),
]

def _validate_args(season: int, bike: int) -> None:
    if bike not in (250, 450):
        raise ValueError(f"'bike' must be 250 or 450; got {bike}")

    if FIRST_YEAR > season > datetime.now().year:
        raise ValueError(
            f"'season' must be between {FIRST_YEAR} and {datetime.now().year}; got {season}"
        )


def scrape_season_results(season: int, bike: int = 450) -> dict | None:
    """Scrape supercross season results from supercrosslive.com

    Args:
        season (int): Year
        bike (int, optional): 250 or 450 class. Defaults to 450.

    Returns:
        dict | None: Season information and results
    """
    _validate_args(season, bike)

    for _race in range(NUM_OF_RACES, 0, -1):
        results_url = f"{_race_url(season, _race)}/{URL_POSTFIX["PT"][bike]}"
        page = requests.get(results_url, timeout=5)
        if page.status_code == 200:
            break
    else:
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    result_table = soup.find("table")

    return {
        "Class": bike,
        "Results": _get_season_results(result_table.find_all("tr")[1:]),  # type: ignore
        "Season": season,
    }


def scrape_race_results(season: int, race_num: int, bike: int = 450) -> dict | None:
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
    _validate_args(season, bike)

    result_status = ""

    for status in ("OF", "PR"):
        results_url = f"{_race_url(season, race_num)}/{URL_POSTFIX[status][bike]}"
        page = requests.get(results_url, timeout=5)
        if page.status_code == 200:
            result_status = status
            break
    else:
        return None

    soup = BeautifulSoup(page.content, "html.parser")
    race_info: list[Tag] = soup.find_all("h4", {"class": "header-class"})
    result_table = soup.find("table")

    return {
        "City": _get_city(race_info[2].text),
        "Class": bike,
        "Date": _get_date(race_info[3].text),
        "Name": race_info[1].text,
        "Results Status": "Official" if result_status == "OF" else "Provisional",
        "Results": _get_race_results(result_table.find_all("tr")[1:]),  # type: ignore
        "Round": race_num,
        "Season": season,
        "State": _get_state(race_info[2].text),
        "Triple Crown": _is_triple_cown(soup),
    }


def _is_triple_cown(content: BeautifulSoup) -> bool:
    return content.find("td", {"data-title": "M1"}) is not None


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


def _get_race_results(rows: list[Tag]) -> list[dict[str, Any]]:
    _results = []
    for pos, row in enumerate(rows, 1):
        _stat = {col: _get_td_text(row, {"data-title": col}) for col in RACE_STATS}
        _stat["Position"] = pos
        _results.append(_stat)
    return _results


def _get_season_results(rows: list[Tag]) -> list[dict[str, Any]]:
    _results = []
    for pos, row in enumerate(rows, 1):
        _stat = {col: _get_td_text(row, {"data-title": col}) for col in SEASON_STATS}
        _stat["Position"] = pos
        _results.append(_stat)
    return _results


def _get_state(val: str) -> str:
    state = re.search(r"(?<=,\s)[A-Z]{2}$", val)
    if state:
        return state.group()
    return ""


def _get_td_text(row: Tag | None, params: dict[str, str]) -> str | int | bool:
    if not row:
        return ""
    if not (td := row.find("td", params)):
        return ""
    if td.text.isnumeric():
        return int(td.text)
    return td.text


def _race_url(season: int, race_num: int) -> str:
    season_path = f"{season}/S{str(season)[-2:]}"
    if season == 2023 and race_num == 2:
        # Race 2 in 2023 does not follow the typical numbering convention
        return f"{RESULTS_URL}{season_path}33"
    return f"{RESULTS_URL}{season_path}{race_num * 5:02d}"

def _print_race_results_table(**vals) -> None:
    race_tile = f"{vals['Season']} Round {vals['Round']} - {vals['Name']} - {vals['Class']}"
    triple_crown = '(Triple Crown)' if vals['Triple Crown'] else ''

    headers: list[Column] = [
        Column("Position", justify="left"),
        Column("Number", justify="center"),
        Column("Rider", justify="left"),
        Column("Hometown", justify="left"),
        Column("Bike", justify="left"),
        Column("Qual", justify="center"),
        Column("Holeshot", justify="center"),
        Column("Laps Led", justify="center"),
        Column("Points", justify="center"),
    ]
    table = Table(
        *headers,
        title=f"{race_tile} {vals['Results Status']} Results {triple_crown}",
    )

    for result in vals["Results"]:
        rider = [str(result[stat]) for stat in RACE_STATS]
        table.add_row(*rider)

    console = Console()
    console.print(table)

def _print_season_results_table(**vals) -> None:
    season_title = f"{vals['Season']} Season - {vals['Class']} Class"

    headers: list[Column] = [
        Column("Position", justify="left"),
        Column("Number", justify="center"),
        Column("Rider", justify="left"),
        Column("Hometown", justify="left"),
        Column("Total Points", justify="left"),
        *[Column(str(r)) for r in range(1, 18)],
    ]
    table = Table(
        *headers,
        title=season_title,
    )

    for result in vals["Results"]:
        rider = [str(result[stat]) for stat in SEASON_STATS]
        table.add_row(*rider)

    console = Console()
    console.print(table)


if __name__ == "__main__":
    args = sys.argv

    year: int = 0
    round_num: int = 0
    bike_size: int = 0

    if len(args) > 1:
        for arg in args:
            if arg.isnumeric():
                if FIRST_YEAR <= int(arg) <= datetime.now().year:
                    year = int(arg)
                elif int(arg) in (250, 450):
                    bike_size = int(arg)
                elif 1 <= int(arg) <= NUM_OF_RACES:
                    round_num = int(arg)

    if not year:
        year = int(input(f"Enter Year [{FIRST_YEAR} - {datetime.now().year}]: "))
    if not bike_size:
        bike_size = int(input("Enter Class [250 or 450]: "))
    if not round_num:
        round_num = int(
            input(f"Enter Round [1-{NUM_OF_RACES}] or 0 for season results: ")
        )

    if round_num:
        if _race := scrape_race_results(year, round_num, bike_size):
            _print_race_results_table(**_race)
        else:
            print("Race not found")

    else:
        if _season := scrape_season_results(year, bike_size):
            _print_season_results_table(**_season)
        else:
            print("Season not found")
