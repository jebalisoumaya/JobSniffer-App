import scrapy


class IndeedSpider(scrapy.Spider):
    name = "indeed"
    allowed_domains = ["indeed.fr"]
    start_urls = ["https://indeed.fr"]

    def parse(self, response):
        pass
