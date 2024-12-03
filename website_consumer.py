from dlsu_website.spiders.dlsu_website import website_queue
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dlsu_website.spiders.cf_email import EmailSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals
from toCsv import ToCSV
import pika, json

import threading, time

import csv

class WebsiteConsumer(threading.Thread):
  def __init__(self, id, toCsv=None):
    threading.Thread.__init__(self)
    self.item=""
    self.result_dict={}
    self.thread_id = id
    self._stop_event = threading.Event()
    self.toCsv = toCsv
    self.count = 0


    try:
      credentials = pika.PlainCredentials('rabbituser', 'rabbit1234')

      connection = pika.BlockingConnection(pika.ConnectionParameters('10.2.202.75',5672,'/',credentials))
      self.channel = connection.channel()

      self.channel.queue_declare(queue='rqueue')
      print("Connected to RabbitMQ")
      self.channel.basic_consume('rqueue', True, self.callback)
    except:
      print("Unable to connect to RabbitMQ")

  def callback(self, ch, method, properties, body):
    self.results = []
    def crawler_results(signal, sender, item, response, spider):
      if self.thread_id == spider.id:
        self.results.append(item)

    process = CrawlerProcess(get_project_settings())
    print(" [x] Received %r" % body)

    # parse body here
    body_dict = json.loads(body)
    self.item = body_dict["url"]

    print(f"Consumer {self.thread_id} processing {self.item}")

    process.stop()
    process.crawl(EmailSpider, url=self.item, id=self.thread_id)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    if len(self.results) > 0:
      for item in self.results:
        email = item["email"]
        del item["email"]
        self.result_dict[email] = item
        if self.toCsv != None:
          self.toCsv.addItem(email, self.result_dict[email]['firstname'], self.result_dict[email]['lastname'])
        else:
          print("%s %s %s", email, self.result_dict[email]['firstname'], self.result_dict[email]['lastname'])

    self.count += 1


  def run(self):
    self.running = True
    self.channel.start_consuming()
    while not self._stop_event.is_set():
      pass

    # output = f"Consumer {self.thread_id} processed: \n {self.result_dict}"
    # print(output)



  def stop(self):
    self._stop_event.set()

  def getCount(self):
    return self.count