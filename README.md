# GYK scraper

This code scrapes data from [gyakorikerdesek.hu](https://www.gyakorikerdesek.hu). The data is not too complex, but complex enough to make sense to load into an sqlite database. 

Currently the code works as it is. However there are things to improve.... the crawling is not automated, a fixed category and a fixed page range is fetched. 

## Usage

```bash
python gyik_scraper.py --database <str> \
            --category <str> \
            --startpage <int> \
            --endpage <int>
```

### where

* **database**: mandatory option, sqlite database file. If not exists, the script creates.
* **category**: mandatory option. Main GyIK category (eg. `tudomanyok`).
* **startpage**: optional. First page of questions to load. Default: 0.
* **lastpage**: optional. The last page of questions to load. Default: last page of questions.

The start page has to be lower then last page. To retrieve all questions for a category these paremeters needs to be omitted.

### SQLite schema

![db schema](db_tools/schema.png)

## TODO

* Clean up the code: the naming of the functions are not intuitive.
* Bit restructure the functions.
* Adding comments.
* Adding tests.
* Integrate Codacy, Travis for code quality measure.

