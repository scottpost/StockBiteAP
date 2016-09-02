import bs4

# SEEKING ALPHA 
url = urllib.urlopen("http://seekingalpha.com/symbol/AAPL/stocktalks")
soup = BeautifulSoup(url)
message = soupComment.find("div", attrs={"class":"conent_cnt"}).text
print message