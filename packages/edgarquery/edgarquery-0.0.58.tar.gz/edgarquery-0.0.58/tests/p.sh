#! /bin/bash
set -ex

echo $EQDIR
echo $EQODIR
PD=src/edgarquery

# big files
# python ${PD}/edgarquery.py --companyfactsarchivezip \
#                                             --cik 1018724
# python ${PD}/edgarquery.py --submissionszip
#python ${PD}/edgarquery.py --submissionszip
#sleep 5

python ${PD}/edgarsubmissionsziptocsv.py --zipfile $EQODIR/submissions.zip \
    --files CIK0000831001.json,CIK0001665650.json,CIK0000019617.json

# SEC needs a user-agent
curl --user-agent $EQEMAIL --output /private/tmp/sitemap.xml \
     https://www.sec.gov/Archives/edgar/daily-index/sitemap.xml
curl --user-agent $EQEMAIL --output /private/tmp/company_tickers.json \
     https://www.sec.gov/files/company_tickers.json
for f in company.idx crawler.idx form.idx master.idx \
         xbrl.idx sitemap.quarterlyindexes.xml; do
    curl --user-agent $EQEMAIL --output $EQODIR/$f \
         https://www.sec.gov/Archives/edgar/full-index/$f
done


#for cik in 1318605 1018724 1045810; do
for ticker in tsla amzn nvda; do
    #python ${PD}/edgarquery.py --companyfacts --cik $cik
    python ${PD}/edgarquery.py --companyfacts --ticker $ticker
done

for fct in AccountsPayableCurrent EarningsPerShareBasic; do
    python ${PD}/edgarquery.py --companyconcept --ticker tsla --fact $fct
    python ${PD}/edgarquery.py --companyconcept --ticker amzn --fact $fct
    python ${PD}/edgarquery.py --companyconcept --ticker nvda --fact $fct
done

for fct in AccountsPayableCurrent AssetsCurrent DebtCurrent \
    LongTermDebt ; do
    for CY in CY2009Q2I CY2023Q1I CY2023Q2I CY2023Q3I; do
        echo $CY
        python ${PD}/edgarquery.py --xbrlframes --cy $CY --fact $fct
    done
done

for F in $(ls $EQODIR/CompanyFacts*.json |xargs basename); do
    echo $F
    python ${PD}/edgarcompanyfactstocsv.py --file $EQODIR/$F --directory $EQODIR
done

for F in $(ls $EQODIR/CompanyConcept*.json |xargs basename); do
    echo $F
    python ${PD}/edgarcompanyconcepttocsv.py --file $EQODIR/$F --directory $EQODIR
done

for F in $(ls $EQODIR/XBRLFrames*.json |xargs basename); do
    echo $F
    python ${PD}/edgarxbrlframestocsv.py --file $EQODIR/$F --directory $EQODIR
done

#python ${PD}/edgarsubmissionszipṫocsv.py --zipfile $EQODIR/submissions.zip --all


#for cik in 5981 1318605 1018724 1045810; do
for ticker in tsla amzn orcl tm; do
    #python ${PD}/edgarsubmissions.py --cik $cik
    #python ${PD}/edgarsubmissions.py --cik $cik --year 2022
    python ${PD}/edgarsubmissions.py --ticker $ticker
    python ${PD}/edgarsubmissions.py --ticker $ticker --year 2022
done

python ${PD}/edgartickerstocsv.py

##############################################################################
exit
##############################################################################



