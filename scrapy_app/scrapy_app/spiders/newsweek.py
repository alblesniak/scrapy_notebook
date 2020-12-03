# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.loader import ItemLoader
from urllib.parse import urljoin
from scrapy_app.items import WeekliesScraperItem
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import re
import os


class NewsweekSpider(Spider):
    name = 'newsweek'
    allowed_domains = ['newsweek.pl']
    start_urls = ['https://konto.newsweek.pl/auth.html?state=%2Farchiwum-wydan&client_id=www.newsweek.pl.okonto.front.onetapi.pl&redirect_uri=https%3A%2F%2Fwww.newsweek.pl%2Fokonto%2Fauth']

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.username = os.environ['NEWSWEEK_LOGIN']
        self.password = os.environ['NEWSWEEK_PASSWORD']

    def parse(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        self.driver.get(response.url)
        username_element = self.driver.find_element_by_id('f_login')
        self.driver.execute_script("document.getElementById('f_login').click()")
        self.driver.execute_script("arguments[0].setAttribute('value', '" + self.username +"')", username_element)
        password_element = self.driver.find_element_by_id('f_password')
        self.driver.execute_script("document.getElementById('f_password').click()")
        self.driver.execute_script("arguments[0].setAttribute('value', '" + self.password +"')", password_element)
        self.driver.execute_script("arguments[0].click();", password_element)
        button_element = self.driver.find_element_by_xpath('//input[@class="loginButton"]')
        self.driver.execute_script("arguments[0].click();", button_element)
        root = html.fromstring(self.driver.page_source)
        issues = root.xpath('.//div[@id="pageMap"]//li/a/@href')
        for issue in issues:
            issue_url = urljoin('https://www.newsweek.pl/', issue)
            yield response.follow(issue_url, callback=self.parse_issue)

    def parse_issue(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        self.driver.get(response.url)
        root = html.fromstring(self.driver.page_source)
        issue_title = str(root.xpath('.//div[@class="categoryTitleBox"]/h1/text()'))
        issue_number = re.search(r"\d{1,2}/\d{4}", issue_title).group(0).split('/')
        issue_name = re.search(r"([^0-9/]*)", issue_title).group(0).lower().replace(' ', '_').lstrip("['").rstrip('_')
        if issue_name == 'wydanie_amerykańskie':
            issue_name = 'newsweek_wydanie_amerykanskie'
        elif issue_name == 'smart_travelling':
            issue_name = 'newsweek_smart_traveling'
        issue_dict = {
            'issue_name'  : issue_name,
            'issue_number' : f'{issue_number[0].zfill(2)}/{issue_number[1]}',
            'issue_url' : response.url,
            'issue_cover_url' : None
        }
        articles = root.xpath('.//div[@class="pure-u-1-1 pure-u-md-1-4 smallItem"]/a/@href')
        for article in articles:
            article_url = urljoin('https://www.newsweek.pl/', article)
            yield response.follow(article_url, callback=self.parse_article, meta=issue_dict)

    def parse_article(self, response):
        self.logger.info('Parse function called parse_article on {}'.format(response.url))
        try:
            section_name = " - ".join([s_name.strip().lower() for s_name in response.xpath('.//ul[@class="breadCrumb"]/li/a/span/text()').getall() if s_name != 'Newsweek'])
        except:
            section_name = None
        article_title = str(response.xpath('.//article/h1/text()').get()).replace('Opinia\n\t\t\n\t\n', '')
        keywords_script = str(response.xpath('.//script[contains(text(),"keywords")]/text()').getall())
        keywords = [re.sub('[\s\"\n]', '', kw).strip('''\\n''').strip('''\\''') for kw in re.search('\"keywords\":\s\[\s*(.*?)\s*\]', keywords_script, re.DOTALL).group(1).split(',')]
        loader = ItemLoader(item=WeekliesScraperItem(), response=response)
        loader.add_value('issue_name', response.meta['issue_name'])
        loader.add_value('issue_number', response.meta['issue_number'])
        loader.add_value('issue_url', response.meta['issue_url'])
        loader.add_value('section_name', section_name)
        loader.add_value('article_url', response.url)
        loader.add_value('article_tags', keywords)
        loader.add_value('article_title', article_title)
        loader.add_xpath('article_authors', './/h4[@class="name"]')
        loader.add_xpath('article_intro', './/article//p[@class="lead"]')
        loader.add_xpath('article_content', './/div[contains(@class, "articleDetail")]/descendant::*[self::h3 or self::p]')
        yield loader.load_item()