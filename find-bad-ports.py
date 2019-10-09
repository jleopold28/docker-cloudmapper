#!/usr/bin/env python

import os
import json
import sys
import subprocess
import csv
import pandas
import logging
import urllib3
from pandas.io.json import json_normalize

logger = logging.getLogger(__name__)

def get_bad_ports(ports):
    # 943 = tuckernet 
    # 1194 = tuckernet udp
    ok_ports = ['80','443','8080','943','1194']
    bad_ports = []
    for port in ports:
        if port not in ok_ports:
            bad_ports.append(port)
    return bad_ports

def test_each_port(host,ports):
    bad_ports = []
    for port in ports:
        if "-" in port:
            bad_ports.append(port)
            continue

        cmd = ['nc','-w','1','-vz',host,port]

        pipes = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        std_out, std_err = pipes.communicate()

        if pipes.returncode != 0:
            # connection refused means the port is defined, but no process is listening
            # and that is bad...
            if 'refused' not in std_err:
                continue
        bad_ports.append(port)

    return bad_ports

def send_event(pd_url, service_key, payload):
    """
    Send an event to PagerDuty.
    :param service_key: service key to send to
    :type service_key: str
    :param payload: data to send with event
    :type payload: dict
    """
    payload['service_key'] = service_key
    http = urllib3.PoolManager()
    logger.info(
        'POSTing to PagerDuty Events API (%s): %s', pd_url, payload
    )
    encoded = json.dumps(payload, sort_keys=True).encode('utf-8')
    resp = http.request(
        'POST', pd_url,
        headers={'Content-type': 'application/json'},
        body=encoded
    )
    if resp.status == 200:
        logger.debug(
            'Successfully POSTed to PagerDuty; HTTP %d: %s',
            resp.status, resp.data
        )
        return
    raise RuntimeError(
        'ERROR creating PagerDuty Event; API responded HTTP %d: %s' % (
            resp.status, resp.data
        )
    )
            
# Set variables from env
account_name    = os.getenv('ACCOUNT')
filename_in     = account_name + '.json'
service_key     = os.getenv('PD_SERVICE_KEY')

# Setup Pagerduty
pd_url = 'https://events.pagerduty.com/generic/2010-04-15/create_event.json'
incident_key = 'cloudmapper-' + account_name
event_data = {
    'incident_key': incident_key,
    'client': 'cloudmapper'
}

sys.stdin = open(filename_in, 'r')

with sys.stdin as data:
    csv_filename = account_name + '.csv'

    json_data = json.load(data)
    df = json_normalize(json_data)
    df = df[['account', 'type', 'hostname', 'ports', 'arn']]
    csv_data = df.to_csv(csv_filename,header=False, index=False)

    with open(csv_filename) as csv_file:
        lines = csv.reader(csv_file, delimiter=',')
        for line in lines:
            account = line[0]
            aws_type = line[1]
            hostname = line[2]
            port_list = line[3]
            arn = line[4]
            #print "%s,%s,%s,%s,%s" % (account,aws_type,hostname,port_list,arn)
        
            ports = port_list.split(',')
        
            bad_ports = get_bad_ports(ports)
            bad_ports = test_each_port(hostname,bad_ports)
            bad_ports = ",".join(bad_ports)
        
            if bad_ports:
                print("%s\t%s\t%s\t%s\t%s" % (account,aws_type,hostname,bad_ports.encode("ascii"),arn))
                event_data['event_type'] = 'trigger'
                event_data['description'] = 'cloudmapper in ' + account_name
                event_data['description'] += ' had the following publicly accesible ports:' \
                    "%s\t%s\t%s\t%s\t%s" % (account,aws_type,hostname,bad_ports.encode("ascii"),arn)
            else:
                event_data['event_type'] = 'resolve'
                event_data['description'] = 'cloudmapper in ' + account_name
                event_data['description'] += ' had no publicly accesible ports'
            
            send_event(pd_url, service_key, event_data)



