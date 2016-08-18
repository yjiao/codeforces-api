#!/usr/bin/env python
from os.path import isfile
import re
import sys
import requests
import pandas as pd
import argparse

import api_functions_v2 as api
import elo as elo

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("-ii", "--inputDataFile", default="problem_data.csv", type=str, help="Name of input problem data file.")
    parser.add_argument("-ir", "--inputRatingFile", default="problem_ratings.csv", type=str, help="Name of input problem ratings file.")
    parser.add_argument("-oi", "--outputDataFile", default="problem_data.csv", type=str, help="Name of output problem data file.")
    parser.add_argument("-or", "--outputRatingFile", default="problem_ratings.csv", type=str, help="Name of output problem data file.")
    parser.add_argument("-oua", "--outputUserActivityFile", default="user_activity.csv", type=str, help="Name of output user activity file.")
    parser.add_argument("-our", "--outputUserRatingFile", default="user_rating.csv", type=str, help="Name of output user rating history file.")
    parser.add_argument("-u", "--handle", default="", type=str, help="User handle on codeforces.")
    parser.add_argument("-f", "--forceUpdate", action='store_true', help="Overwrite previous file containing problem ratings, if exists.")

    args = parser.parse_args()
    return args

def updateProblemData(prevFile, newFile, force):
    """
    Update problem_data.csv
    prevFile: name of local file containing problem data
    newFile: name of new file name with new problem data. Should be set to be the same as the prevFile for appending, unless currently debuggin
    """
    df_prev = pd.DataFrame.from_csv(prevFile, index_col=None)
    
    cur_contests = api.getContestList()
    max_prev_contests = max(df_prev.contestID)
    
    new_contests = [c for c in cur_contests if c > max_prev_contests]
    
    dflist = []
    cnt = 0
    for contestID in new_contests:
	print "   contest", contestID
        try:
            contestProblems = api.getProblemDataFromContest(contestID)
            contestProblems = contestProblems.rename(index=str, columns={'index': 'problemID'})
            contestProblems = contestProblems.drop('contestId', 1)
            dflist.append(contestProblems)
            cnt += 1
        except api.ContestNotFound:
            sys.stderr.write(str(contestID) + ', api returned contest not found error.')
    
    if not dflist:
	print "   Problem ratings file up to date."
	return
    problemData = pd.concat(dflist)
    writeFile(problemData, newFile, force)
    sys.stderr.write("Successfully wrote problem data from " + str(cnt) + " contests.")

def updateProblemRating(prevFile, newFile, force):
    """
    Update problem_ratings.csv
    prevFile: name of local file containing problem ratings.
    newFile: name of new file name with new problem ratings. Should be set to be the same as the prevFile for appending, unless currently debuggin
    """
    df_prev = pd.DataFrame.from_csv(prevFile, index_col=None)
    
    cur_contests = api.getContestList()
    max_prev_contests = max(df_prev.contestID)
    
    new_contests = [c for c in cur_contests if c > max_prev_contests]
    
    dflist = []
    cnt = 0
    for contestID in new_contests:
	print "   contest", contestID
	df = elo.get_contest_elo(contestID)
	dflist.append(df)
	cnt += 1

    if not dflist:
	print "   Problem ratings file up to date."
	return
    problemRatings = pd.concat(dflist)
    writeFile(problemRatings, newFile, force)
    sys.stderr.write("Successfully wrote problem data from " + str(cnt) + " contests.")

def writeFile(data, outFile, force):
    # note: we can't just return a file handle here, although that would be more efficient. This is because whether we write the header or not is dependent on whether we are appending.
    # file handling: figure out if user wants to append or not
    if isfile(outFile):
	if force:
	    sys.stderr.write(outFile + " found, -f flag set, overwriting...\n")
	    fh = open(outFile, 'w')
	    data.to_csv(fh, encoding='utf-8', index=None, header=True)
	else:
	    sys.stderr.write(outFile + " found, opening in append mode...\n")
	    fh = open(outFile, 'a')
	    data.to_csv(fh, encoding='utf-8', index=None, header=False)
    else:
	sys.stderr.write(outFile + " not found, creating new file...\n")
	fh = open(outFile, 'w')
	data.to_csv(fh, encoding='utf-8', index=None, header=True)


if __name__ == '__main__':
    args = readCL()
    
    print '   ------------------------------------'
    print "   Updating problem ratings file:", args.inputRatingFile
    updateProblemRating(args.inputRatingFile, args.outputRatingFile, args.forceUpdate)

    print '   ------------------------------------'
    print "   Updating problem data file:", args.inputDataFile
    updateProblemData(args.inputDataFile, args.outputDataFile, args.forceUpdate)

    print '   ------------------------------------'
    print "   Getting all user problem submission information for:", args.handle
    # always overwrite
    try:
	df_user = api.getUserActivity(args.handle)
	df_user.to_csv(args.outputUserActivityFile, header=True, index=None, encoding='utf-8')
    except api.UserNotFound:
	print "   **********************************************"
	print "   ERROR: FAILED TO UPDATE USER ACTIVITY LIST."
	print "   User with handle", args.handle, "was not found at codeforces. Please double check to make sure the handle was entered correctly."

    print '   ------------------------------------'
    print "   Getting user rating history for:", args.handle
    # always overwrite
    try:
	df_ratinghistory = api.getUserRatingHistory(args.handle)
	df_ratinghistory.to_csv(args.outputUserRatingFile, header=True, index=None, encoding='utf-8')
    except api.UserNotFound:
	print "   **********************************************"
	print "   ERROR: FAILED TO UPDATE USER ACTIVITY LIST."
	print "   User with handle", args.handle, "was not found at codeforces. Please double check to make sure the handle was entered correctly."
