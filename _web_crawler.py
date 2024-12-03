from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import Pyro4

from dlsu_website.spiders.dlsu_website import WebsiteSpider, website_queue

from toCsv import ToCSV

import threading
import time
import sys
from toCsv import ToCSV

import pika, json

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

  """Starts the Pika consumer."""
  credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
  connection = pika.BlockingConnection(pika.ConnectionParameters("10.2.202.75", 5672, "/", credentials))
  channel = connection.channel()

  q = channel.queue_declare(queue="equeue")
  q = q.method.message_count

  tocsv = ToCSV()

  def callback(ch, method, properties, body):
    body_dict = json.loads(body)
    tocsv.addItem(body_dict['email'], body_dict['firstname'], body_dict['lastname'])
    q = q - 1
    if q == 0:
      channel.stop_consuming()

  channel.basic_consume(queue="equeue", on_message_callback=callback, auto_ack=True)

  channel.start_consuming()

  website_count = website_queue.qsize()

  email_count = tocsv.getEmailCount()

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