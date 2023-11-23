from bs4 import BeautifulSoup
from pymongo import MongoClient

# Connect to database using previous hw code
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

# Store all CS professor database in mongodb
def storeProfessors(db):
    #Get the html data of the permanent faculty page
    entry = db.pages.find_one({'url': 'https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml'})
    html = entry['html']

    # Create bs object
    bs = BeautifulSoup(html, "html.parser")
    # Find the section with all the professors which are seperated by divs
    result = bs.find('section').find_all('div')

    # Iterate through each professor
    for entry in result:
        # Check if there is the h2(name) some have missing ones
        if entry.h2:
            # Get data which can easily be found with help of bs
            name = entry.h2.text.strip()
            email = entry.find('a').text
            # Get the second link tag and website
            website = entry.find_all('a', href=True)[1]['href']

            # Title and office are a little harder to get due to the strong tag
            # Get all the text
            data = entry.find('p').text.split()
            title = ""
            office = ""

            # Start iterating from index 1 (ignore Title:)
            for i in range(1, len(data)):
                # When we hit office we stop and get next element which is the office
                if data[i] == 'Office:':
                    office = data[i+1]
                    break
                # Keep adding to title some are greater than 1 word
                title += data[i] + " "

            # Reformate data
            title = title.strip()
            office = office.strip()

            # Dictionary that we will insert in mongoDB
            information = {
                "Name": name,
                "Title": title,
                "Office": office,
                "Email": email,
                "Website": website
            }

            # Insert into faculty collection
            db.faculty.insert_one(information)
            
# Main Program to store all professors in database
# Create db connection
db = connectDataBase()
# Call function with db connection to store all professors
storeProfessors(db)




