#==================================================================================================================================
# IMPORTS
#==================================================================================================================================

from stockBite import StockBite
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from yahoo_finance import Share
from GChartWrapper import *
from urllib import urlopen
from faker import Faker
from datetime import date, timedelta
from bs4 import BeautifulSoup
from lxml.html import parse


#==================================================================================================================================
# CONFIGURATION
#==================================================================================================================================

#FLASK CONFIGURATION
app = Flask(__name__)
app.debug = True


#SECTOR CONFIGURATION
SECTORS = {
	"Technology" : "XLK",
	"Financials" : "XLF",
	"Industrials" : "XLI",
	"Cyclical Consumer Goods & Services" : "XLY",
	"Non-Cyclical Consumer Goods & Services" : "XLP",
	"Healthcare" : "XLV",
	"Energy" : "XLE"
}

#BLUECHIP CONFIGURATION
BLUECHIPS = ["BAC", "KO", "XOM", "IBM", "DIS"]

#==================================================================================================================================
# HELPER FUNCTIONS
#==================================================================================================================================

def getStockInfo(name):
  return "Healthcare", "Industry", "Name"

def drawGraphs(query, queryData, sector, sectorData):
	#Initialize variables
	GList = []
	dataset1 = []
	dataset2 = []
	dataset3 = []

	#Calculate correct dates for x-axis of graphs
	week4 = date.today()
	week3 = week4 - timedelta(days=7)
	week2 = week3 - timedelta(days=7)
	week1 = week2 - timedelta(days=7)
	w4 = week4.strftime('%d-%m-%y')
	w3 = week3.strftime('%d-%m-%y')
	w2 = week2.strftime('%d-%m-%y')
	w1 = week1.strftime('%d-%m-%y')

	#Gather trading volume data
	for tick in queryData.get_historical(week1.strftime('%Y-%m-%d'), week4.strftime('%Y-%m-%d')):
		dataset1.append(int(tick['Volume']))

	maxData = max(dataset1)
	G1 = GChart('lc', dataset1).axes.type('xy').axes.label(1, "0% ", "25% ", "50% ", "75% ", "100% ").label(w1, w2, w3, w4).axes.tick(1,20).size(400, 200).color('72c02c').scale(0, max(dataset1))
	G2 = GChart('lc', dataset1).axes.type('xy').axes.label(1, 0, "{:,}".format(maxData/4), "{:,}".format(maxData/2), "{:,}".format(3 * maxData/4), "{:,}".format(maxData)).label(w1, w2, w3, w4).axes.tick(1,20).size(400, 200).scale(0, maxData).color('72c02c')

	GList.extend([G1, G2])
	return GList

def stockBiteInfo(query):
    info = []
    for bite in StockBite.queryBites("security", query):
        info.append(bite.getMessage())
    return info

#==================================================================================================================================
# FLASK VIEW FUNCTIONS
#==================================================================================================================================

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		query = request.form["stockTicker"]
		return redirect(url_for('profile', query=query))
	return render_template('index.html')

@app.route('/faq')
def faq():
	return render_template('faq.html')

@app.route('/stocks')
def stocks():
	sectorData = Share("FORD")
	blueChips = []
	for stock in BLUECHIPS:
		blueChips.append(Share(stock))
	return render_template('stocks.html', sectorData=sectorData, blueChips=blueChips)

@app.route('/analysts')
def analysts():
	return render_template('analysts.html')

@app.route('/profile/<query>')
def profile(query):
	fake = Faker()
	queryData = Share(query)
	sector, industry, name = getStockInfo(query)
	biteInfo = []
	for bite in stockBiteInfo(query):
		biteInfo.append([bite.replace("&#39;", "'"), fake.name()])
	print biteInfo
	sectorData = Share(SECTORS[sector])
	sectorName = SECTORS[sector]
	GList = drawGraphs(query, queryData, sector, sectorData)
	return render_template('profile.html', sector=sector,
		industry=industry, name=name, query=query, sectorName=sectorName,
		queryData=queryData, sectorData=sectorData, G=GList, biteInfo = biteInfo[:10])

#==================================================================================================================================
# MAIN FUNCTIONS
#==================================================================================================================================

#run the main methods
if __name__ == "__main__":
	app.run()

#==================================================================================================================================
#
#==================================================================================================================================