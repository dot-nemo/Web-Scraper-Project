import scrapy
import re
import pika, json

class EmailSpider(scrapy.Spider):
  name = "email"
  allowed_domains = ["www.dlsu.edu.ph"]
  non_names = [
    "De La Salle University",
  ]

  affixes = [
    "Dr.",
    "Dr",
    "PhD",
    "Ph.D",
    "Ph.d",
    "Ph.d.",
    "Ms.",
    "Ms",
    "Mr.",
    "Mr",
    "Engr.",
    "Engr",
    "Atty.",
    "Atty",
  ]

  def __init__(self, url=None, id=None, *args, **kwargs):
    super(EmailSpider, self).__init__(*args, **kwargs)
    self.start_urls = [url]  # Use the provided URL
    self.id = id
    try:
      credentials = pika.PlainCredentials('rabbituser', 'rabbit1234')

      connection = pika.BlockingConnection(pika.ConnectionParameters('10.2.202.75',5672,'/',credentials))
      self.channel = connection.channel()

      self.channel.queue_declare(queue='equeue')
      print("Connected to RabbitMQ")
    except:
      print("Unable to connect to RabbitMQ")


  def parse(self, response):
    for element in response.css('.__cf_email__'):
      if element.css('.__cf_email__::attr(data-cfemail)').extract_first():
        firstname = lastname = ""
        email=self.decodeEmail(element.css('.__cf_email__::attr(data-cfemail)').extract_first())
        try:
          match, _ = re.match("^([^@]+)@(.+)$", email).groups()
          if '.' in match:
            name1, name2 = re.match(r"^([^.]+)\.([^.]+)$", match).groups()
            longest_name = 0
            firstname = lastname = ""
            for potential_name in response.css("*::text"):
              if name1.lower() in str(potential_name).lower() and name2.lower() in str(potential_name).lower():
                narrowed_name = str(potential_name).strip()
                if len(narrowed_name) < 500 and not any(banned_names in narrowed_name for banned_names in self.non_names):
                  split_name = narrowed_name.replace(",", "").split(" ")
                  if len(split_name) > longest_name:
                    split_name = [item for item in split_name if item not in self.affixes]
                    firstname = lastname = ""
                    if "," in narrowed_name:
                      lastname = split_name[0].capitalize()
                      for spl in split_name[1:]:
                        firstname += f" {spl.capitalize()} "
                        firstname = firstname.strip()
                    else:
                      for spl in split_name[:-1]:
                        firstname += f" {spl.capitalize()} "
                        firstname = firstname.strip()
                      lastname = split_name[-1].replace(",", "").capitalize()
        except:
          pass
        if email:
          msg_dict={
            'email': email,
            'firstname': firstname,
            'lastname': lastname
          }
          msg_json=json.dumps(msg_dict)
          self.channel.basic_publish(exchange='', routing_key='rqueue', body=msg_json)
          print(" [x] Sent '%s'", email, end="\r")
        yield {
          'email': email,
          'firstname': firstname,
          'lastname': lastname
        }

  def decodeEmail(self, e):
    de = ""
    k = int(e[:2], 16)

    for i in range(2, len(e)-1, 2):
      de += chr(int(e[i:i+2], 16)^k)

    return de