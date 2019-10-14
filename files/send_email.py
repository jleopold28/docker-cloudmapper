import os
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
    subject = account_name + ' cloudmapper results'
    body_text = "Please see the attached file for cloudmapper results."
    body_html = """\
<html>
<head></head>
<body>
<p>Please see the attached file for cloudmapper results.</p>
</body>
</html>
"""
    attachments = ['/opt/cloudmapper/web/account-data/report.html',
    '/opt/cloudmapper/web/css/bootstrap.css',
    '/opt/cloudmapper/web/css/lato.css',
    '/opt/cloudmapper/web/css/report.css',
    '/opt/cloudmapper/web/js/chart.js',
    '/opt/cloudmapper/web/js/report.js']

    ses.send_email(subject, body_text, body_html, attachments)

if __name__ == "__main__":
    send_email()
