from website_consumer import WebsiteConsumer
import sys

if __name__ == "__main__":
  id = 0
  if len(sys.argv) > 1:
    id = int(sys.argv[1])
  t = WebsiteConsumer(id)
  t.start()
  t.join()