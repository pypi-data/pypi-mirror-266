# **FNews** #

[![PyPI version](https://img.shields.io/pypi/v/FNews.svg)](https://pypi.org/project/FNews/)
<!-- [![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=XX272QZV9A2FN&source=url) -->

<!-- <img align="right" height="128px" width="128px" src="https://raw.githubusercontent.com/fhamborg/FNews/master/misc/logo/logo-256.png" /> -->

FNews is an open-source, easy-to-use Fake News crawler that extracts structured information from the Fake news websites for machine learning purposes. It can recursively follow internal hyperlinks and read RSS feeds to fetch the most recent fake articles. You only need to provide the desired field ('politics', 'Entertainment') of the fake news website to crawl it completely.

## Extracted information
FNews extracts the following attributes from Cnbc news articles.
* article headline
* article content (main text)
* article's author name
* publication date

## Features
* **works out of the box**: install with pip, add the desired field of your articles, run :-)
* run FNews conveniently using its [**CLI**](#run-the-crawler-via-the-cli) mode

### Modes and use cases
FNews supports two main use cases, which are explained in more detail in the following.

#### CLI mode
* stores extracted results in csv files in your own storage
* simple but extensive configuration (if you want to tweak the results)
* revisions: crawl fake articles multiple times and track changes

#### Library mode
* crawl and extract information given a list of fake article URLs
* to use FNews within your own Python code

## Getting started
It's super easy.

### Installation
```
$ pip3 install FNews
```

### Use within your own code (as a library)
You can access the core functionality of FNews, i.e. extraction of semi-structured information from one or more news articles, in your own code by using FNews in library mode.

```python
from FNews import getArticles

getArticles(field="politics", number=50, dropna=True)
```

If you want to crawl multiple fields at a time, optionally with a timeout in seconds and number of articles for each field
```python
NewsPlease.from_fields([field1, field2, ...], number=10, timeout=6)
```

### Run the crawler (via the CLI)

```
$ FNews-getArticles field [number] [dropna]
```

FNews will then start crawling a few fake articles and The results are stored by default in CSV file.

## License

Copyright 2023-2024 Ahmed Bendrioua