import os
import json
import sys
import subprocess
import csv
import pandas
import logging
from pandas.io.json import json_normalize
from .pagerdutyv1 import PagerDutyV1

logger = logging.getLogger(__name__)

class PortCheck():

    def __init__(self, ok_ports, account_name):
        """
        Initialize PortCheck provider.

        :param ok_ports: List of acceptable ports to be
          accessible to the public internet.
        :type ok_ports: list
        :param account_name: A name for the account that
          cloudmapper is currently running on, to use
          in the default incident_key and description
        :type account_name: str
        """
        self.ok_ports = ok_ports
        self.account_name = account_name
        self.filename_in = account_name + '.json'
        self.pd = PagerDutyV1(account_name)

    def get_bad_ports(self, ports):
        """
        Compare the list of publicly acceible ports
        to the ports that are acceptable. 

        Return any ports that should not be accessible.

        :param ports: List of publicly accesible ports
        :type ports: list
        """
        # 943 = tuckernet 
        # 1194 = tuckernet udp
        #ok_ports = ['80','443','8080','943','1194']
        bad_ports = []
        for port in ports:
            if port not in self.ok_ports:
                bad_ports.append(port)
        return bad_ports

    def test_each_port(self, host, ports):
        """
        Test each port to see if it can be accessed.

        :param host: Host to connect to
        :type host: str
        :param ports: Ports on host
        :type ports: list
        """
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

    def check_ports(self):
        """
        Check which ports are publicly accesible.
        Read the account.json file and parse through the open ports.
        Test each port with the test_each_port function.

        Alert PagerDuty if any publicly accesible ports are not
        in the list of acceptable ports.

        If no bad ports are found, resolve the issue in PagerDuty.
        """
        sys.stdin = open(self.filename_in, 'r')

        with sys.stdin as data:
            csv_filename = self.account_name + '.csv'

            json_data = json.load(data)
            df = json_normalize(json_data)
            df = df[['account', 'type', 'hostname', 'ports', 'arn']]
            #csv_data = df.to_csv(csv_filename,header=False, index=False)

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
                
                    bad_ports = self.get_bad_ports(ports)
                    bad_ports = self.test_each_port(hostname, bad_ports)
                    bad_ports = ",".join(bad_ports)
                
                    if bad_ports:
                        print("%s\t%s\t%s\t%s\t%s" % (account,aws_type,hostname,bad_ports.encode("ascii"),arn))
                        problem_str = ' had the following publicly accesible ports:' \
                            "%s\t%s\t%s\t%s\t%s" % (account,aws_type,hostname,bad_ports.encode("ascii"),arn)
                        self.pd.on_failure(problem_str)
                    else:
                        self.pd.on_success()