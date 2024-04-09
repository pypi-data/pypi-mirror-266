from datetime import datetime

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib

def GMAIL_SEND_MAIL(account_g, gmail_password, from_to, send_to, subject, message_html, slack_canal="default"):
    """
    Send an email using the Gmail SMTP server.
    Args:
        :account_g: The Gmail account used to send the email.
        :gmail_password: The password of the Gmail account.
        :from_to: The email address of the sender.
        :send_to: The email address of the recipient.
        :subject: The subject of the email.
        :message_html: The HTML content of the email.
        :slack_canal: The Slack channel to send the message to.
        
	"""
    print(datetime.now(), "\tExecution ENVOIE MAIL")
    sender = account_g
    html = message_html
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_to
    msg['To'] = "To Person <>"
    part = MIMEText(html, 'html')
    msg.attach(part)
    try:
        smtpObj = smtplib.SMTP('smtp-relay.gmail.com', port=587)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.ehlo()		
        smtpObj.login('lpb_scripts@lepetitballon.com', gmail_password)
        smtpObj.sendmail(sender, send_to, msg.as_string())         
        smtpObj.quit()
        print(f"{datetime.now()}\tSuccessfully sent email to {send_to}")
    #		sendMessageToSlack(slack_canal, "#0C7C59", f"Email envoyé à {send_to}\n avec l'objet:{subject}", f"{message_html}")
    except smtplib.SMTPException:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPException This exception is raised when the server unexpectedly disconnects, or when an attempt is made to use the SMTP instance before connecting it to a server.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPException This exception is raised when the server unexpectedly disconnects, or when an attempt is made to use the SMTP instance before connecting it to a server.")
    except smtplib.SMTPServerDisconnected:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPServerDisconnected This exception is raised when the server unexpectedly disconnects, or when an attempt is made to use the SMTP instance before connecting it to a server.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPServerDisconnected This exception is raised when the server unexpectedly disconnects, or when an attempt is made to use the SMTP instance before connecting it to a server.")
    except smtplib.SMTPResponseException:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("STMPResponseException Base class for all exceptions that include an SMTP error code. These exceptions are generated in some instances when the SMTP server returns an error code. The error code is stored in the smtp_code attribute of the error, and the smtp_error attribute is set to the error message.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "STMPResponseException Base class for all exceptions that include an SMTP error code. These exceptions are generated in some instances when the SMTP server returns an error code. The error code is stored in the smtp_code attribute of the error, and the smtp_error attribute is set to the error message.")
    except smtplib.SMTPSenderRefused:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPSenderRefused Sender address refused. In addition to the attributes set by on all SMTPResponseException exceptions, this sets ‘sender’ to the string that the SMTP server refused.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPSenderRefused Sender address refused. In addition to the attributes set by on all SMTPResponseException exceptions, this sets ‘sender’ to the string that the SMTP server refused.")
    except smtplib.SMTPRecipientsRefused:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPRecipientsRefused All recipient addresses refused. The errors for each recipient are accessible through the attribute recipients, which is a dictionary of exactly the same sort as SMTP.sendmail() returns.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPRecipientsRefused All recipient addresses refused. The errors for each recipient are accessible through the attribute recipients, which is a dictionary of exactly the same sort as SMTP.sendmail() returns.")
    except smtplib.SMTPDataError:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTP DataError The SMTP server refused to accept the message data.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTP DataError The SMTP server refused to accept the message data.")
    except smtplib.SMTPConnectError:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPConnectError Error occurred during establishment of a connection with the server.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPConnectError Error occurred during establishment of a connection with the server.")
    except smtplib.SMTPHeloError:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPHeloError The server refused our HELO message.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPHeloError The server refused our HELO message.")
    except smtplib.SMTPNotSupportedError:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPNotSupportedError The command or option attempted is not supported by the server.")
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPNotSupportedError The command or option attempted is not supported by the server.")
    except smtplib.SMTPAuthenticationError:
        print(f"{datetime.now()}\tError to sent email to {send_to}")
        print("SMTPAuthenticationError SMTP authentication went wrong. Most probably the server didn’t accept the username/password combination provided.")		
        #sendMessageToSlack(slack_canal, "#D64933", f"Erreur pour {send_to} \n avec l'objet:{subject}", "SMTPAuthenticationError SMTP authentication went wrong. Most probably the server didn’t accept the username/password combination provided.")