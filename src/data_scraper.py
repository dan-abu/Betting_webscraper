"""
Scrapes track names, race numbers, race URLs and race time
from Swiftbet Australia for today and tomorrow.
"""
import re
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from datetime import datetime as dt
from datetime import timedelta

class Bookie_Data():
    """Creating class for bookie data"""
    def __init__(self, url: str, scrape_time: str, xpaths_file: str) -> None:
        """Initialising bookie class"""
        self.url = url
        self.df = None
        self._table_count = 0
        self._track_names = []
        self._race_names = {}
        self._race_data = []
        self._file_creation_time = None
        self._scrape_time = scrape_time
        self.xpaths_file = xpaths_file
        self.tomorrows_races_xpath = None
        self._all_race_tables_xpath = None
        self._race_table_xpath = None
        self._race_table_row_xpath = None
        self._race_table_cell_xpath = None
        self._race_table_track_name_xpath = None
        self._race_table_row_track_name_xpath = None
        self._race_category_xpath = None
        self._race_category_columns_xpath = None
        self._race_category_headers_xpath = None

    def load_xpaths(self) -> None:
        """Reads xpaths file and sets xpath variables"""
        with open(self.xpaths_file, 'r') as file:
            lines = file.readlines()

        self.tomorrows_races_xpath = lines[0]
        self._all_race_tables_xpath = lines[1]
        self._race_table_xpath = lines[2]
        self._race_table_row_xpath = lines[3]
        self._race_table_cell_xpath = lines[4]
        self._race_table_cell_links_xpath = lines[5]
        self._race_table_cell_link_xpath = lines[6]
        self._race_table_track_name_xpath = lines[7]
        self._race_table_row_track_name_xpath = lines[8]
        self._race_category_xpath = lines[9]
        self._race_category_columns_xpath = lines[10]
        self._race_category_headers_xpath = lines[11]

    @staticmethod
    def parse_time_string(time_str: str) -> int:
        """Converts time string into integer (seconds)"""
        total_seconds = 0
        parts = re.findall(r"(-?\d+)([dhms])", time_str)
        for value, unit in parts:
            value = int(value)
            if unit == "d":
                total_seconds += value * 86400
            elif unit == "h":
                total_seconds += value * 3600
            elif unit == "m":
                total_seconds += value * 60
            elif unit == "s":
                total_seconds += value
        return total_seconds

    def calculate_race_time(self, time_left: int) -> str:
        """Returns actual race time in format"""
        seconds_left = self.parse_time_string(time_left)
        now = dt.now()
        race_time = now + timedelta(seconds=seconds_left)
        return race_time.strftime("%H:%M:%S %Y-%m-%d")

    @staticmethod
    def get_element_count(xpath:str) -> None:
        """Get number of elements in part of webpage"""
        return len(driver.find_elements(By.XPATH, xpath))

    def get_all_cell_values(self) -> None:
        """Get race times and race links"""
        for i in range(1, self._table_count):
            row_count = len(
                driver.find_elements(
                    By.XPATH,
                    self._race_table_xpath.format(i=i),
                )
            )
            for j in range(1, row_count + 1):
                row_cell_values = []
                cell_count = len(
                    driver.find_elements(
                        By.XPATH,
                        self._race_table_row_xpath.format(i=i, j=j),
                    )
                )
                for k in range(1, cell_count + 1):
                    cell_text = driver.find_element(
                        By.XPATH,
                        self._race_table_cell_xpath.format(i=i, j=j, k=k),
                    )
                    if cell_text.text:
                        if cell_text.text == "CLOSED":
                            row_cell_values.append("")
                        elif cell_text.text == "ABANDONED":
                            row_cell_values.append("")
                        elif "/" in cell_text.text:
                            row_cell_values.append("")
                        else:
                            race_time = self.calculate_race_time(cell_text.text)
                            row_cell_values.append(race_time)
                    else:
                        row_cell_values.append("")
                    cell_link_count = len(
                        driver.find_elements(
                            By.XPATH,
                            self._race_table_cell_links_xpath.format(i=i, j=j, k=k),
                        )
                    )
                    if cell_link_count > 0:
                        cellLink = driver.find_element(
                            By.XPATH,
                            self._race_table_cell_link_xpath.format(i=i, j=j, k=k),
                        )
                        row_cell_values.append(cellLink.get_attribute("href"))
                    else:
                        row_cell_values.append("")

                self._race_data.append(row_cell_values)

    def get_track_names(self) -> None:
        """Gets track names"""
        for i in range(1, self._table_count):
            row_count = len(
                driver.find_elements(
                    By.XPATH,
                    self._race_table_track_name_xpath.format(i=i),
                )
            )
            for j in range(1, row_count + 1):
                track_name = driver.find_element(
                    By.XPATH,
                    self._race_table_row_track_name_xpath.format(i=i, j=j),
                )
                self._track_names.append(track_name.text)

    def get_race_names(self) -> None:
        """Get race names"""
        for i in range(1, self._table_count):
            table_race_names = []
            race_category = driver.find_element(
                By.XPATH,
                self._race_category_xpath.format(i=i),
            )
            column_count = len(
                driver.find_elements(
                    By.XPATH,
                    self._race_category_columns_xpath.format(i=i),
                )
            )
            for j in range(1, column_count + 1):
                race_name = driver.find_element(
                    By.XPATH,
                    self._race_category_headers_xpath.format(i=i, j=j),
                )
                table_race_names.append(race_name.text)
            self._race_names[race_category.text] = table_race_names

    def create_df(self) -> None:
        """Creates DataFrame from scraped data"""
        cols = max([value for value in self._race_names.values()], key=len)
        race_info = ["Time", "Link"]
        new_cols = pd.MultiIndex.from_product([cols, race_info])
        self.df = pd.DataFrame(data=self._race_data, index=self._track_names, columns=new_cols)

def scrape(bookies: Bookie_Data) -> None:
    """Scrapes web data"""
    bookies._table_count = bookies.get_element_count(xpath=bookies._all_race_tables_xpath) + 1 #counting number of tables (i.e. race categories), add one because of future use of range(1, bookies._table_count)
    bookies.get_track_names()
    bookies.get_race_names()
    bookies.get_all_cell_values()

def main() -> None:
    """Entry point to programme"""
    global driver, day_check
    driver = webdriver.Chrome()
    url = sys.argv[1]
    day_check = sys.argv[2]
    scrape_time = dt.now()
    xpaths_file = sys.argv[3]
    bookies = Bookie_Data(url=url, xpaths_file=xpaths_file, scrape_time=scrape_time)
    bookies.load_xpaths()
    
    driver.get(url)
    time.sleep(20)

    if day_check == "tomorrow":
        # Getting tomorrow's data
        driver.find_element(
            By.XPATH,
            bookies.tomorrows_races_xpath,
        ).click()
        time.sleep(20)

    try:
        scrape(bookies=bookies)
    except NoSuchElementException as e:
        print(e)
        scrape(bookies=bookies)

    bookies._file_creation_time = dt.now().strftime("%Y-%m-%d_%H%M%S")
    bookies.create_df()

    if day_check == "tomorrow":
        bookies.df.to_csv(
            f"data/tomorrow_races_data{bookies._file_creation_time}.csv", header=True, index=True
        )
    else:
        bookies.df.to_csv(
            f"data/today_races_data{bookies._file_creation_time}.csv", header=True, index=True
        )

    driver.quit()

if __name__ == "__main__":
    main()