# docker-cloudmapper

A Docker container that has cloudmapper downloaded. This container also has python files to support checking
for publicly acceisible ports. The port checking is done by checking the `$ACCOUNT.json` file.


## Example usage
This is designed to be used with cloudmapper.
```
pipenv run python cloudmapper.py collect --account $ACCOUNT
pipenv run python cloudmapper.py public --account $ACCOUNT > $ACCOUNT.json
pipenv run python /opt/cloudmapper/run_port_check.py
```
