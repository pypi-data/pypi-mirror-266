import pandas as pd
from bs4 import BeautifulSoup
import requests
import argparse
import os
import time

def getLinks(field, number, page_number=1):
    article_urls = []
    while len(article_urls) < number:
        url = f"https://www.cnbc.com/{field}/?page={page_number}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        news_sections = soup.find_all("a", class_="Card-title")
        for section in news_sections:
            try:
                article_urls.append(section['href'])
            except KeyError as e:
                print(repr(e))
        page_number += 1
    return article_urls[:number]


def getArticles(field, number=20, dropna= True | False):
    r"""GET the Article from Cnbc
    :param field: section of the Articles, 'technology', 'politics', 'tv', 'business', 'markets', 'investing'
    :param dropna: Drop rows which contain missing values, True | False
    :return: None
    """
    if field not in ['technology', 'politics', 'tv', 'business', 'markets', 'investing']:
        print("Invalid field. Please provide one of the following sections: 'technology', 'politics', 'tv', 'business', 'markets', 'investing'.")
        return
    
    print(f"crawling {field} articles ...")
    articles_url = getLinks(field, number)
    articles_df = pd.DataFrame({"url":articles_url})
    
    for i in range(number):
        response = requests.get(articles_df.iloc[i].url)
        article_page = BeautifulSoup(response.content, "html.parser")
        article_headline = article_page.find("h1", class_="ArticleHeader-headline")
        article_body = article_page.find("div", class_="ArticleBody-articleBody")
        article_author = article_page.find("a", class_="Author-authorName")
        article_header = article_page.find(id="main-article-header")
        article_label = article_page.find("a", class_="ArticleHeader-eyebrow")
        if None in [article_headline, article_body, article_author, article_header, article_label] : 
            continue

        article_headline = article_headline.text.strip()
        article_body=""
        article_p_groups = article_page.find_all("div", class_="group")
        for group in article_p_groups:
            for paragraph in group.find_all("p"):
                article_body+=paragraph.text.strip()
        article_author = article_author.text.strip()
        article_header = article_page.find(id="main-article-header")
        article_publish_time = article_header.find("time")['datetime']
        article_label = article_label.text.strip()
        # Columns to check and insert if not present
        new_cols = ['article_headline', 'article_body', 'article_author', 'article_publish_time', 'article_label']
        # Insert columns if they don't exist
        for col in new_cols:
            if col not in articles_df.columns:
                articles_df[col] = None
        # Assign values to columns at row i
        articles_df.loc[i, 'article_headline'] = article_headline
        articles_df.loc[i, 'article_body'] = article_body
        articles_df.loc[i, 'article_author'] = article_author
        articles_df.loc[i, 'article_publish_time'] = article_publish_time
        articles_df.loc[i, 'article_label'] = article_label

    if dropna: articles_df.dropna(how='any', inplace=True)
    if os.path.exists(f"articles_{field}.csv"):
        old_articles_df = pd.read_csv(f"articles_{field}.csv")
        articles_df = pd.concat([old_articles_df, articles_df], ignore_index=True)
    articles_df.drop_duplicates(inplace=True, ignore_index=True)
    articles_df.to_csv(f"articles_{field}.csv", index=False)
    print("done")


def from_fields(fields=[], number=10, timeout=6):
    r"""GET the Article from Cnbc
    :param fields: sections of the Articles, 'technology', 'politics', 'tv', 'business', 'markets', 'investing'
    :param number: number of collected articles for each field
    :return: None
    """
    for field in fields: 
        getArticles(field=field, number=number)
        time.sleep(timeout)


def main():
    parser = argparse.ArgumentParser(description="CnbcNews Cnbc article retrieval tool by Ahmed Bendrioua")
    parser.add_argument("field", help="Field/category of articles to retrieve from CNBC")
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