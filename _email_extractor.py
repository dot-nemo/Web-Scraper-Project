from twisted.internet import asyncioreactor
asyncioreactor.install()

from dlsu_website.spiders.dlsu_website import website_queue
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from dlsu_website.spiders.cf_email import EmailSpider
from scrapy.signalmanager import dispatcher
from scrapy import signals
import pika, json
from twisted.internet import reactor, threads
import Pyro4


class WebsiteConsumer:
    def __init__(self, id, toCsv=None):
        self.result_dict = {}
        self.thread_id = id
        self.toCsv = toCsv
        self.count = 0
        try:
          credentials = pika.PlainCredentials('rabbituser', 'rabbit1234')

          connection = pika.BlockingConnection(pika.ConnectionParameters('10.2.202.75',5672,'/',credentials))
          self.channel = connection.channel()

          self.channel.queue_declare(queue='rqueue')
          print("Connected to RabbitMQ")
          self.channel.basic_consume('rqueue', self.callback, True)
        except:
          print("Unable to connect to RabbitMQ")

    def process_url(self, url):
        runner = CrawlerRunner(get_project_settings())
        results = []

        # def crawler_results(signal, sender, item, response, spider):
        #     if self.thread_id == spider.id:
        #         results.append(item)

        # dispatcher.connect(crawler_results, signal=signals.item_scraped)

        # Schedule the crawl
        d = runner.crawl(EmailSpider, url=url, id=self.thread_id)

        # Process results after crawl completes
        # d.addCallback(lambda _: self._process_results(results))
        # d.addErrback(lambda error: print(f"Error in spider: {error}"))

    def _process_results(self, results):
        if results:
            for item in results:
                email = item["email"]
                del item["email"]
                self.result_dict[email] = item
                self.toCsv.addItem(email, self.result_dict[email]['firstname'], self.result_dict[email]['lastname'])
        self.count += 1

    def callback(self, ch, method, properties, body):
        print(" [x] Received %r" % body)
        body_dict = json.loads(body)
        url = body_dict["url"]

        # Schedule processing on the reactor thread
        reactor.callFromThread(self.process_url, url)


def start_pika_consumer():
    """Starts the Pika consumer."""
    credentials = pika.PlainCredentials("rabbituser", "rabbit1234")
    connection = pika.BlockingConnection(pika.ConnectionParameters("10.2.202.75", 5672, "/", credentials))
    channel = connection.channel()

    channel.queue_declare(queue="rqueue")

    webcon = WebsiteConsumer(id=1)
    channel.basic_consume(queue="rqueue", on_message_callback=webcon.callback, auto_ack=True)

    print(" [*] Waiting for messages. To exit press CTRL+Z")
    channel.start_consuming()


# Run Pika consumer in a separate thread
threads.deferToThread(start_pika_consumer)

# Start the Twisted reactor
reactor.run()
