from website_consumer import WebsiteConsumer

if __name__ == "__main__":
  t = WebsiteConsumer(0)
  t.start()
  t.join()