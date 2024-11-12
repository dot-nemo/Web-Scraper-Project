import csv
import threading

class ToCSV() :
    def __init__(self):
        self.lock = threading.Lock()
        self.emailsDict = {}
    
    def read(self):
        return self.emailsDict
    
    def addItem(self, email, firstname, lastname):
        with self.lock:
            self.emailsDict.update({email: {'firstname': firstname, 'lastname': lastname}})

    def toCsv(self):
        with open('emails.csv', 'w', newline='') as csvfile:
            fieldnames = ['email', 'first name', 'last name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for email, info in self.emailsDict.items():
                writer.writerow({'email': email, 'first name': info['firstname'], 'last name': info['lastname']})
