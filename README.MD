# **SWIFTBET WEBSCRAPER AND BOT**

Welcome to my swiftbet webscraper and bot.
The URL used is https://www.swiftbet.com.au/racing.


The first script will scrape track names, race numbers, race URLs and approximate race times for today or tomorrow's races.
The second script navigates to a randomly selected race (a race that has not yet finished) and scrapes current market prices for horses in the race.

The data scraped from both scripts is stored as a CSV.
As part of this repo, a `data/` directory has already been set up to store any data downloaded from the scripts.

You must download Google Chrome to run these scripts.
You will find other technical dependencies in `requirements.txt`.

## Example execution commands

Use the CLI to run these scripts.
Here are some example commands.

For `data_scraper.py`:

- `python3 ./src/data_scraper.py today`

- `python3 ./src/data_scraper.py tomorrow`

For `bot.py`:

- `python3 ./src/bot.py data/today_races_data2024-06-30_170326.csv today`

- `python3 ./src/bot.py data/tomorrow_races_data2024-06-30_170458.csv tomorrow`

## Considerations

Given that these are Australian markets, I recommend running these scripts first thing in the morning to make the most of any opportunities.

If the Swiftbet website undergoes significant design changes, these scripts will need to be updated, so please keep this in mind.

A key step in the next stage of development is handling `StaleElement` exceptions.
These rarely occur currently. If they do, you'll need to rerun the script and it will run successfully.
Unfortunately, I ran out of time to redesign the script to handle them but will resolve this in the next version.
The solution I have in mind is replacing `time.sleep()` with explicit waits to ensure the element is available for interaction.

**HAPPY WEBSCRAPING**


