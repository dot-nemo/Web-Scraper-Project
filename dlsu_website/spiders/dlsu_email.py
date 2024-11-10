import scrapy


class CCSEmailSpider(scrapy.Spider):
  name = "ccs_email"
  allowed_domains = ["www.dlsu.edu.ph"]
  start_urls = ["https://www.dlsu.edu.ph/colleges/ccs/faculty-profile/"]

  def parse(self, response):
    CONTENT_SELECTOR = '.wpb_text_column'
    POSITION_SELECTOR = '.vc_message_box.vc_message_box-standard.vc_message_box-rounded.vc_color-white'
    DEPARTMENT_SELECTOR = '.breadcrumbs'

    try:

      for body in response.css(CONTENT_SELECTOR):
          name = body.css('span::text').extract_first()
          email = self.decodeEmail(body.css('.__cf_email__::attr(data-cfemail)').extract_first())

      for body in response.css(POSITION_SELECTOR):
          position = body.css('p::text').extract_first()

      for body in response.css(DEPARTMENT_SELECTOR):
          department = body.css('li > a::attr(title)').extract()[2]

      yield {
         'name': name,
         'email': email,
         'position': position,
         'department': department,
      }
    except:
      pass

    next_page = response.css('.wpb_column.vc_column_container.vc_col-sm-4 h3 > a::attr(href)').extract()
    for page in  next_page:
      yield scrapy.Request(
        response.urljoin(page)
      )

  def decodeEmail(self, e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
      de += chr(int(e[i:i+2], 16)^k)

    return de
