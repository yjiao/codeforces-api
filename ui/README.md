# Custom User Profiles

The scripts in this folder creates individualized user profiles similar to those found [here](http://codeforces.com/blog/entry/46304). In this bare bones version, plots are made in R and aggregated in a HTML page.


## Usage
```
chmod +x createReport.sh
```
Generate report:

```
./createReport.sh -n --handle=yourCodeforcesHandle
```

View report:

```
open report.html
```

This will automatically update problem and user data, if new problems have been published on codeforces between runs. Note calculating problem ratings can be a bit slow depending on the number of contests elapsed between runs--this is limited by the speed of codeforces api. Usually tens of competitions will run in a few minutes.

## History
2016 08 18: barebones version uploaded.