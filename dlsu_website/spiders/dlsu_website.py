import scrapy
import queue
import threading

website_queue = queue.Queue()

class WebsiteSpider(scrapy.Spider):
  thread_id = threading.get_ident()
  handle_httpstatus_list = [404]
  name = "website"
  allowed_domains = ["www.dlsu.edu.ph"]
  start_urls = []

  result_list = []

  todo_list = []

  filetype_list = [
    '.pdf',
    '.png',
    '.jpg',
  ]

  def __init__(self, url=None, *args, **kwargs):
    global website_queue
    super(WebsiteSpider, self).__init__(*args, **kwargs)
    self.start_urls = [url]  # Use the provided URL
    website_queue.put(url)


  def parse(self, response):
    global website_queue
    url = str(response.request.url)
    for anchor in response.css('a::attr(href)'):
      path = str(anchor).strip()

      if path and path[0] == '/':
        path = 'https://www.dlsu.edu.ph' + path

      if path and path[-1] == '/':
        path = path[:-1]

      if "www.dlsu.edu.ph" not in path:
        continue

      try:
        for filex in self.filetype_list:
          if filex in path:
            raise
        if path not in self.result_list and path not in self.todo_list and "email-protection" not in path:
          website_queue.put(path)
          self.todo_list.append(path)
      except:
        pass

    # for anchor in response.css('a'):
    #   if anchor.css('.__cf_email__::attr(data-cfemail)').extract_first():
    #     yield {
    #       'email': self.decodeEmail(anchor.css('.__cf_email__::attr(data-cfemail)').extract_first())
    #     }

    self.result_list.append(url)
    next_page = self.todo_list.pop(0)

    yield scrapy.Request(
      response.urljoin(next_page),
    )

  # def decodeEmail(self, e):
  #   de = ""
  #   k = int(e[:2], 16)

  #   for i in range(2, len(e)-1, 2):
  #     de += chr(int(e[i:i+2], 16)^k)

  #   return de