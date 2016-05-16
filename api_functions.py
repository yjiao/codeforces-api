# coding: utf-8

# # Contest Parser v1
# Goal is to return the following table
#  
# handle | rating | contestID | problemID | success 
# --- | --- | --- | --- | --- | ---
# handle0 | 1234 | 633 | A | 1
# handle0 | 1234 | 633 | B | 1
# handle0 | 1234 | 633 | C | 0
# 

import os
import re
import sys
import time
import requests
import pandas as pd

from collections import defaultdict

def getProblemDataFromContest(contestID):
    url = 'http://codeforces.com/api/contest.standings?contestId=' + str(contestID) + '&from=1&count=1'
    r = requests.get(url).json()['result']

    contest = r['contest']['name']
    startTimeSeconds = r['contest']['startTimeSeconds']

    isD1 = False
    isD2 = False

    for d1key in ['Div. 1', 'Div.1']:
        if d1key in contest:
            isD1 = True
    for d2key in ['Div. 2', 'Div.2']:
        if d2key in contest:
            isD2 = True

    problems = r['problems']
    probdf = pd.DataFrame.from_dict(problems)

    probdf['contestID'] = contestID
    probdf['contestName'] = contest
    probdf['startTimeSeconds'] = startTimeSeconds

    probdf['division'] = 12
    if isD1 and not isD2: probdf['division'] = 1
    if isD2 and not isD1: probdf['division'] = 2

    return probdf

def getSolveSuccessDF(contestID):
#contestID = 671
    urlbase = 'http://codeforces.com/api/'
    method = 'contest.standings'
    maxcnt = 100000
    #http://codeforces.com/api/contest.standings?contestId=566&from=1&count=5&showUnofficial=true
    url = urlbase + method + '?contestId=' + str(contestID) + '&from=1&count=' + str(maxcnt) + '&showUnofficial=false'
    r = requests.get(url).json()['result']
    rows = r['rows']
    problems = r['problems']
    contest = r['contest']

    # CHECK TO MAKE SURE THAT TEAMS ARE NOT ALLOWED!!!
    for r in rows: # for each person
	if len(r['party']['members']) > 1:
	    raise Error("This contest allows teams. ELO scores are not well-defined.")

    users = []
    points = []
    for r in rows:
	users.append(r['party']['members'][0]['handle'])
	
	userpts = [0]*len(problems)
	for i in range(len(problems)):
	    userpts[i] = r['problemResults'][i]['points']
	points.append([1 if u > 0 else 0 for u in userpts])


    # Grab rating changes
    method = 'contest.ratingChanges'
    url = urlbase + method + '?contestId=' + str(contestID)
    ratingchanges = requests.get(url).json()['result']
    ratingdict = dict()
    for r in ratingchanges:
	ratingdict[r['handle']] = r['oldRating']


    # Create output df 
    # start constructing dataframe
    array_out = []
    for i in range(len(users)): # for each user in the contest
	hdl = users[i]
	rating = ratingdict[hdl]
	for j, p in enumerate(problems): # for each problem in the contest, make a new row
	    temp = dict.fromkeys(['handle', 'rating', 'contestID', 'problemID', 'success'])
	    temp['handle'] = hdl
	    temp['contestID'] = contestID
	    temp['problemID'] = p['index']
	    temp['success'] = points[i][j]
	    temp['rating'] = rating
	    array_out.append(temp)

    output = pd.DataFrame.from_dict(array_out)
    return output

def getContestList():
    url_contest = 'http://codeforces.com/api/contest.list?gym=false'
    r = requests.get(url_contest) #ther eare some issues with Russian letters in contest names

    contests = r.json()['result']
    df_contests = pd.DataFrame.from_dict(contests)
    return list(df_contests.loc[df_contests.phase == 'FINISHED']['id'])





