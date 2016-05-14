#!/usr/bin/env python

import math
import argparse

import numpy as np
import pandas as pd

import api_functions as af

from collections import defaultdict

MINRATING = 0.0
MAXRATING = 5000.0

MAXITER = 20

def readCL():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--contestID")

    args = parser.parse_args()
    return args.contestID

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
        problem_df["problemRating"] = mid 
        expSolve = np.sum(problem_df.apply(process_row, axis = 1))

        if solveCnt > expSolve:
            hi = mid
        else:
            lo = mid

    return int(round((lo + hi) / 2.0))

def get_contest_elo(contestID):
    contest_df = af.getSolveSuccessDF(contestID)

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
    contestID = readCL()
    print get_contest_elo(contestID)
