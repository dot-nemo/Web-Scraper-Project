from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider

from dlsu_website.spiders.dlsu_website import WebsiteSpider, website_queue

from website_consumer import WebsiteConsumer

from toCsv import ToCSV

import threading
import time
import sys

def main(arg1, arg2):
  process = CrawlerProcess(get_project_settings())

  process.crawl(WebsiteSpider, url=arg1)

  t1 = threading.Thread(target=process.start)
  t1.start()
  print(website_queue)

  minutes = int(arg2) * 60

  n_threads = 1

  toCsv = ToCSV()

  c_threads=[]
  for i in range(n_threads):
    t = WebsiteConsumer(i, toCsv)
    c_threads.append(t)
    t.start()

  for _ in range(minutes):
    time.sleep(1)

  process.stop()

  for c in c_threads:
    c.stop()

  toCsv.toCsv()

if __name__ == "__main__":
  # if len(sys.argv) != 3:
  #   print("Usage: python main.py <url> <minutes>")
  # else:
  #   main(sys.argv[1], sys.argv[2])
  main("https://www.dlsu.edu.ph", 1)