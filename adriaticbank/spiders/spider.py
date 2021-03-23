import scrapy

from scrapy.loader import ItemLoader

from ..items import AdriaticbankItem
from itemloaders.processors import TakeFirst

import requests

url = "https://adriaticbank.com/en/news"

payload={}
headers = {
  'Cookie': 'PHPSESSID=gf65eotv7210fg13ud2r6c2cs5'
}


class AdriaticbankSpider(scrapy.Spider):
	name = 'adriaticbank'
	start_urls = ['https://adriaticbank.com/en/news']

	def parse(self, response):
		data = requests.request("GET", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)

		post_links = raw_data.xpath('//ul[@class="search_result r_sidebar_news_list news_list"]/li/a/@href').getall()
		for post in post_links:
			yield response.follow(post, self.parse_post, cb_kwargs={'url': post}, dont_filter=True)

	def parse_post(self, response, url):
		data = requests.request("GET", url, headers=headers, data=payload)
		raw_data = scrapy.Selector(text=data.text)
		title = raw_data.xpath('//h2[@class="page_title page_title_no_border page_in_title page_in_in_title"]/text()').get()
		description = raw_data.xpath('//div[@class="cover content"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=AdriaticbankItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)

		return item.load_item()
