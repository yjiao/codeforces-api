#!/bin/bash

# usage examples
#./createReport.sh -n --handle=yj12

# Note not all the command line options for ui_functions are being used right now, for first pass there's no reason to have non-standard file names

update=true

for i in "$@"
do
    case $i in
	-u=*|--handle=*)
	    handle="${i#*=}"
	    shift # past argument=value
	    ;;
	-n|--noUpdate)
	    update=false
	    shift # past argument, no value
	    ;;
	*)
	    #unknown option
	    echo "option not found"
	    ;;
    esac
done


if [ -z $handle ] && $update
then
    echo "Update selected, but no user handle was given. Please use -u=... or --handle=... to supply user handle to this function."
    exit
fi

echo "================================================================="
echo "Creating report for $handle, update = $update..."

if $update
then
    echo "0. Updating data required for creating plots..."
    python ui_functions.py -u $handle
fi

echo "1. Checking that all required csv files exist..."

arr=("problem_data.csv" "problem_ratings.csv" "user_activity.csv" "user_rating.csv")
for fileName in "${arr[@]}"
do
    if [ ! -e $fileName ]
    then
	echo "   $fileName not found. Please call this function without the -n flag to update required csv files"
	exit
    else
	echo "   $fileName found"
    fi

done


echo "2. Creating plots..."
Rscript makePlots.R

echo "Profile completed. Please open report.html to view your profile."

