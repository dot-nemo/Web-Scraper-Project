import scrapy

class EmailSpider(scrapy.Spider):
  name = "email"
  allowed_domains = ["www.dlsu.edu.ph"]

  def __init__(self, url=None, id=None, *args, **kwargs):
    super(EmailSpider, self).__init__(*args, **kwargs)
    self.start_urls = [url]  # Use the provided URL
    self.id = id


  def parse(self, response):
    for element in response.css('.__cf_email__'):
      if element.css('.__cf_email__::attr(data-cfemail)').extract_first():
        email=self.decodeEmail(element.css('.__cf_email__::attr(data-cfemail)').extract_first())
        yield {
          'email': email
        }

  def decodeEmail(self, e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
      de += chr(int(e[i:i+2], 16)^k)

    return de