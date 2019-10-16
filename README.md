# docker-cloudmapper

A Docker container that has [cloudmapper](https://github.com/duo-labs/cloudmapper) installed.

## Public port checking
This container also has python files to support checking for publicly acceisible ports. The port checking is done by reading the `$ACCOUNT.json` file.  


## AWS SES Email functionality
Email funcionality is provided through AWS SES. This required a registed domain with AWS SES to use as the email sender.  

## Environment variables
The python scripts for public port checks and email sending use environment varaibles. The following varaibles must be set for the scripts to work.
```
S3_BUCKET:       AWS S3 bucket location for config.json file
ACCOUNT:         AWS account name
AWS_REGION:      AWS region where the SES client is created.
DATADOG_API_KEY: required for Datadog monitoring
PD_SERVICE_KEY:  PagerDuty service key for alerts
OK_PORTS:        List of acceptable public ports in string format (example "80,443")
SES_ENABLED:     Whether SES email sending is enabled ("true" to enable)
SES_SENDER:      email address that sends SES emails
SES_RECIPIENT:   email address of recipients
```

## Example usage
This is designed to be used with cloudmapper.
```
pipenv run python cloudmapper.py collect --account $ACCOUNT
pipenv run python cloudmapper.py public --account $ACCOUNT > $ACCOUNT.json
pipenv run python /opt/cloudmapper/run_port_check.py
pipenv run python /opt/cloudmapper/send_email.py
```
