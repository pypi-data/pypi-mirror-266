import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import time
import argparse

def getLinks(field, number, page_number=1):
    article_urls = []
    while len(article_urls)<number:
        url = f"https://www.snopes.com/category/{field}/?pagenum={page_number}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        news_sections = soup.find_all("a",class_="outer_article_link_wrapper")
        for section in news_sections:
            try:
                article_urls.append(section['href'])
            except KeyError as e:
                print(repr(e))
        page_number+=1
    return article_urls[:number]


def getArticles(field, number=20, dropna= True | False):
    r"""GET Fake Articles
    :param field: section of the Articles, 'politics', 'Entertainment'
    :param dropna: Drop rows which contain missing values, True | False
    :return: None
    """
    if field not in ['politics', 'Entertainment']:
        print("Invalid field. Please provide one of the following sections: politics, Entertainment.")
        return
    
    print(f"crawling {field} articles ...")

    articles_url = getLinks(field, number)
    articles_df = pd.DataFrame({"url":articles_url})

    for i in range(number):
        response = requests.get(articles_df.iloc[i].url)
        article_page = BeautifulSoup(response.content, "html.parser")
        article_headline = article_page.find("h1")
        article_body = article_page.find(id="article-content")
        article_author = article_page.find("a", class_="author_link")
        article_publish_date = article_page.find("h3", class_="publish_date")       
        if None in [article_headline, article_body, article_author, article_publish_date] : 
            continue
        article_headline = article_headline.text.strip()
        article_content = ''.join([paragraph.text.strip() for paragraph in article_body.find_all("p")])
        article_author = article_author.text.strip()
        article_publish_date = article_publish_date.text.strip() 

        # Columns to check and insert if not present
        new_cols = ['article_headline', 'article_content', 'article_author', 'article_publish_date']

        # Insert columns if they don't exist
        for col in new_cols:
            if col not in articles_df.columns:
                articles_df[col] = None

        # Assign values to columns at row i
        articles_df.loc[i, 'article_headline'] = article_headline
        articles_df.loc[i, 'article_content'] = article_content
        articles_df.loc[i, 'article_author'] = article_author
        articles_df.loc[i, 'article_publish_date'] = article_publish_date.replace("Published ", "")

    if dropna: articles_df.dropna(how='any', inplace=True)
    if os.path.exists(f"articles_{field}.csv"):
        old_articles_df = pd.read_csv(f"articles_{field}.csv")
        articles_df = pd.concat([old_articles_df, articles_df], ignore_index=True)
    articles_df.drop_duplicates(inplace=True, ignore_index=True)
    articles_df.to_csv(f"articles_{field}.csv", index=False)
    print("done")


def from_fields(fields=[], number=10, timeout=6):
    r"""GET Fake Articles
    :param fields: sections of the Articles, culture', 'innovation', 'business', 'travel', 'future-planet'
    :param number: number of collected articles for each field
    :return: None
    """
    for field in fields: 
        getArticles(field=field, number=number)
        time.sleep(timeout)


def main():
    parser = argparse.ArgumentParser(description="FNews Fake article retrieval tool by Ahmed Bendrioua")
    parser.add_argument("field", help="Field/category of articles to retrieve")
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