from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import Pyro4

from dlsu_website.spiders.dlsu_website import WebsiteSpider

from toCsv import ToCSV

import threading
import time
import sys

def main(arg1, arg2, arg3):
  process = CrawlerProcess(get_project_settings())

  process.crawl(WebsiteSpider, url=arg1)

  t1 = threading.Thread(target=process.start)
  t1.start()

  minutes = int(arg2) * 60

  for i in range(minutes):
    print(i)
    time.sleep(1)

  process.stop()

  website_count = 0

  email_count = 0

  f = open("results.txt", "w")
  f.write(f"URL: {arg1}\nNumber of pages: {website_count}\nNumber of emails: {email_count}")
  f.close()

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Usage: python _web_crawler.py <url> <minutes> [nodes]")
  else:
    count = 2
    if len(sys.argv) == 4:
      count = sys.argv[3]
    main(sys.argv[1], sys.argv[2], count)