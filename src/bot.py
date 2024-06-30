"""
Scrapes current market prices for horses participating in
a selected race
"""

import sys
import time
import random
import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime as dt


def csvToDF(csv: str) -> pd.DataFrame:
    """Turn given CSV into DF"""
    races = pd.read_csv(csv, header=[0, 1], index_col=[0])
    return races


def getRandomRace(df: pd.DataFrame) -> pd.DataFrame:
    """Randomly select race from csv"""
    raceInfo = ["Time", "Link"]
    placeholder = ["Placeholder"]
    randomRace = pd.DataFrame(
        index=["Placeholder"],
        columns=pd.MultiIndex.from_product([placeholder, raceInfo]),
    )

    randomTrack = df.sample(n=1, axis=0)
    trackName = randomTrack.index[0]

    ogCols = list(randomTrack.columns)
    newCols = []
    for col in ogCols:
        newCols.append(col[0])
    newCols = set(newCols)
    newCols = list(newCols)

    nameRandomRace = random.choice(newCols)
    dfNameRandomRace = [nameRandomRace]
    randomRace.index = randomTrack.index
    newCol = pd.MultiIndex.from_product([dfNameRandomRace, raceInfo])
    randomRace.columns = newCol

    randomRace.loc[trackName, (nameRandomRace, "Time")] = randomTrack.loc[
        trackName, (nameRandomRace, "Time")
    ]
    randomRace.loc[trackName, (nameRandomRace, "Link")] = randomTrack.loc[
        trackName, (nameRandomRace, "Link")
    ]

    return randomRace


def getRandomRaceWithTimeout(df: pd.DataFrame, timeout: int = 60) -> pd.DataFrame:
    """Calling getRandomRace with a timeout"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        race = getRandomRace(df)
        if not pd.isna(race.iloc[0, 0]):
            return race
    raise TimeoutError(
        "Function getRandomRace did not complete within 1 minute.\nIt appears there are no more races today.\nDouble-check the CSV file."
    )


def getHeaders(
    xpath='//*[@id="main-content-page"]/div[2]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[2]/div/div[3]/div[6]/div[1]',
):
    """Get market price headers"""
    headers = driver.find_element(By.XPATH, xpath)
    headers = headers.text
    headers = headers.split("\n")
    return headers


def getIndex(rowCount: int) -> list:
    """Get market price Index"""
    indexes = []
    for i in range(1, rowCount + 1, 2):
        index = driver.find_element(
            By.XPATH,
            f'//*[@id="main-content-page"]/div[2]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[2]/div/div[3]/div[6]/ul/li[{i}]/div[1]/div[1]/div/div[2]/div[1]',
        )
        indexes.append(index.text)

    return indexes


def getPrices(rowCount: int) -> list:
    """Get market prices"""
    prices = []
    columnCount = len(
        driver.find_elements(
            By.XPATH,
            f'//*[@id="main-content-page"]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[2]/div[2]/div/div[3]/div[6]/div[1]/*',
        )
    )
    for i in range(1, rowCount + 1, 2):
        rowPrices = []
        for j in range(2, columnCount + 1):
            columnPrice = driver.find_element(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[2]/div/div[3]/div[6]/ul/li[{i}]/div[1]/div[{j}]',
            )
            if "\nFAV" in columnPrice.text:
                price = columnPrice.text
                rowPrices.append(price.removesuffix("\nFAV"))
            else:
                rowPrices.append(columnPrice.text)
        prices.append(rowPrices)

    return prices


def getRaceHeaderCount() -> int:
    """Returns number of races for a given track"""
    try:
        raceHeaderCount = len(
            driver.find_elements(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/div/div[2]/*',
            )
        )
    except Exception as e:
        print(e)
    else:
        return raceHeaderCount

    try:
        raceHeaderCount = len(
            driver.find_elements(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/div/*',
            )
        )
    except Exception as e:
        print(e)
        raise e
    else:
        return raceHeaderCount


if __name__ == "__main__":
    file = sys.argv[1]
    dayCheck = sys.argv[2]
    ogDF = csvToDF(csv=file)
    race = getRandomRaceWithTimeout(df=ogDF)
    raceName = race.index[0]

    driver = webdriver.Chrome()
    URL = "https://www.swiftbet.com.au/racing"
    driver.get(URL)

    time.sleep(10)

    if dayCheck == "tomorrow":
        # Tomorrow's webpage
        driver.find_element(
            By.XPATH,
            '//*[@id="main-content-page"]/div[2]/div[2]/div/div[2]/div/button[5]',
        ).click()
        time.sleep(10)

    driver.find_element(By.XPATH, f'//*[@title="{raceName}"]').click()

    numberRaceName = race.columns[0][0][5:]

    headerRaceCount = getRaceHeaderCount()

    if headerRaceCount >= 8:
        driver.find_element(
            By.XPATH,
            f'//*[@id="main-content-page"]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/div/div[2]/span[{numberRaceName}]',
        ).click()
    else:
        driver.find_element(
            By.XPATH,
            f'//*[@id="main-content-page"]/div[2]/div[3]/div[2]/div[1]/div/div/div[2]/div[1]/div/div[{numberRaceName}]',
        ).click()

    time.sleep(20)

    rowCount = len(
        driver.find_elements(
            By.XPATH,
            '//*[@id="main-content-page"]/div[2]/div[3]/div/div[1]/div/div/div[2]/div[2]/div[2]/div/div[3]/div[6]/ul/*',
        )
    )
    headers = getHeaders()
    index = getIndex(rowCount=rowCount)
    prices = getPrices(rowCount=rowCount)

    fileCreationTime = dt.now().strftime("%Y-%m-%d_%H%M%S")
    bets = pd.DataFrame(data=prices, index=index, columns=headers)

    if dayCheck == "tomorrow":
        bets.to_csv("data/staging_bets.csv")
        df_performed_bets = pd.read_csv("data/staging_bets.csv", header=0, index_col=0)
        df_performed_bets.dropna(inplace=True)
        df_performed_bets.to_csv(f"data/tomorrow_{raceName}_{fileCreationTime}.csv")
        os.remove("data/staging_bets.csv")
    else:
        bets.to_csv("data/staging_bets.csv")
        df_performed_bets = pd.read_csv("data/staging_bets.csv", header=0, index_col=0)
        df_performed_bets.dropna(inplace=True)
        df_performed_bets.to_csv(f"data/today{raceName}_{fileCreationTime}.csv")
        os.remove("data/staging_bets.csv")

    driver.quit()
