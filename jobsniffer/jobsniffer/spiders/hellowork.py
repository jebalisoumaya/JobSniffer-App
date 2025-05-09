import scrapy


class HelloworkSpider(scrapy.Spider):
    name = "hellowork"
    allowed_domains = ["pole-emploi.fr"]
    start_urls = ["https://pole-emploi.fr"]

    def parse(self, response):
        pass
