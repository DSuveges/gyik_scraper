# GYK scraper

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b18d92473e344f929baa2fc3051d0520)](https://app.codacy.com/manual/DSuveges/gyik_scraper?utm_source=github.com&utm_medium=referral&utm_content=DSuveges/gyik_scraper&utm_campaign=Badge_Grade_Dashboard)

This code scrapes data from [gyakorikerdesek.hu](https://www.gyakorikerdesek.hu). The data is not too complex, but complex enough to make sense to load into an sqlite database. The loaded data then can be used to do some analytics.

Finally the code is getting into shape. User can decide to fetch all questions for a category, a range of a category by defining a start and end page or fetching a single question based on a provided URL.

## Usage

```bash
python gyik_scraper.py --database <str> \
            --category <str> \
            --subCategory <str> \
            --startPage <int> \
            --endPage <int> \
            --directQuestion <str> \
            --logFile <str>
```

### where

* **database**: mandatory option, sqlite database file. If not exists, the script creates.
* **category**: mandatory option. Main GyIK category (eg. `tudomanyok`).
* **subCategory**: optionally the subcategory within the category can be specified to narow down the scope.
* **startPage**: optional. First page of questions to load. Default: 1.
* **lastpage**: optional. The last page of questions to load. Default: last page of questions.
* **directQuestion**: optional. If present only this question will be downloaded. Mostly for testing purposes.
* **logFile**: optional filename for the logs. Default filename: scraper.log

The start page has to be lower then last page. To retrieve all questions for a category these paremeters needs to be omitted.

### SQLite schema

![db schema](db_tools/schema.png)


