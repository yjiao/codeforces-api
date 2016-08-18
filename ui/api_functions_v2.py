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

# first, we need to define error classes to check the status of querying
class ContestAllowsTeams(Exception):
    def __init__(self, contestID):
        self.contestID = contestID
    def __str__(self):
        return repr(self.contestID)
class ContestNotFound(Exception):
    def __init__(self, contestID):
        self.contestID = contestID
    def __str__(self):
        return repr(self.contestID)
class UserNotFound(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
class ContestUnrated(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def getProblemDataFromContest(contestID):
    url = 'http://codeforces.com/api/contest.standings?contestId=' + str(contestID) + '&from=1&count=1'
    
    r = requests.get(url).json()
    
    if r['status'] == 'FAILED':
	expectedMessage = 'contestId: Contest with id ' + str(contestID) + ' not found'
	if r['comment'] == expectedMessage:
	    raise ContestNotFound(contestID)

    r = r['result']
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

def getUserActivity(handle):
    # Unfortunately there doesn't seem to be a way to get only the new entries, and we shouldn't make any assumptions on how many new entries there has been since the user last updated. So each time we need to re-write the dataframe.
    maxcount = '100000000'
    url = 'http://codeforces.com/api/user.status?handle=' + handle + '&from=1&count=' + maxcount

    r = requests.get(url).json()
    if r['status'] == 'FAILED':
	expectedMessage = 'handle: User with handle ' + str(handle) + ' not found'
	if r['comment'] == expectedMessage:
	    raise UserNotFound(handle)

    dictlist = []
    keys = ['testset', 'passedTestCount', 'author', 'relativeTimeSeconds', 
	    'language', 'memoryBytes', 'timeMilliseconds', 'problem_name', 'problem_index',
	    'problem_tags', 'points', 'contestID', 'verdict', 'id', 'participantType', 'startTimeSeconds']

    r = r['result']
    for rr in r:
	temp = dict.fromkeys(keys)
	temp['author'] = rr['author']['members'][0]['handle']
	temp['startTimeSeconds'] = rr['creationTimeSeconds']

	if 'startTimeSeconds' not in rr['author']:
	    temp['participantType'] = 'GYM'
	else:
	    temp['participantType'] = rr['author']['participantType']

	temp['id'] = rr['id']
	temp['verdict'] = rr['verdict']
	temp['contestID'] = rr['contestId']

	if 'points' not in rr['problem']:
	    temp['points'] = 0
	else:
	    temp['points'] = rr['problem']['points']

	temp['problem_tags'] = rr['problem']['tags']
	temp['problem_index'] = rr['problem']['index']
	temp['problem_name'] = rr['problem']['name']
	temp['timeMilliseconds'] = rr['timeConsumedMillis']
	temp['memoryBytes'] = rr['memoryConsumedBytes']
	temp['language'] = rr['programmingLanguage']
	temp['relativeTimeSeconds'] = rr['relativeTimeSeconds']
	temp['passedTestCount'] = rr['passedTestCount']
	temp['testset'] = rr['testset']

	dictlist.append(temp)
    df_userActivity = pd.DataFrame.from_dict(dictlist)
    return df_userActivity

def getUserRatingHistory(handle):
    url = 'http://codeforces.com/api/user.rating?handle=' + handle

    r = requests.get(url).json()
    if r['status'] == 'FAILED':
	expectedMessage = 'handle: User with handle ' + str(handle) + ' not found'
	if r['comment'] == expectedMessage:
	    raise UserNotFound(handle)

    r = r['result']
    rating_history = pd.DataFrame.from_dict(r)
    return rating_history

