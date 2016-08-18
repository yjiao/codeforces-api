# Custom User Profiles

The scripts in this folder creates individualized user profiles similar to those found [here](http://codeforces.com/blog/entry/46304). In this bare bones version, plots are made in R and aggregated in a HTML page.

## Requirements
- R (scripts were written under version 3.2.4)
- Python 2.7

## Usage
```
chmod +x createReport.sh
```
Generate report:

```
./createReport.sh -n --handle=yourCodeforcesHandle
```
Example script output:
```
=================================================================
Creating report for yj12, update = true...
0. Updating data required for creating plots...
   ------------------------------------
   Updating problem ratings file: problem_ratings.csv
   Problem ratings file up to date.
   ------------------------------------
   Updating problem data file: problem_data.csv
   Problem ratings file up to date.
   ------------------------------------
   Getting all user problem submission information for: yj12
   ------------------------------------
   Getting user rating history for: yj12
1. Checking that all required csv files exist...
   problem_data.csv found
   problem_ratings.csv found
   user_activity.csv found
   user_rating.csv found
2. Creating plots...
There were 50 or more warnings (use warnings() to see the first 50)
Warning messages:
1: In max(df$problemRating) :
  no non-missing arguments to max; returning -Inf
2: In max(df$problemRating) :
  no non-missing arguments to max; returning -Inf
null device 
          1 
null device 
          1 
null device 
          1 
null device 
          1 
null device 
          1 
Profile completed. Please open report.html to view your profile.

```


View report:

```
open report.html
```

This will automatically update problem and user data, if new problems have been published on codeforces between runs. Note calculating problem ratings can be a bit slow depending on the number of contests elapsed between runs--this is limited by the speed of codeforces api. Usually tens of competitions will run in a few minutes.

## History
2016 08 18: barebones version uploaded.