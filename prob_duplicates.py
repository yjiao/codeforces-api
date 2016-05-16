import os
import re
import sys
import time
import requests
import pandas as pd

from collections import defaultdict

import api_functions as af

def mergeDuplicateProblems(outfile, clist = None):
    df = pd.DataFrame({})

    calls = 0

    if clist is None:
        clist = af.getContestList()

    for cid in clist:
        probdf = af.getProblemDataFromContest(cid)
        df = df.append(probdf)

        calls += 1
        if calls % 5 == 0:
            sys.stderr.write('Got problem info for contest ' + str(cid) + '\n')
            sys.stderr.flush()
            time.sleep(1)

    dup = defaultdict(list)

    for _, r in df.iterrows():
        name = r['name']
        startTimeSeconds = r['startTimeSeconds']

        tdf = df[(df.name == name) & (df.startTimeSeconds == startTimeSeconds)]

        if tdf.shape[0] > 1:
            tdf = tdf.sort(['division'])

            dup['contestID'].append(r['contestID'])
            dup['problemID'].append(r['index'])
            dup['refContestID'].append(tdf['contestID'].iloc[0])
            dup['refProblemID'].append(tdf['index'].iloc[0])

    dupdf = pd.DataFrame(dup)
    dupdf.to_csv(outfile, index=False)

