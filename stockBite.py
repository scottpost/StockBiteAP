#==================================================================================================================================
# IMPORTS
#==================================================================================================================================

import sqlite3 as lite

#==================================================================================================================================
# STOCKBITE CLASS ABSTRACTION
#==================================================================================================================================
   
class StockBite:
    
    #Keep track of number of bites
    totalBites = 0

    def __init__(self, row):
        self.security = row[0]
        self.message = row[1]
        self.author = row[2]
        self.date = row[3]
        
        #Prediction will be analyzed and assigned to: 1 (Bullish) || 0 (Neutral) || -1 (Bearish)
        self.prediction = 0

        #Represents the bites real time value (in $USD)
        self.value = 0.0 
        
        StockBite.totalBites += 1

    def getSecurity(self):
        return self.security

    def getMessage(self):
        return self.message

    def getAuthor(self):
        return self.author

    def getDate(self):
        return self.date

    def getPrediction(self):
        return self.prediction

    def setPrediction(self, pred):
        self.prediction = pred

    def getValue(self):
        return self.value

    @staticmethod
    def getTotalBites():
        return StockBite.totalBites

    @staticmethod
    def queryBites(queryType, query):
        if queryType == "security":
            i = 0
        if queryType == "message":
            i = 1
        if queryType == "author":
            i = 2
        if queryType == "date":
            i = 3
        stockBites = []
        conn = lite.connect('StockBite.db')
        c = conn.cursor()
        for row in c.execute('SELECT * FROM bites'):
            if query.upper() == row[i]:
                stockBites.append(StockBite(row))
        return stockBites

    @staticmethod
    def loadAll():
        stockBites = []
        conn = lite.connect('StockBite.db')
        c = conn.cursor()
        for row in c.execute('SELECT * FROM bites'):
            stockBites.append(StockBite(row))
        return stockBites

#==================================================================================================================================
#
#==================================================================================================================================