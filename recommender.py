#-- Imports --
import sqlite3
import codecs
import math
import numpy as np
#--------------

# CONFIG options
ITEM_RATING_OVERLAP_THRESHOLD = 2 # Requires at least this many items to be shared between two users so consider calculating a simularity score, otherwise returns 0


#Open up sql connection
connector = sqlite3.connect("recommender.db")
c = connector.cursor()


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
        c.execute('INSERT INTO ratings VALUES (?,?,?,?)', (line[0], line[1], line[2], line[3]))
        
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

def getUserRatings(user_id: int):
    """   
    :param user_id: the user id for the ratings you want to get

    Returns: All ratings from input user as a dictionary {itemID: rating, ...}
    """
    c.execute('SELECT itemID, Rating FROM ratings WHERE userID = ?', (user_id,))

    itemsDict = {}
    for row in c.fetchall():
        itemsDict[row[0]] = row[1]
    
    return itemsDict

def calculateCosineSim(ratings1: dict, ratings2: dict):
    """
    Given two users and their ratings, calculate their simularity between one another
    
    :param ratings1: {itemID: rating, ...} dictionary
    :param ratings2: {itemID: rating, ...} dictionary

    Returns: a similarity score FLOAT from 0 to 1
    """
    # Get items that are rated by both users
    sharedItems = set(ratings1.keys()) & set(ratings2.keys())

    # If none are shared then aren't similar at all
    if len(sharedItems) < 1:
        return 0.0

    #Calculating mean
    user1Mean = 0
    user2Mean = 0
    for item in sharedItems:
        user1Mean += ratings1[item]
        user2Mean += ratings2[item]
    
    user1Mean = user1Mean / len(sharedItems)
    user2Mean = user2Mean / len(sharedItems)

    #Top half of the equation
    topHalfSum = 0
    for item in sharedItems:
        topHalfSum += ((ratings1[item] - user1Mean) * (ratings2[item] - user1Mean))

    #Bottom half of the equation
    bottomHalfUser1Sum = 0
    bottomHalfUser2Sum = 0
    for item in sharedItems:
        bottomHalfUser1Sum += (ratings1[item] - user1Mean) ** 2
        bottomHalfUser2Sum += (ratings2[item] - user2Mean) ** 2

    bottomHalfUser1Sum = math.sqrt(bottomHalfUser1Sum)
    bottomHalfUser2Sum = math.sqrt(bottomHalfUser2Sum)

    # Just stops any divide by 0 errors if they come up!
    if (bottomHalfUser1Sum == 0 or bottomHalfUser2Sum == 0):
        return 0.0 

    similarity = topHalfSum / (bottomHalfUser1Sum * bottomHalfUser2Sum)

    return similarity



def precomputeSimularities():
    """
    Precomputes the cosine simularity between EACH user (U2U) and stores it in a seperate table called similarities, 
    """

    #Creating table for user cosine simularities (stored as pairs between two users)
    print("Creating table for user cosine simularities...")
    c.execute('DROP TABLE IF EXISTS similarities') #Clearing old data each time it runs
    c.execute('''
              CREATE TABLE similarities(
              user1ID INT, 
              user2ID INT,
              similarity FLOAT
              )
              ''')
    
    #Going through and getting each similarity
    print("Calculating similarities between each user...")
    c.execute('SELECT DISTINCT userID FROM ratings')
    userIDs = c.fetchall()
    for user1 in userIDs:
        user1ID = user1[0] #Because sql works with tuples
        user1Ratings = getUserRatings(user1ID)
        for user2 in userIDs:
            user2ID = user2[0] #Ditto as above comment

            # If they are the same then just skip this
            if user1ID == user2ID:
                continue

            user2Ratings = getUserRatings(user2ID)

            similarity = calculateCosineSim(user1Ratings, user2Ratings)

            c.execute('INSERT INTO similarities VALUES (?,?,?)', (user1ID, user2ID, similarity))
    
    connector.commit()

def getUserNeighbourHood(userID: int):
    c.execute('''
              SELECT user2ID, similarity
              FROM similarities
              WHERE user1ID = ? 
              ORDER BY similarity DESC 
              LIMIT 30
              ''', (userID,))
    
    return c.fetchall()

# ----------------------- CODE EXECUTION -----------------------
if __name__ == '__main__':
    
    # Get the data
    listLines = listTrainingLines()

    # Create sql tables and indexes with that data
    createSQLtables(listLines)

    # Calculate the cosine simularity of each user with each user
    precomputeSimularities()

    # Go through each unrated item and find neighbourhood of users for that user

    #Testing user1 neighbours
    print(getUserNeighbourHood(userID=1))

    # Using the neighbourhood calculate the score that the user should give (avg I think)

    # Done! Write all results to a file (if not doing already)

    #Close connection
    c.close()
    connector.close()

