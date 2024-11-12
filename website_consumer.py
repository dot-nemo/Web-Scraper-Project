from dlsu_website.spiders.dlsu_website import website_queue
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dlsu_website.spiders.cf_email import EmailSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals

import threading, time

import csv

class WebsiteConsumer(threading.Thread):
  def __init__(self, id):
    threading.Thread.__init__(self)
    self.item=""
    self.result_dict={}
    self.thread_id = id
    self._stop_event = threading.Event()

  def run(self):
    process = CrawlerProcess(get_project_settings())
    self.running = True
    print(f"Consumer {self.thread_id} is waiting\n")

    while not self._stop_event.is_set():
      results = []
      def crawler_results(signal, sender, item, response, spider):
        if self.thread_id == spider.id:
          results.append(item)

      dispatcher.connect(crawler_results, signal=signals.item_scraped)

      try:
        self.item = website_queue.get(timeout=3)
      except:
        continue

      print(f"Consumer {self.thread_id} processing {self.item}")

      process.stop()
      process.crawl(EmailSpider, url=self.item, id=self.thread_id)

      if len(results) > 0:
        for item in results:
          email = item["email"]
          del item["email"]
          self.result_dict[email] = item

    output = f"Consumer {self.thread_id} processed: \n {self.result_dict}"
    print(output)
    # with open('emails.csv', 'w', newline='') as csvfile:
    #   fieldnames = ['email']
    #   writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    #   writer.writeheader()
    #   for i in self.list:
    #     writer.writerow({'email': i})

  def stop(self):
    self._stop_event.set()
