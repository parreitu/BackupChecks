#!/usr/bin/python
import smtplib 
from email.mime.text import MIMEText
import os

# uncomment this line and put your SMTP server's IP address
# DEFAULT_SMTP = "192.168.10.1"

def send_email (sender, receivers, subject, message, smtp_ip = DEFAULT_SMTP):

    for mail_to in receivers:
        try:
            message2 = "From: " + sender + "\n" + "To: " + mail_to + "\n" + "Subject: " + subject + "\n" + message + '\n'
            smtpObj = smtplib.SMTP(smtp_ip)
            smtpObj.sendmail(sender, mail_to, message2)                    
        except smtplib.SMTPException:
            print "Error: unable to send email"


# to test:
# email_message = "CAUTION There aren't 'bz2' copies in the backup folder"
# send_email('myname@mydomain.com', ['myname@mydomain.com', 'othername@mydomain.com'], "Elkarbackup: Errors", email_message)

