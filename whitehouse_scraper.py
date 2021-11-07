#!/usr/bin/env python3
import csv
import os
import requests
from bs4 import BeautifulSoup
from pathlib import Path


def sanitize_str(s: str):
    return s.strip().replace(u'\xa0', u' ').replace('\n', ' ')


def get_page_soup(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
    }
    page = requests.get(url, headers=headers).content
    return BeautifulSoup(page, "html.parser")


def get_article_urls(url):
    soup = get_page_soup(url)
    articles_urls = soup.find('div', {'class': 'article-wrapper'}).findChildren('a', {'class': 'news-item__title'})
    articles_urls = [e['href'] for e in articles_urls]
    return articles_urls


def crawl_article(url):
    try:
        soup = get_page_soup(url)
        title = sanitize_str(soup.find('h1', {'class': 'page-title'}).text)  # [title, date, tag, body, url]
        print(title)
        date = sanitize_str(soup.find('time', {'class': 'posted-on'}).text)
        tag = sanitize_str(soup.find('a', {'rel': 'category'}).text)
        body = sanitize_str(soup.find('section', {'class': 'body-content'}).text)
        result = [title, date, tag, body, url]
    except Exception:
        print(Exception)
        print(url)
    save_to_csv(result)


def save_to_csv(result):
    filename = result[0].replace(' ', '_')+'.csv'
    filepath = os.path.join('wh_out', filename)
    with open(filepath, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['title', 'date', 'tag', 'body', 'url'])
        writer.writerow(result)


def crawl_page(url):
    article_urls = get_article_urls(url)
    for url in article_urls:
        crawl_article(url)


def main(start=1, end=2):
    Path('wh_out').mkdir(parents=True, exist_ok=True)
    for i in range(start, end + 1):
        print(f'\nCrawling page {i}\n')
        url = f'https://www.whitehouse.gov/briefing-room/page/{i}/'
        crawl_page(url)


if __name__ == '__main__':
    # specify which pages to crawl, start and end are inclusive
    main(end=3)
