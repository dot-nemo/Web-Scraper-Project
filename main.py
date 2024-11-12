from scrapy.crawler import CrawlerRunner, CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import CloseSpider

from dlsu_website.spiders.dlsu_website import WebsiteSpider, website_queue

from website_consumer import WebsiteConsumer

import threading
import time
import sys

def main(arg1, arg2, arg3):
  process = CrawlerProcess(get_project_settings())

  process.crawl(WebsiteSpider, url=arg1)

  t1 = threading.Thread(target=process.start)
  t1.start()
  print(website_queue)

  minutes = int(arg2) * 60

  c_threads=[]
  for i in range(arg3):
    t = WebsiteConsumer(i)
    c_threads.append(t)
    t.start()

  for _ in range(minutes):
    time.sleep(1)

  process.stop()

  for c in c_threads:
    c.stop()



if __name__ == "__main__":
  if len(sys.argv) < 3:
    print("Usage: python main.py <url> <minutes> [number of threads]")
  else:
    if len(sys.argv) == 4:
      threads = int(sys.argv[3])
    else:
      threads = 2
    main(sys.argv[1], sys.argv[2], threads)
  # main("https://www.dlsu.edu.ph", 1)