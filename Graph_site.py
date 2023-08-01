import json
import random
import time
import requests
import pickle


cookies = {'steamLoginSecure': ''} # we set a steam cookie.
games = ['730'] # game id cs-go

for gameID in games:
    AllItemNames = []
    AllItemsGet = requests.get(
        'https://steamcommunity.com/market/search/render/?search_descriptions=0&sort_column=default&sort_dir=desc&appid=' + gameID + '&norender=1&count=100',
        cookies=cookies)

    AllItems = AllItemsGet.content
    AllItems = json.loads(AllItems)

    totalItems = AllItems['total_count'] # amount of stuff in the game
    print(totalItems)

count = 0
for currPos in range(0, totalItems + 50, 50): # going through every 50 items
    checking = True
    while checking:
        allItemsGet = requests.get('https://steamcommunity.com/market/search/render/?start=' + str(currPos) +
                                   '&count=100&search_descriptions=0&sort_column=default&sort_dir=desc&appid=' + gameID + '&norender=1&count=5000',
                                   cookies=cookies) # Even though we flip every 50 items, we always get 100, this is
                                                    # done so that steam changes the location of things quite often.
        print('try', currPos)
        Items = allItemsGet.text
        Items = json.loads(Items)
        if Items['results'] == []:             # Steam may eventually start issuing micro-bans, so
            print('results 0 refresh', currPos)   # if we get an empty json, we'll do the same request again
            continue
        checking = False


    count += 1
    allItems = Items['results']
    print('Items ' + str(currPos) + ' out of ' + str(totalItems) + ' code: ' + str(AllItemsGet.status_code) + ' ' + str(
        count)) # if all is well, then we do the print.
    for currItem in allItems:
        AllItemNames.append(currItem['hash_name']) # add all the items we've found

allItemmames = list(set(AllItemNames)) # kick duplicate items
print(allItemmames)
print(len(allItemmames))
with open(gameID + '_names.txt', "wb") as file:
    pickle.dump(allItemmames, file) # save all the items we find
