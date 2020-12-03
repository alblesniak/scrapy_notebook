# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.loader import ItemLoader
from urllib.parse import urljoin
from scrapy_app.items import WeekliesScraperItem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from lxml import html
from time import sleep
import time
import re
import os

class PolitykaSpider(Spider):
    name = 'polityka'
    allowed_domains = ['polityka.pl']
    start_urls = ['https://polityka.pl/logowanie?loginSuccessUrl=https%3A%2F%2Fwww.polityka.pl%2Farchiwumpolityki%253F_spring_security_remember_me%253Dtrue']

    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument('--window-size=1420,1080')
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.username = os.environ['POLITYKA_LOGIN']
        self.password = os.environ['POLITYKA_PASSWORD']

    def parse(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        self.driver.get(response.url)
        username_element = self.driver.find_element_by_id('repeat')
        self.driver.execute_script("document.getElementById('repeat').click()")
        self.driver.execute_script("arguments[0].setAttribute('value', '" + self.username +"')", username_element)
        password_element = self.driver.find_element_by_id('password')
        self.driver.execute_script("document.getElementById('password').click()")
        self.driver.execute_script("arguments[0].setAttribute('value', '" + self.password +"')", password_element)
        self.driver.execute_script("arguments[0].click();", password_element)
        button_element = self.driver.find_element_by_xpath('//input[@class="btn btn-sm btn-primary"]')
        self.driver.execute_script("arguments[0].click();", button_element)
        root = html.fromstring(self.driver.page_source)
        issues = root.xpath('.//div[@class="cg_toc_covers_list_wrapper"]/ul/li/a/@href')
        for issue in issues:
            yield response.follow(issue, callback=self.parse_issue)

    def parse_issue(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        self.driver.get(response.url)
        root = html.fromstring(self.driver.page_source)
        issue_number = str(root.xpath('//div[@class="cg_toc_issue"]/text()')[0]).split('.')
        issue_dict = {
            'issue_name' : 'polityka',
            'issue_number' : f'{issue_number[0].zfill(2)}/{issue_number[1]}',
            'issue_url' : response.url,
            'issue_cover_url' : root.xpath('.//div[@class="cg_toc_cover"]/img/@src')[0].replace('//', 'https://')
        }
        articles = root.xpath('.//section[@class="cg_toc"]//a[not(contains(@class, "cg_toc_previous_link"))]/@href')
        for article in articles:
            sleep(0.25)
            yield response.follow(article, callback=self.parse_article, meta=issue_dict)
            
    def parse_article(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        self.driver.get(response.url)
        root = html.fromstring(self.driver.page_source)
        loader = ItemLoader(item=WeekliesScraperItem(), response=response)
        loader.add_value('issue_name', response.meta['issue_name'])
        loader.add_value('issue_number', response.meta['issue_number'])
        loader.add_value('issue_url', response.meta['issue_url'])
        loader.add_value('issue_cover_url', response.meta['issue_cover_url'])
        loader.add_value('section_name', root.xpath('.//div[@class="cg_article_section"]/a/text()'))
        loader.add_value('article_url', response.url)
        loader.add_value('article_title', root.xpath('.//h1[@class="cg_article_internet_title"]/text()'))
        loader.add_value('article_authors', root.xpath('.//div[@class="cg_article_author_name"]/text()'))
        loader.add_value('article_intro', root.xpath('.//div[@class="cg_article_lead"]//text()')[0])
        loader.add_value('article_content', root.xpath('.//div[@class="cg_article_meat"]//text()'))
        yield loader.load_item()