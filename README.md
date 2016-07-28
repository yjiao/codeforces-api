# Problem Ratings for Codeforces

[Codeforces](codeforces.com) is a well-known community for algorithms competitions. There are several heuristics that exist for finding suitable practice problems on Codeforces (sorting by the total number of solvers, for example), but none of them perform well and consistently in practice. We decided to create a better measure of problem difficulty, which we’ll call “problem rating”. You can read more about problem rating on our blog post [here].


## Functions
**api_functions.py** contains functions to parse information using APIs provided by codeforces.

**elo.py** was used to calculate problem ratings.

**blogPost_v1.ipynb** is a jupyter/iPython notebook that contains Python and R scripts used to generate figures for our first blog post.

**prob_duplicates.py** identifies probable duplicated problems.


## Files
**problem_duplicates.csv** A list of duplicated problems between Div. 1 and Div. 2.
**problem_ratings.csv**	Problem ratings from elo.py.
**rating_histories.csv** Rating history of active users who competed in at least 15 competitions.

