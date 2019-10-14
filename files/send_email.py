import os
import json
import json2table
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

    audit_json = json.loads('/opt/cloudmapper/' + account_name + '-audit.json')
    build_direction = "LEFT_TO_RIGHT"
    table_attributes = {"style": "width:100%"}
    audit_table = json2table.convert(audit_json, build_direction=build_direction, table_attributes=table_attributes)
    
    body_html = """\
<html>
<head></head>
<body>
<p>Please see the attached file for cloudmapper results.</p>
"""
    body_html += audit_table
    body_html += """\
</body>
</html>
"""
    attachments = ['/opt/cloudmapper/web/account-data/report.html']

    ses.send_email(subject, body_text, body_html, attachments)

if __name__ == "__main__":
    send_email()
