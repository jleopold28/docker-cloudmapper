import os
import json
import datetime
import premailer
import re
import shutil
from tempfile import mkstemp
from premailer import transform
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

    body_html = """\
<html>
<head></head>
<body>
<p>Please see the attached file for cloudmapper results.</p>
</body>
</html>
"""

    # Run premailer transformation to inject CSS data directly in HTML
    # https://pypi.org/project/premailer/
    report_name = premailer_transform('/opt/cloudmapper/web/account-data/report.html')
    attachments = [report_name]

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

def premailer_transform(source):
    """Runs premailer transformation on an html source file.
    First use sed commands to change javascript file src
    A new HTML file with CSS injections is created

    Args:
        source  (str): input filename
    Returns:
        output_file (str): name of newly generated html file
    """
    
    # Replace the js script source with raw github content
    # Content is served via jsdelivr CDN (https://www.jsdelivr.com/)
    # Raw github files do not have correct js headers
    sed('../js/chart.js', 'https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/chart.js', source)
    sed('../js/report.js','https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/report.js', source)
    sed('../favicon.ico','https://raw.githubusercontent.com/duo-labs/cloudmapper/master/web/favicon.ico', source)

    fin = open(source, 'r')
    new_content = transform(fin.read(), base_path='/opt/cloudmapper/web/css')
    now = datetime.datetime.now()
    cloudmapper_filename = 'cloudmapper_report_' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '.html'
    fout = open('/opt/cloudmapper/' + cloudmapper_filename, 'w+')
    fout.write(new_content)
    fin.close()
    fout.close()

    # Hack to fix Javascript Pop up Chart backgrounds
    # For some reason, premailer has a hard time evaluating the CSS on JS componenets
    additional_css = """
.mytooltip:hover .tooltiptext {visibility:visible}
#chartjs-tooltip td {background-color: #fff}
#chartjs-tooltip table {box-shadow: 5px 10px 8px #888888}
table {border-collapse:collapse;}
table, td, th {border:1px solid black; padding: 1px;}
th {background-color: #ddd; text-align: center;}"""

    sed('.mytooltip:hover .tooltiptext {visibility:visible}', additional_css, cloudmapper_filename)

    return cloudmapper_filename

if __name__ == "__main__":
    send_email()
