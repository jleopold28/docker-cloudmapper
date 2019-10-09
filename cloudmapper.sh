#!/bin/bash

# set -e
echo "Runnning Cloudmapper.sh"

echo "Copying S3 config.json file to container..."
aws s3 cp s3://$S3_BUCKET/config.json config.json
echo "S3 Copy successful!"

echo "config.json: "
cat config.json

echo "Running cloudmapper.py collect on $ACCOUNT"
pipenv run python cloudmapper.py collect --account $ACCOUNT

echo "Running cloudmapper.py report on $ACCOUNT"
pipenv run python cloudmapper.py report --account $ACCOUNT

echo "Running cloudmapper.py public scan on $ACCOUNT"
pipenv run python cloudmapper.py public --account $ACCOUNT > $ACCOUNT.json

echo "Running check on bad ports for $ACCOUNT"
pipenv run python find-bad-ports.py

echo "$ACCOUNT.json: "
cat $ACCOUNT.json

echo "$ACCOUNT.csv: "
cat $ACCOUNT.csv

# echo "Report.html: "
# send to sns email?
# cat web/account-data/report.html

# Alert pagerduty on critical
#$PD_SERVICE_KEY
# Alert pagerduty on warning

echo "done!"

# Send $runtime to cloudmapper.runtime 
#$DATADOG_API_KEY