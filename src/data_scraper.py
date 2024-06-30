"""
Scrapes track names, race numbers, race URLs and race time
from Swiftbet Australia for today and tomorrow.
"""
import re
import sys
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime as dt
from datetime import timedelta


def parseTimeString(timeStr: str) -> int:
    """Converts time string into integer (seconds)"""
    totalSeconds = 0
    parts = re.findall(r"(-?\d+)([dhms])", timeStr)
    for value, unit in parts:
        value = int(value)
        if unit == "d":
            totalSeconds += value * 86400
        elif unit == "h":
            totalSeconds += value * 3600
        elif unit == "m":
            totalSeconds += value * 60
        elif unit == "s":
            totalSeconds += value
    return totalSeconds


def calculateRaceTime(timeLeft: int) -> str:
    """Returns actual race time in format"""
    secondsLeft = parseTimeString(timeLeft)
    now = dt.now()
    raceTime = now + timedelta(seconds=secondsLeft)
    return raceTime.strftime("%H:%M:%S %Y-%m-%d")


def getElementCount(xpath='//*[@id="main-content-page"]/div[2]/div[4]/div/*') -> int:
    """Get number of elements in part of webpage"""
    return len(driver.find_elements(By.XPATH, xpath))


def getAllCellValues(tableCount: int) -> dict:
    """Get race times and race links"""
    allCellValues = []
    for i in range(1, tableCount + 1):
        rowCount = len(
            driver.find_elements(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[2]/*',
            )
        )
        for j in range(1, rowCount + 1):
            rowCellValues = []
            cellsCount = len(
                driver.find_elements(
                    By.XPATH,
                    f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[2]/div[{j}]/*',
                )
            )
            for k in range(1, cellsCount + 1):
                cellText = driver.find_element(
                    By.XPATH,
                    f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[2]/div[{j}]/div[{k}]',
                )
                if cellText.text:
                    if cellText.text == "CLOSED":
                        rowCellValues.append("")
                    elif cellText.text == "ABANDONED":
                        rowCellValues.append("")
                    elif "/" in cellText.text:
                        rowCellValues.append("")
                    else:
                        raceTime = calculateRaceTime(cellText.text)
                        rowCellValues.append(raceTime)
                else:
                    rowCellValues.append("")
                cellLinkCount = len(
                    driver.find_elements(
                        By.XPATH,
                        f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[2]/div[{j}]/div[{k}]/*',
                    )
                )
                if cellLinkCount > 0:
                    cellLink = driver.find_element(
                        By.XPATH,
                        f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[2]/div[{j}]/div[{k}]/a',
                    )
                    rowCellValues.append(cellLink.get_attribute("href"))
                else:
                    rowCellValues.append("")

            allCellValues.append(rowCellValues)
            continue

    return allCellValues


def getTrackNames(tableCount: int) -> list:
    """Gets track names"""
    trackNames = []
    for i in range(1, tableCount + 1):
        rowCount = len(
            driver.find_elements(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[1]/div/div[2]/div/*',
            )
        )
        for j in range(1, rowCount + 1):
            trackName = driver.find_element(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[1]/div/div[2]/div/div[{j}]/div/a',
            )
            trackNames.append(trackName.text)

    return trackNames


def getRaceName(tableCount: int) -> dict:
    """Get race names"""
    raceNames = {}
    for i in range(1, tableCount + 1):
        tableRaceNames = []
        raceCategory = driver.find_element(
            By.XPATH,
            f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[1]/div/div[1]/span[1]',
        )
        columnCount = len(
            driver.find_elements(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[1]/span/div/*',
            )
        )
        for j in range(1, columnCount + 1):
            raceName = driver.find_element(
                By.XPATH,
                f'//*[@id="main-content-page"]/div[2]/div[4]/div/div[{i}]/div[2]/div/div/div/div/div[1]/span/div/div[{j}]',
            )
            tableRaceNames.append(raceName.text)
        raceNames[raceCategory.text] = tableRaceNames

    return raceNames


def createDF(raceNames: dict, raceData: list, trackNames: list) -> pd.DataFrame:
    """Creates DataFrame from scraped data"""
    cols = max([value for value in raceNames.values()], key=len)
    raceInfo = ["Time", "Link"]
    newCols = pd.MultiIndex.from_product([cols, raceInfo])
    df = pd.DataFrame(data=raceData, index=trackNames, columns=newCols)

    return df


if __name__ == "__main__":
    driver = webdriver.Chrome()
    URL = "https://www.swiftbet.com.au/racing"
    driver.get(URL)
    dayCheck = sys.argv[1]

    time.sleep(20)

    if dayCheck == "tomorrow":
        # Getting tomorrow's data
        driver.find_element(
            By.XPATH,
            '//*[@id="main-content-page"]/div[2]/div[2]/div/div[2]/div/button[5]',
        ).click()
        time.sleep(20)

    RaceTableCount = getElementCount()
    TrackNames = getTrackNames(tableCount=RaceTableCount)
    RaceNames = getRaceName(tableCount=RaceTableCount)
    RaceData = getAllCellValues(tableCount=RaceTableCount)
    fileCreationTime = dt.now().strftime("%Y-%m-%d_%H%M%S")
    df_races_data = createDF(
        raceNames=RaceNames, raceData=RaceData, trackNames=TrackNames
    )

    if dayCheck == "tomorrow":
        df_races_data.to_csv(
            f"data/tomorrow_races_data{fileCreationTime}.csv", header=True, index=True
        )
    else:
        df_races_data.to_csv(
            f"data/today_races_data{fileCreationTime}.csv", header=True, index=True
        )

    driver.quit()
