import scrapy


class DlsuEmailSpider(scrapy.Spider):
    name = "dlsu_email"
    allowed_domains = ["www.dlsu.edu.ph"]
    start_urls = ["https://www.dlsu.edu.ph/"]

    def parse(self, response):
        pass
