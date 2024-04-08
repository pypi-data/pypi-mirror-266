import re
import requests 
import pandas as pd
from bs4 import BeautifulSoup
import time
import os
import argparse
import datetime


def getLinks(field, number):
    article_urls = []
    url = f"https://www.bbc.com/{field}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    news_sections = soup.find_all("a", class_="sc-4befc967-1 gzOvMy")
    for section in news_sections:
        try:
            if 'news' in section['href'] and section['href'][len(section['href'])-1].isnumeric() : article_urls.append("https://www.bbc.com" + section['href'] + ".json")
        except KeyError as e:
            print(repr(e))
    return article_urls[:number]


def getArticles(field, number=20, dropna=True | False):
    r"""GET the Article from BBC
    :param field: section of the Articles,'news', 'innovation', 'business', 'culture', 'travel'
    :param dropna: Drop rows which contain missing values, True | False
    :return: None
    """
    if field not in ['news', 'innovation', 'business', 'culture', 'travel']:
        print("Invalid field. Please provide one of the following sections: 'technology', 'politics', 'tv', 'business', 'markets', 'investing'.")
        return
    
    print(f"crawling {field} articles ...")
    articles_url = getLinks(field, number)
    articles_df = pd.DataFrame({"url":articles_url})

    for i in range(number):
        print(articles_url[i])
        article_json = requests.get(articles_url[i]).json()

        if article_json["content"] == None:
            continue
        try:
            article_headline = article_json["promo"]["headlines"]["headline"]
            article_all_authors = article_json["promo"]["byline"]["name"]
            article_bbc_author = article_json["promo"]["byline"]["persons"][0]["name"]
            article_summary = article_json["promo"]["summary"]
            article_language = article_json["promo"]["passport"]["language"]
            article_body = " ".join([re.sub(r'&.*;','',re.sub('<.*>',"",paragraph.get("text"))) for paragraph in article_json["content"]["blocks"] if "text" in paragraph.keys()])
            article_publish_date = datetime.datetime.fromtimestamp(article_json['metadata']['firstPublished']/1000).strftime('%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(repr(e))
        cols = ['article_headline', 'article_body', 'article_all_authors', 'article_bbc_author', 'article_summary', 'article_language', 'article_publish_date']
        for col in cols:
            if col not in articles_df.columns:
                articles_df[col] = None

        articles_df.loc[i, 'article_headline'] = article_headline
        articles_df.loc[i, 'article_all_authors'] = article_all_authors
        articles_df.loc[i, 'article_bbc_author'] = article_bbc_author
        articles_df.loc[i, 'article_summary'] = article_summary
        articles_df.loc[i, 'article_language'] = article_language
        articles_df.loc[i, 'article_body'] = article_body
        articles_df.loc[i, 'article_publish_date'] = article_publish_date
    
        time.sleep(5)

    if dropna: articles_df.dropna(how="any", inplace=True)
    if os.path.exists(f"articles_{field}.csv"):
        old_articles_df = pd.read_csv(f"articles_{field}.csv")
        articles_df = pd.concat([old_articles_df, articles_df], ignore_index=True)
    articles_df.drop_duplicates(inplace=True, ignore_index=True)
    articles_df.to_csv(f"articles_{field}.csv", index=False)
    print("done")

def from_fields(fields=[], number=10, timeout=6):
    r"""GET the Article from BBC
    :param fields: sections of the Articles, 'innovation', 'business', 'culture', 'travel'
    :param number: number of collected articles for each field
    :return: None
    """
    for field in fields:
        getArticles(field, number)
        time.sleep(timeout)


def main():
    parser = argparse.ArgumentParser(description="BbcNews BBC article retrieval tool by Ahmed Bendrioua")
    parser.add_argument("field", help="Field/category of articles to retrieve from BBC  ")
    parser.add_argument("--number", "-n", type=int, help="Number of articles to retrieve")
    parser.add_argument("--dropna", "-d", action="store_true", help="Drop rows with missing values")

    args = parser.parse_args()

    field = args.field
    number = args.number
    dropna = args.dropna

    if number is not None and dropna is not None:
        getArticles(field, number, dropna)
    elif number is not None:
        getArticles(field, number)
    else:
        getArticles(field)

if __name__ == "__main__":
    main()

