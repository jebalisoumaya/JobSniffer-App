import scrapy


class WttjSpider(scrapy.Spider):
    name = "wttj"
    allowed_domains = ["welcometothejungle.com"]
    start_urls = ["https://welcometothejungle.com"]

    def parse(self, response):
        pass
