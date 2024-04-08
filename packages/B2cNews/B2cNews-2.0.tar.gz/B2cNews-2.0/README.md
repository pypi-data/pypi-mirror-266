# **B2cNews** #

[![PyPI version](https://img.shields.io/pypi/v/B2cNews.svg)](https://pypi.org/project/B2cNews/)

B2cNews is an open-source, easy-to-use news crawler that extracts structured information from the Bbc news website for machine learning purposes. It can recursively follow internal hyperlinks and read RSS feeds to fetch the most recent articles in any given field. You only need to provide the desired field ('news', 'innovation', 'business', 'culture', 'travel', etc.) of the news website to crawl it completely.

## Extracted information
B2cNews extracts the following attributes from Bbc news articles.
* Article Headline
* Article Authors
* BBC Author
* Article Body
* Article Summary
* Article Publish Date
* Article Language

## Features
* **works out of the box**: install with pip, add the desired field of your articles, run :-)
* run B2cNews conveniently using its [**CLI**](#run-the-crawler-via-the-cli) mode

### Modes and use cases
B2cNews supports two main use cases, which are explained in more detail in the following.

#### CLI mode
* stores extracted results in csv files in your own storage
* simple but extensive configuration (if you want to tweak the results)
* revisions: crawl articles multiple times and track changes

#### Library mode
* crawl and extract information given a list of article URLs
* to use B2cNews within your own Python code

## Getting started
It's super easy.

### Installation
```
$ pip3 install B2cNews
```

### Use within your own code (as a library)
You can access the core functionality of B2cNews, i.e. extraction of semi-structured information from one or more news articles, in your own code by using B2cNews in library mode.

```python
from B2cNews import getArticles

getArticles(field="culture", number=50, dropna=True)
```

If you want to crawl multiple fields at a time, optionally with a timeout in seconds and number of articles for each field
```python
B2cNews.from_fields([field1, field2, ...], number=10, timeout=6)
```

### Run the crawler (via the CLI)

```
$ B2cNews-getArticles field [number] [dropna]
```

B2cNews will then start crawling a few articles and The results are stored by default in CSV file.

## License

Copyright 2023-2024 Ahmed Bendrioua