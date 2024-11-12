from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider

from dlsu_website.spiders.dlsu_website import WebsiteSpider, website_queue

from website_consumer import WebsiteConsumer

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

  n_threads = int(arg3)

  toCsv = ToCSV()

  c_threads=[]
  for i in range(n_threads):
    t = WebsiteConsumer(i, toCsv)
    c_threads.append(t)
    t.start()

  for _ in range(minutes):
    time.sleep(1)

  process.stop()

  website_count = 0
  for c in c_threads:
    website_count += c.getCount()
    c.stop()

  email_count = toCsv.getEmailCount()
  print(website_count)
  print(email_count)

  toCsv.toCsv()

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Usage: python main.py <url> <minutes> [threads]")
  else:
    count = 2
    if len(sys.argv) == 4:
      count = sys.argv[3]
    main(sys.argv[1], sys.argv[2], count)