import json
import pickle
from datetime import datetime
import scipy.stats as sci
import numpy as np
import pandas as pd
import requests

cookie = {'steamLoginSecure': ''}

with open('730_names.txt', 'rb') as file:
    allItemnames = pickle.load(file) # retrieve the items

allItemsPd = pd.DataFrame(data=None, index=None,
                          columns=['itemName', 'initial', 'timeOnMarket', 'priceIncrease', 'priceAvg', 'priceSD',
                                   'maxPrice', 'maxIdx', 'minPrice', 'minIdx', 'swing', 'volAvg', 'volSD', 'slope',
                                   'rr'])
currRun = 0 # current item
for currItem in allItemnames:
    try:
        params = {
            'appid' : 730,
            'market_hash_name' : currItem
        }
        items = requests.get(
            'https://steamcommunity.com/market/pricehistory/',
            cookies=cookie, params=params) # get the entire history of the item

        item = json.loads(items.text)
        currRun += 1
        print(str(currRun),' out of ',str(len(allItemnames))+' code: '+str(items.status_code), item['prices'][0])
        # Steam doesn't give microbans for getting history, so you don't have to worry about it
        itemPriceData = item['prices'] # get the price, time, quantity (steam averages the price for the time given)
        itemPrices = []
        itemVol = []
        itemDate = []
        for currDay in itemPriceData:
            itemPrices.append(currDay[1]) # getting a price
            itemVol.append(currDay[2]) # getting a quantity
            itemDate.append(datetime.strptime(currDay[0][0:11], '%b %d %Y')) # getting a time

            itemPrices = list(map(float, itemPrices))
            itemVol = list(map(int, itemVol))

        for currDay in range(len(itemDate)-1, 1, -1): # Steam for the last month gives data for every hour, we'll
            if itemDate[currDay] == itemDate[currDay-1]: # average everything for every day
                itemPrices[currDay-1] = np.mean([itemPrices[currDay], itemPrices[currDay-1]])
                itemVol[currDay-1] = np.sum([itemPrices[currDay], itemPrices[currDay-1]])
                itemDate.pop(currDay)
                itemVol.pop(currDay)
                itemPrices.pop(currDay)

        normTime = list(range(len(itemDate))) # Let's convert everything to number of days, it's
                                              # easier to work with than datetime
        timeOnMarket = (datetime.today()-itemDate[0]).days # number of days since the first sale
        priceIncrease = itemPrices[-1] - itemPrices[0] # the difference between the first day's price and
                                                       # the current day's price
        maxPrice = max(itemPrices)
        maxIdx = itemPrices.index(maxPrice) # when was the maximum price?
        minPrice = min(itemPrices)
        minIdx = itemPrices.index(minPrice)
        swing = maxPrice - minPrice # highest price range

        # obtain descriptive statistics
        itemPriceAvg = np.mean(itemPrices) # average price
        if len(itemPrices) > 1: # if two days + sales
            itemPriceInitial = itemPrices[1] - itemPrices[0] # How much did the price jump from day 0 to day 1?
                                                            # For example, on the first trading day.
        else:
            itemPriceInitial = itemPrices[0]
        itemVolAvg = np.mean(itemVol) # average quantity
        itemPriceSD = np.std(itemPrices) # standard deviation of price
        # Linear regression to find the slope and fit
        itemVolSD = np.std(itemVol) # Slope intercept rvalue pvalue stderr
        fitR = sci.linregress(normTime, itemPrices)
        rr = float(fitR[2] ** 2)
        # Save data
        currItemDict = {'itemName': currItem, 'initial': itemPriceInitial, 'timeOnMarket': timeOnMarket,
                           'priceIncrease': priceIncrease, 'priceAvg': itemPriceAvg, 'priceSD': itemPriceSD,
                           'maxPrice': maxPrice, 'maxIdx': maxIdx, 'minPrice': minPrice, 'minIdx': minIdx,
                           'swing': swing, 'volAvg': itemVolAvg, 'volSD': itemVolSD, 'slope': fitR[0], 'rr': rr}
        currItemPD = pd.DataFrame(currItemDict, index=[0])
        allItemsPD = allItemsPd._append(currItemPD, ignore_index=True)
    except:
        print(items.text)

print('All item data collected')
allItemsPD.to_pickle('730'+'PriceData.pkl') # Save the dataframe
