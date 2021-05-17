import requests
import re
from bs4 import BeautifulSoup
import os


class Scrapper:

    def __init__(self, url):
        self.url = url
        self.articles_info = dict()
        self.saved_articles = dict()

    @staticmethod
    def request_url(url, page):
        response = requests.get(url, params={'page': page})
        if response.status_code != 200:
            print(f'The URL returned {response.status_code}!')
        else:
            return response.content

    @staticmethod
    def get_title(title):
        pattern = re.compile(r'\w+')
        return '_'.join(pattern.findall(title))

    def save_articles(self, n_pages):
        dirs = os.listdir()
        for n in range(1, n_pages + 1):
            dir_name = 'Page_' + str(n)
            if dir_name not in dirs:
                os.mkdir(dir_name)
        for page, p_info in self.saved_articles.items():
            for a in p_info:
                p_name = a[0] + '.txt'
                path = os.path.join(page, p_name)
                with open(path, 'wb') as f:
                    f.write(a[1])

    def get_articles_list(self, page, ptype):
        p_links = []
        content = self.request_url(self.url, page)
        if content is not None:
            soup = BeautifulSoup(content, 'html.parser')
            articles = soup.find_all('article')
            articles_type = [art for art in articles
                             if art.find('span', {'data-test': 'article.type'}).text.strip() == ptype]
            for art in articles_type:
                a = art.find('a', {'class': 'c-card__link u-link-inherit'}, href=True)
                p_links.append((self.get_title(a.text), a['href']))
            self.articles_info[page] = p_links

    def get_articles_content(self):
        for page, p_info in self.articles_info.items():
            dir_name = 'Page_' + page
            p_content = []
            for t, url in p_info:
                a_url = 'https://www.nature.com' + url
                content = self.request_url(a_url, page)
                if content is not None:
                    soup = BeautifulSoup(content, 'html.parser')
                    article = soup.find('div', {'class': 'article__body'})
                    if article is None:
                        article = soup.find('div', {'class': 'article-item__body'})
                    p_content.append((t, bytes(article.text, 'utf-8')))
                else:
                    print('Cannot download article content')
            self.saved_articles[dir_name] = p_content

    def run(self):
        n_pages = int(input())
        ptype = input()
        for p in range(1, n_pages + 1):
            p = str(p)
            self.get_articles_list(p, ptype)
        self.get_articles_content()
        self.save_articles(n_pages)


scr = Scrapper('https://www.nature.com/nature/articles')
scr.run()
