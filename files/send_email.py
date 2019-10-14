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
    subject = "Cloudmapper results for " + account_name
    body_text = "Hello,\r\nPlease see the attached file for cloudmapper results."
    body_html = """\
<html>
<head></head>
<body>
<h1>Hello!</h1>
<p>Please see the attached file for cloudmapper results.</p>
</body>
</html>
"""
    attachment = '/opt/cloudmapper/web/account-data/report.html'

    ses.send_email(subject, body_text, body_html, attachment)

if __name__ == "__main__":
    send_email()
