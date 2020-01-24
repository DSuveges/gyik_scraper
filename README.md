# GYK scraper

This code scrapes data from [gyakorikerdesek.hu](https://www.gyakorikerdesek.hu). The data is not too complex, but complex enough to make sense to load into an sqlite database. 

Currently the code works as it is. However there are things to improve.... the crawling is not automated, a fixed category and a fixed page range is fetched. 

## TODO

* Clean up the code: the naming of the functions are not intuitive.
* Bit restructure the functions.
* Adding comments.
* Adding tests.
* Integrate Codacy, Travis for code quality measure.