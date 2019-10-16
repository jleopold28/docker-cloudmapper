import os
import datetime
import premailer
import re
import shutil
from tempfile import mkstemp
from premailer import transform
from .ses import SES

class Report():
    
    # Base path for CSS stylings, default for cloudmapper
    BASE_PATH = '/opt/cloudmapper/web/css'

    def __init__(self, report_source='/opt/cloudmapper/web/account-data/report.html', account_name=None, sender=None, recipient=None, region=None, ses_enabled=None):
        """
        Initialize the Cloudmapper report. Sets variables for email.

        :param account_name: AWS account name
        :type account_name: str
        :param sender: Email address registered to SES that will send emails
        :type sender: str
        :param recipient: Email address to send emails to
        :type recipient: str
        :param region: AWS Region
        :type region: str
        :param ses_enabled: wheter the SES email functionality is enabled
        :type ses_enabled: str
        """
        self.report_source = report_source
        if account_name is None:
            account_name = os.environ.get('ACCOUNT', None)

        if sender is None:
            sender = os.environ.get('SES_SENDER', None)
    
        if recipient is None:
            recipient = 'AWS SES <' + os.environ.get('SES_RECIPIENT', None) + '>'

        if region is None:
            region = os.environ.get('AWS_REGION', None)

        if ses_enabled is None:
            ses_enabled = os.environ.get('SES_ENABLED', None)

        self.account_name = account_name
        self.sender = sender
        self.recipient = recipient
        self.region = region
        self.ses_enabled = ses_enabled

        self.ses = SES(self.region)
    
    def generate_and_send_email(self):
        """
        Generate Cloudmapper Email and send via AWS SES

        Transformations are done on the report.html file
        to support CSS and JS functionality
        """

        if self.ses_enabled != "true":
            print("Skipping Cloudmapper SES Email send because SES is not enabled.")
            return

        subject = '[cloudmapper ' + self.account_name + '] Cloudmapper audit findings'
        body_text = "Please see the attached file for cloudmapper results."

        # Inject JS file contents into HTML
        self.js_replace(self.report_source)

        # Run premailer transformation to inject CSS data directly in HTML
        # https://pypi.org/project/premailer/
        out_file = self.premailer_transform(self.report_source)

        with open(out_file, 'r') as html:
            body_html = html.read()

        attachments = [out_file]

        self.ses.send_email(self.sender, self.recipient, subject, body_text, body_html, attachments)

    def js_replace(self, source):
        """
        Replaces js source file tags with js file contents.
        This allows the html to contain all data needed for the report
        with no additional links, etc.
        
        :param source: Filepath to report.html
        :type source: str
        """

        html = open(source, 'r')
        html_data = html.read()
        html.close()

        chart_js = open('/opt/cloudmapper/web/js/chart.js', 'r')
        chart_js_data = chart_js.read()
        chart_js.close()

        report_js = open('/opt/cloudmapper/web/js/report.js', 'r')
        report_js_data = report_js.read()
        report_js.close()

        new_html_data = html_data.replace('<script src="../js/chart.js"></script>', '<script>' + chart_js_data + '</script>')
        new_html_data = new_html_data.replace('<script src="../js/report.js"></script>', '<script>' + report_js_data + '</script>')

        new_html = open(source, 'w')
        new_html.write(new_html_data)
        new_html.close()

    def premailer_transform(self, source):
        """Runs premailer transformation on an html source file.

        First use sed commands to change javascript file src
        A new HTML file with CSS injections is created

        :param source: Filepath to report.html
        :type source: str
        """
        
        # Replace the js script source with raw github content
        # Content is served via jsdelivr CDN (https://www.jsdelivr.com/)
        # Raw github files do not have correct js headers
        #self.sed('../js/chart.js', 'https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/chart.js', source)
        #self.sed('../js/report.js','https://cdn.jsdelivr.net/gh/duo-labs/cloudmapper@master/web/js/report.js', source)
        #self.sed('../favicon.ico','https://raw.githubusercontent.com/duo-labs/cloudmapper/master/web/favicon.ico', source)

        #with open('/opt/cloudmapper/web/js/chart.js', 'r') as chart_js:
        #    chart_js_data = chart_js.read()

        now = datetime.datetime.now()
        cloudmapper_filename = 'cloudmapper_report_' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '.html'

        with open(source, 'r') as fin, open('/opt/cloudmapper/' + cloudmapper_filename, 'w+') as fout:
            data = fin.read()
            new_content = transform(data, base_path=self.BASE_PATH)
            fout.write(new_content)

        # Fix Javascript Pop up Chart backgrounds
        # For some reason, premailer has a hard time evaluating the CSS on JS componenets
        additional_css = """
    .mytooltip:hover .tooltiptext {visibility:visible}
    #chartjs-tooltip td {background-color: #fff}
    #chartjs-tooltip table {box-shadow: 5px 10px 8px #888888}
    table {border-collapse:collapse;}
    table, td, th {border:1px solid black; padding: 1px;}
    th {background-color: #ddd; text-align: center;}"""

        self.sed('.mytooltip:hover .tooltiptext {visibility:visible}', additional_css, cloudmapper_filename)

        return cloudmapper_filename
    
    def sed(self, pattern, replace, source, dest=None):
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
