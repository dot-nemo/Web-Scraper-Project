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

class WebsiteConsumer():
  def __init__(self, id, toCsv=None):
    self.result_dict={}
    self.thread_id = id
    self.toCsv = toCsv
    self.count = 0

  def processURL(self, url):
    process = CrawlerProcess(get_project_settings())
    results = []
    def crawler_results(signal, sender, item, response, spider):
        if self.thread_id == spider.id:
          results.append(item)

    dispatcher.connect(crawler_results, signal=signals.item_scraped)

    process.crawl(EmailSpider, url=url, id=self.thread_id)
    process.start()

    if len(results) > 0:
      for item in results:
        email = item["email"]
        del item["email"]
        self.result_dict[email] = item
        # self.toCsv.addItem(email, self.result_dict[email]['firstname'], self.result_dict[email]['lastname'])

    self.count += 1

  def getCount(self):
    return self.count

  def callback(self, ch, method, properties, body):
    print(" [x] Received %r" % body)
    body_dict = json.loads(body)
    url = body_dict["url"]
    self.processURL(url)

credentials = pika.PlainCredentials('rabbituser', 'rabbit1234')

connection = pika.BlockingConnection(pika.ConnectionParameters('10.2.202.75',5672,'/',credentials))
channel = connection.channel()

channel.queue_declare(queue='rqueue')

webcon = WebsiteConsumer()

callback = webcon.callback

channel.basic_consume('rqueue', callback, True)

channel.start_consuming()