# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.loader import ItemLoader
from urllib.parse import urljoin
from scrapy_app.items import WeekliesScraperItem


class PrzewodnikKatolickiSpider(scrapy.Spider):
	name = 'przewodnik_katolicki'
	allowed_domains = ['przewodnik-katolicki.pl']
	start_urls = ['https://www.przewodnik-katolicki.pl/Archiwum?rok=wszystkie']

	def parse(self, response):
		self.logger.info('Parse function called on {}'.format(response.url))
		issues = response.xpath("//ul[@class='lista-artykulow']/li")
		for issue in issues:
			# check if this periodical is regular issue
			issue_name_number = issue.xpath('.//h3[@class="naglowek-0"]/a/text()').get().split()
			if issue_name_number[0] == 'Przewodnik' and issue_name_number[1] == 'Katolicki':
				issue_cover_url = urljoin(response.url, str(issue.xpath('.//div[@class="zdjecie"]/a/img/@src').get()).replace('.aspx?width=150', '.aspx?width=600'))
				issue_dict = {
					'issue_name' : 'przewodnik_katolicki',
					'issue_cover_url' : issue_cover_url
				}
				# go to the issue page and pass the current collected issue info
				issue_url = issue.xpath('.//h3[@class="naglowek-0"]/a/@href').get()
				yield response.follow(issue_url, meta=issue_dict, callback=self.parse_issue)
		next_page = response.xpath('.//a[@title="Następna"]/@href').get()
		if next_page is not None:
			yield response.follow(next_page, callback=self.parse)

	def parse_issue(self, response):
		self.logger.info('Parse function called on {}'.format(response.url))
		# check if all articles are aviailable to read
		if not response.xpath('//h3[@class="naglowek-0 klodka"]'):
			issue_number = response.xpath('.//head[@id="head"]/title/text()').re_first(r"\d{1,2}/\d{4}").split('/')
			issue_dict = response.meta
			issue_dict['issue_number'] = f'{issue_number[0].zfill(2)}/{issue_number[1]}'
			issue_dict['issue_url'] = response.url
			articles = response.xpath('.//li[@class="zajawka-art"]/h3[@class="naglowek-0 "]/a/@href').getall()
			for article in articles:
				yield response.follow(article, callback=self.parse_article, meta=issue_dict)
				
	def parse_article(self, response):
		self.logger.info('Parse function called on {}'.format(response.url))
		loader = ItemLoader(item=WeekliesScraperItem(), response=response)
		loader.add_value('issue_name', response.meta['issue_name'])
		loader.add_value('issue_number', response.meta['issue_number'])
		loader.add_value('issue_url', response.meta['issue_url'])
		loader.add_value('issue_cover_url', response.meta['issue_cover_url'])
		loader.add_xpath('article_authors', './/span[@class="wpis"]/i/*[@class="autor"]')
		loader.add_xpath('article_title', './/header[@class="naglowek"]/*[@class="naglowek-4"]')
		loader.add_xpath('article_intro', './/p[@class="wstep"]')
		loader.add_xpath('article_content', './/article[@class="artykul"]/div[@class="tresc"]/descendant::*[self::p or self::strong]/text()')
		loader.add_xpath('article_tags', './/div[@class="tagi clearfix"]/ul/li/span/a/text()')
		loader.add_value('article_url', response.url)
		loader.add_xpath('section_name', './/h2[@class="nagl-akord kategoria aktywne"]')
		yield loader.load_item()