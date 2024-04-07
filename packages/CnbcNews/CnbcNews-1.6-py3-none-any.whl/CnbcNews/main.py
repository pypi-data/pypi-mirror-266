import pandas as pd
from bs4 import BeautifulSoup
import requests
import csv
import os

def getLinks(field, number, article_urls=[], page_number=1):
    if len(article_urls)>=number: return article_urls
    url = f"https://www.cnbc.com/{field}/?page={page_number}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    news_sections = soup.find_all("a",class_="Card-title")
    for section in news_sections:
        try:
            article_urls.append(section['href'])
        except Exception as e:
            print(repr(e))
    page_number+=1
    return getLinks(field=field, number=number, article_urls=article_urls, page_number=page_number)


def getArticles(field, number=20, dropna= True | False):
    r"""GET the Article from Cnbc
    :param field: section of the Articles, 'technology', 'politics', 'tv', 'business', 'markets', 'investing'
    :param dropna: Drop rows which contain missing values, True | False
    :return: None
    """
    if field not in ['technology', 'politics', 'tv', 'business', 'markets', 'investing']:
        print("Invalid field. Please provide one of the following sections: 'technology', 'politics', 'tv', 'business', 'markets', 'investing'.")
        return

    articles_url = getLinks(field, number)
    articles_df = pd.DataFrame({"url":articles_url})
    le = len(articles_df)
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
        old_articles_df = pd.read_csv(f"articles_{field}.csv").drop(columns=['id'])
        articles_df = pd.concat([old_articles_df, articles_df], ignore_index=True)
    articles_df.drop_duplicates(inplace=True, ignore_index=True)
    articles_df.to_csv(f"articles_{field}.csv", index_label="id")


def main():
    import sys
    if len(sys.argv)==4:
        getArticles(sys.argv[1], sys.argv[2], sys.argv[3])
    elif len(sys.argv)==3:
        getArticles(sys.argv[1], sys.argv[2])
    elif len(sys.argv)==2:
        getArticles(sys.argv[1])
    else:
        print("please provide the field ! exemple : CnbcNews-getArticles technology")

if __name__ == "__main__":
    main()