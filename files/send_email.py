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
    attachments = ['/opt/cloudmapper/web/account-data/report.html',
    '/opt/cloudmapper/' + account_name + '-audit.json'
    ]

    ses.send_email(subject, body_text, body_html, attachments)

if __name__ == "__main__":
    send_email()
