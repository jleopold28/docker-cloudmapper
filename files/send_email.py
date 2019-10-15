import os
import json

import premailer
from premailer import transform

import re
import shutil
from tempfile import mkstemp

from ses.ses import SES

def send_email():
    # Get variables from env
    ses_enabled     = os.getenv('SES_ENABLED')

    if ses_enabled != "true":
        print("Skipping Cloudmapper SES Email send because SES is not enabled.")
        return

    account_name    = os.getenv('ACCOUNT')
    sender          = os.getenv('SES_SENDER')
    recipient       = 'AWS SES <' + os.getenv('SES_RECIPIENT') + '>'
    region          = os.getenv('AWS_REGION')
    ses = SES(sender, recipient, region)
    subject = '[cloudmapper ' + account_name + '] Cloudmapper audit findings'
    body_text = "Please see the attached file for cloudmapper results."

    #with open('/opt/cloudmapper/' + account_name + '-audit.json') as json_file:
    #    audit_json = json.load(json_file)
    #    build_direction = "TOP_TO_BOTTOM"
    #    table_attributes = {"style" : "width:100%", "class" : "table table-striped"}
    #    audit_table = convert(audit_json, build_direction=build_direction, table_attributes=table_attributes)

    body_html = """\
<html>
<head></head>
<body>
<p>Please see the attached file for cloudmapper results.</p>
</body>
</html>
"""
    #body_html += audit_table
    #body_html += """\
#</html>
#"""

    # Replace the script string
    sed('../js/chart.js', 'https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/chart.js', "/opt/cloudmapper/web/account-data/report.html")
    sed('../js/report.js','https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/report.js',"/opt/cloudmapper/web/account-data/report.html")
    #pysed.replace('../js/chart.js', 'https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/chart.js', '/opt/cloudmapper/web/account-data/report.html')
    #pysed.replace('../js/report.js','https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/report.js','/opt/cloudmapper/web/account-data/report.html')


    f = open('/opt/cloudmapper/web/account-data/report.html', 'r')
    new_content = transform(f.read(), base_path='/opt/cloudmapper/web/css')
    o = open('/opt/cloudmapper/new_report.html', 'w+')
    o.write(new_content)

    attachments = ['/opt/cloudmapper/new_report.html']

    ses.send_email(subject, body_text, body_html, attachments)

def sed(pattern, replace, source, dest=None):
    """Reads a source file and writes the destination file.

    In each line, replaces pattern with replace.

    Args:
        pattern (str): pattern to match (can be re.pattern)
        replace (str): replacement str
        source  (str): input filename
        dest (str): destination filename, if not given, source will be over written.        
    """

    fin = open(source, 'r')
    if dest:
        fout = open(dest, 'w')
    else:
        fd, name = mkstemp()
        fout = open(name, 'w')
    
    for line in fin:
        out = re.sub(pattern, replace, line)
        fout.write(out)

    try:
        fout.writelines(fin.readlines())
    except Exception as E:
        raise E

    fin.close()
    fout.close()

    if not dest:
        shutil.move(name, source)


if __name__ == "__main__":
    send_email()
