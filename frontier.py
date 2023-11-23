from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re

# Implementing frontier class to fufill algorithm
class Frontier:
    def __init__(self):
        self.urls = []
    def addURL(self, url):
        self.urls.append(url)
    def nextURL(self):
        if self.urls:
            return self.urls.pop(0)
        return None
    def done(self):
          return not self.urls
    def clear(self):
        self.urls = []
    
# Method to retreive the url returns the html text
def retrieveURL(url):
    try:
        html = urlopen(url)
        bs = BeautifulSoup(html.read(), "html.parser")
        return str(bs.get_text)
    except:
        print("Could not open:", url)

# Store a page in mongo db in pages collection
def storePage(url, html, db):
    try:
        db.pages.insert_one({
            "url": url,
            "html": html
        })
    except:
        print("Error inserting document")

# Checks to see if it is the CS Permanent faculty page
def target_page(html):
    bs = BeautifulSoup(html, "html.parser")
    regex = re.compile('Permanent Faculty')
    result = bs.find_all('h1', text=regex)
    if result:
        return True
    return False

# Parse the html page for additional links
def parse(html, base):
    bs = BeautifulSoup(html, "html.parser")
    # Find all additional links and add it to the links list
    result = bs.find_all('a', href=True)
    links = []
    for link in result:
        links.append(link['href'])

    # Checking for relative and full links
    # Only want full links so retrieve URL wont crash
    regex = re.compile('^https') 
    valid_links = []
    for link in links:
        # If it is a full link then url is = link
        if re.match(regex, link):
            url = link
        else:
        # If it is not we will join the bas link to the relative to create full link
            url = urljoin(base, link)
        # Add full url to valid_links
        valid_links.append(url)
    
    #Return valid links
    return valid_links

# Create database connection using code from previous hw
def connectDataBase():
    # Create a database connection object using pymongo
    # --> add your Python code here
    DB_NAME = "corpus"
    DB_HOST = "localhost"
    DB_PORT = 27017

    try:
         client = MongoClient(host=DB_HOST, port=DB_PORT)
         db = client[DB_NAME]
         return db
    
    except:
         print("Database not connected successfully")

# Psuedo code previded 
def crawler_thread(frontier, db):
    while not frontier.done():
        url = frontier.nextURL()
        html = retrieveURL(url)
        storePage(url, html, db)
        if target_page(html):
            # Implemented the clear in frontier class because it was more convienet
            frontier.clear()
        else:
            # Passing in url to parse to deal with relative/full links
            for link in parse(html, url):
                frontier.addURL(link)

# Main Program
# Databse connection, start link
db = connectDataBase()
start = 'https://www.cpp.edu/sci/computer-science/'

# Frontier, add start link and use crawler thread.
frontier = Frontier()
frontier.addURL(start)
crawler_thread(frontier, db)
