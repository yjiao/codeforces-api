#!/usr/bin/env python

import sys
from os.path import isfile
import math
import argparse

import numpy as np
import pandas as pd

import api_functions_v2 as af

from collections import defaultdict

MINRATING = 0.0
MAXRATING = 5000.0

MAXITER = 20
pd.options.mode.chained_assignment = None

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--contestID", default="0", type=str, help="ID of contest to query. A default value of 0 calculates problem ratings for all competitions.")
    parser.add_argument("-o", "--outputFile", default="problem_elos.csv", type=str, help="Name of output file.")
    parser.add_argument("-f", "--forceUpdate", action='store_true', help="Overwrite previous file containing problem ratings, if exists.")

    args = parser.parse_args()
    return args

def get_win_prob(ri, rj): # probability that rating ri beats rating rj
    return 1.0 / (1.0 + math.pow(10, (rj-ri) / 400.0))

def process_row(r):
    return get_win_prob(r["rating"], r["problemRating"])

def get_problem_elo(problem_df):
    rowCnt = problem_df.shape[0]
    solveCnt = np.sum(problem_df.success)

    lo = MINRATING
    hi = MAXRATING

    for i in range(MAXITER):
        mid = (lo + hi) / 2.0
        #expSolve = np.sum(problem_df.apply(process_row, axis = 1))
        expSolve = np.sum(problem_df.rating.apply(lambda x: get_win_prob(x, mid)))

        if solveCnt > expSolve:
            hi = mid
        else:
            lo = mid

    return int(round((lo + hi)/ 2.0))

def get_contest_elo(contestID):
    try:
        contest_df = af.getSolveSuccessDF(contestID)
    except Exception as e:
        with open('bad_contests.txt', 'a') as f:
          f.write(str(contestID) + '\n')
        return None
  
    if contest_df.shape[0] < 50:
        with open('bad_contests.txt', 'a') as f:
          f.write(str(contestID) + '\n')
        return None

    contestID = contest_df.contestID.unique()[0]
    uniqProbs = contest_df.problemID.unique()

    data = defaultdict(list)

    for pi in uniqProbs:
        pe = get_problem_elo(contest_df[contest_df.problemID == pi]) 

        data["contestID"].append(contestID)
        data["problemID"].append(pi)
        data["problemRating"].append(pe)

    return pd.DataFrame(data)

def get_win_prob(ri, rj): # probability that rating ri beats rating rj
    return 1.0 / (1.0 + math.pow(10, (rj-ri)/400.0))

if __name__ == "__main__":
    args = readCL()
    contestID = args.contestID
    
    # file handling: figure out if user wants to append or not
    if isfile(args.outputFile):
	if args.forceUpdate:
	    sys.stderr.write(args.outputFile + " found, -f flag set, overwriting...\n")
	    fh = open(args.outputFile, 'w')
	else:
	    sys.stderr.write(args.outputFile + " found, opening in append mode...\n")
	    fh = open(args.outputFile, 'a')
    else:
	sys.stderr.write(args.outputFile + " not found, creating new file...\n")
	fh = open(args.outputFile, 'w')

    if contestID != "0": # calculate problem ratings for a specific competition
        df = get_contest_elo(contestID)
	df.to_csv(fh, header=True, index=False)

    else: # calculate problem ratings for all currently available contests

        for cid in af.getContestList():
            sys.stderr.write("Calculating ELO for contest " + str(cid) + ".\n")

            contest_elos = get_contest_elo(cid)

            if contest_elos is not None:
		contest_elos.to_csv(fh, header=True, index=False)
                sys.stderr.write("Got " + str(contest_elos.shape[0]) + " new rows.\n")

            sys.stderr.flush()

