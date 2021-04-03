import smtplib
import ssl
import os
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config_personal import sender_email, receiver_email, subject, port, smtp_server, password


def send_email(image_file_name=None):
    # create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    body = "Motion has been captured and saved to drive"

    # add body to email
    message.attach(MIMEText(body, "plain"))

    # read and attach image
    if image_file_name is not None:
        img_data = open(image_file_name, 'rb').read()
        image = MIMEImage(img_data, name=os.path.basename(image_file_name))
        message.attach(image)
    text = message.as_string()

    # send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
