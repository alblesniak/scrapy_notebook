# -*- coding: utf-8 -*-
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy_app.items import WeekliesScraperItem

class NiedzielaSpider(Spider):
    name = 'niedziela'
    allowed_domains = ['niedziela.pl']
    start_urls = ['https://www.niedziela.pl/archiwum']

    def parse(self, response):
        self.logger.info('Parse function called parse on {}'.format(response.url))
        years = response.xpath('.//ul[@class="list-inline pt-main px-main text-center"]/li/a/@href')
        for year in years:
            yield response.follow(year, callback=self.parse_year)

    def parse_year(self, response):
        self.logger.info('Parse function called parse_year on {}'.format(response.url))
        issues = response.xpath('.//div[@class="row px-main"]/div/a/@href')
        for issue in issues:
            yield response.follow(issue, callback=self.parse_issue)

    def parse_issue(self, response):
        self.logger.info('Parse function called parse_issue on {}'.format(response.url))
        issue_number = response.xpath('.//h1[@class="title-page text-center mb-main"]/text()').re_first(r"\d{1,2}/\d{4}").split('/')
        issue_dict = {
            'issue_name' : 'niedziela',
            'issue_number' : f'{issue_number[0].zfill(2)}/{issue_number[1]}',
            'issue_url' : response.url,
            'issue_cover_url' : response.xpath('.//img[@class="img-fluid center-block border-solid"]/@src').get()
        }
        sections = response.xpath('.//div[@class="row border-dotted-left border-dotted-right mb-main magazine-big-hor mt-2x"]')
        for section in sections:
            issue_dict['section_name'] = section.xpath('.//p[@class="label-index"]/text()').get()
            articles = section.xpath('.//a/@href')
            for article in articles:
                yield response.follow(article, callback=self.parse_article, meta=issue_dict)

    def parse_article(self, response):
        self.logger.info('Parse function called parse_article on {}'.format(response.url))
        if not response.xpath('//div[@class="row my-2x label-color"]//p[@class="py-half px-main" and contains(text(),"Pełna treść tego i pozostałych artykułów")]'):
            loader = ItemLoader(item=WeekliesScraperItem(), response=response)
            loader.add_value('issue_name', response.meta['issue_name'])
            loader.add_value('issue_number', response.meta['issue_number'])
            loader.add_value('issue_url', response.meta['issue_url'])
            loader.add_value('issue_cover_url', response.meta['issue_cover_url'])
            loader.add_value('section_name', response.meta['section_name'])
            loader.add_value('article_url', response.url)
            loader.add_xpath('article_title', '//h1')
            loader.add_xpath('article_intro', '//article[@class="article"]/preceding::p[@class="article-lead font-weight-bold text-center mx-main mb-main"]')
            loader.add_xpath('article_content', '//article[@class="article"]//p[contains(@class,"") and not(contains(@class, "reklama")) and not(contains(text(), "Reklama") and contains(@class, "text-center")) and not(contains(@class, "nota"))]')
            loader.add_xpath('article_authors', './/article[@class="article"]/preceding::h3[contains(@class, "article-author")]')
            yield loader.load_item()