import csv
import threading
import Pyro4

@Pyro4.expose
class ToCSV() :
    lock = threading.Lock()
    def __init__(self):
        self.emailsDict = {}

    def read(self):
        return self.emailsDict

    def addItem(self, email, firstname, lastname):
        with ToCSV.lock:
            self.emailsDict.update({email: {'firstname': firstname, 'lastname': lastname}})
            self.toCsv()

    def toCsv(self):
        with open('emails.csv', 'w', newline='') as csvfile:
            fieldnames = ['email', 'first name', 'last name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for email, info in self.emailsDict.items():
                writer.writerow({'email': email, 'first name': info['firstname'], 'last name': info['lastname']})

    def getEmailCount(self):
        return len(self.emailsDict)