#! /bin/sh
#set -ex


D=src/edgarquery

for i in cikperson.py \
    companyconcepttocsv.py \
    companyfactsshow.py \
    companyfactstocsv.py \
    companyfactsziptocsv.py \
    doquery.py \
    latest10K.py \
    latestsubmissions.py \
    submissions.py \
    submissionsziptocsv.py \
    tickerstocsv.py \
    xbrlframestocsv.py; do
     echo
     f=$(echo $i | cut -f1 -d.)
     echo '##'
     echo "## $f"
     echo '##'
     python $D/$i -h
     echo
done | while read line; do
    echo "$line<br/>"
done | sed 's/[.]py//'

