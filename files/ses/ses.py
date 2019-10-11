import os
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

class SES():

    # The character encoding for the email.
    CHARSET = "utf-8"

    # Specify a configuration set. If you do not want to use a configuration
    # set, comment the following variable, and the 
    # ConfigurationSetName=CONFIGURATION_SET argument below.
    #CONFIGURATION_SET = "ConfigSet"

    def __init__(self, sender, recipient, region):
        """
        Initialize the SES provider

        :param X: fds
        :type X: str
        """
        self.sender = sender
        self.recipient = recipient
        self.region = region

        # Create a new SES resource
        self.client = boto3.client('ses',region_name=region)

    def send_email(self, subject, body_text, body_html, attachment):
        # Create a multipart/mixed parent container.
        msg = MIMEMultipart('mixed')
        # Add subject, from and to lines.
        msg['Subject'] = subject 
        msg['From'] = self.sender 
        msg['To'] = self.recipient

        # Create a multipart/alternative child container.
        msg_body = MIMEMultipart('alternative')
        # Encode the text and HTML content and set the character encoding. This step is
        # necessary if you're sending a message with characters outside the ASCII range.
        textpart = MIMEText(body_text.encode(self.CHARSET), 'plain', self.CHARSET)
        htmlpart = MIMEText(body_html.encode(self.CHARSET), 'html', self.CHARSET)

        # Add the text and HTML parts to the child container.
        msg_body.attach(textpart)
        msg_body.attach(htmlpart)

        # Define the attachment part and encode it using MIMEApplication.
        att = MIMEApplication(open(attachment, 'rb').read())

        # Add a header to tell the email client to treat this part as an attachment,
        # and to give the attachment a name.
        att.add_header('Content-Disposition','attachment',filename=os.path.basename(attachment))

        # Attach the multipart/alternative child container to the multipart/mixed
        # parent container.
        msg.attach(msg_body)

        # Add the attachment to the parent container.
        msg.attach(att)

        # Add the attachment to the parent container.
        msg.attach(att)
        #print(msg)
        try:
            #Provide the contents of the email.
            response = self.client.send_raw_email(
                Source=self.sender,
                Destinations=[
                    self.recipient
                ],
                RawMessage={
                    'Data':msg.as_string(),
                }
            )
        # Display an error if something goes wrong.	
        except ClientError as e:
            print(e.response['Error']['Message'])
        else:
            print("Email sent! Message ID:"),
            print(response['MessageId'])


