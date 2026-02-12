#-- Imports --
import sqlite3
import codecs
import math
import numpy as np
#--------------

# ----------------------- FUNCTION BIN -----------------------

# ------ File read / write functions ------
def listTrainingLines():
    """
    Returns a array  containing each row and then each entry as a tuple \n
    Format for each row is given as follows:                            \n
    user_id (int), item_id (int), user_rating (float), timestamp (int)
    """

    #Get all the lines from the csv file
    print("Reading the training ratings file...")
    readHandler = codecs.open( 'train_100k_withratings.csv', 'r', 'utf-8', errors = 'replace')
    listLines = readHandler.readlines()
    readHandler.close()

    #Cleans them up and adds them to a 2D array
    print("Cleaing up the csv file and reading in correct formats...")
    output = []
    for line in listLines:
        tempLine = line.replace("\n", "")
        splitLine = tempLine.split(",")
        
        lineTuple = (int(splitLine[0]), int(splitLine[1]), float(splitLine[2]), int(splitLine[3]))
        output.append(lineTuple)

    return output

def createSQLtables(listLines):
    #Creating ratings table
    print("Connecting to sqlite3 db or whatever...")
    connector = sqlite3.connect('recommender.db')
    c = connector.cursor() #Needed to init the cursor (tell sql where to do stuff)

    print("Creating new ratings table...")
    c.execute('DROP TABLE IF EXISTS ratings') #Clearing old data each time it runs
    c.execute('''
        CREATE TABLE ratings (
              userID INT,
              itemID INT,
              rating FLOAT,
              timestamp INT
              )
              ''')

    # Inserting things into the ratings table
    print("Inserting values into new ratings table...")
    for line in listLines:
        c.execute('INSERT INTO ratings VALUES (?,?,?,?)', 
                 (line[0], line[1], line[2], line[3]))
        
    connector.commit() #Like git lol

    #Creating indexes
    print("Creating indexes...")
    # UserID index (when wanting to get all the items that user i rated)
    c.execute('CREATE INDEX idx_user ON ratings(userID)')
    
    # itemID index (when wanting to get all the users that rated some item x)
    c.execute('CREATE INDEX idx_item ON ratings(itemID)')

    # composite just in case i need it (don't know if I actually will)
    c.execute('CREATE index idx_user_item ON ratings(userID, itemID)')

    connector.commit() # Git moment!

    c.close()
    connector.close()


# ----------------------- CODE EXECUTION -----------------------
if __name__ == '__main__':
    
    # Get the data
    listLines = listTrainingLines()

    # Create sql tables and indexes with that data
    createSQLtables(listLines)

    #Quickly testing that then indexes work
    connector = sqlite3.connect('recommender.db')
    c = connector.cursor() #Needed to init the cursor (tell sql where to do stuff)

    c.execute('SELECT itemID, rating FROM ratings WHERE userId = 1')
    print(f"User 1 ratings: {c.fetchall()}")

    c.close()
    connector.close()

    # Calculate the cosine simularity of each user with each user

    # Go through each unrated item and find neighbourhood of users for that user

    # Using the neighbourhood calculate the score that the user should give (avg I think)

    # Done! Write all results to a file (if not doing already)

