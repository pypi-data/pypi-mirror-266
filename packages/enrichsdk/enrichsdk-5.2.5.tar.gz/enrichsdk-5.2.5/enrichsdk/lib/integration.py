import os
import sys
import smtplib
import time
import mimetypes
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage


def attach_files(msg, attachments=[]):

    # https://docs.python.org/3.4/library/email-examples.html
    for path in attachments:

        if (not isinstance(path, str)) or (not os.path.isfile(path)):
            continue

        ctype, encoding = mimetypes.guess_type(path)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)
        if maintype == "text":
            with open(path) as fp:
                attach = MIMEText(fp.read(), _subtype=subtype)
        elif maintype == "image":
            with open(path, "rb") as fp:
                attach = MIMEImage(fp.read(), _subtype=subtype)
        elif maintype == "audio":
            with open(path, "rb") as fp:
                attach = MIMEAudio(fp.read(), _subtype=subtype)
        else:
            with open(path, "rb") as fp:
                attach = MIMEBase(maintype, subtype)
                attach.set_payload(fp.read())
            encoders.encode_base64(attach)

        filename = os.path.basename(path)
        attach.add_header("Content-Disposition", "attachment", filename=filename)
        msg.attach(attach)


def send_html_email(content, sender, receivers, subject, attachments=[], reply_to=[], cc=[], bcc=[], cred={}, retries=2):
    """
    Send HTML email to target audience
    """
    if cred is None:
        cred = {}

    retry_delay = 30 # seconds

    msg = MIMEMultipart()
    msg.attach(MIMEText(content, "html"))

    if isinstance(receivers, str):
        receivers = [receivers]

    msg["From"] = sender
    msg["To"] = ", ".join(receivers)
    if isinstance(reply_to, list) and len(reply_to) > 0:
        msg.add_header('reply-to', ",".join(reply_to))
    msg["Subject"] = subject
    if len(cc) > 0:
        msg['Cc'] = ",".join(cc)
    if len(bcc) > 0:
        msg['Bcc'] = ",".join(bcc)

    # Construct final list that includes everyone...
    to = receivers + cc + bcc

    # Add payload
    if isinstance(attachments, list) and len(attachments) > 0:
        attach_files(msg, attachments)

    server = cred.get("EMAIL_HOST", os.environ["EMAIL_HOST"])
    username = cred.get("EMAIL_HOST_USER", os.environ["EMAIL_HOST_USER"])
    password = cred.get("EMAIL_HOST_PASSWORD", os.environ["EMAIL_HOST_PASSWORD"])
    port = cred.get("EMAIL_PORT", os.environ.get("EMAIL_PORT", "587"))
    timeout = cred.get("EMAIL_TIMEOUT", os.environ.get("EMAIL_TIMEOUT", "30"))

    # Collect the body
    text = msg.as_string()


    while retries > 0:
        try:
            smtp = smtplib.SMTP(server, port=int(port), timeout=int(timeout))
            smtp.starttls()
            smtp.login(username, password)
            smtp.sendmail(sender, to, text)
            return
        except:
            retries -= 1
            time.sleep(retry_delay)

    raise Exception("Email sending process exhausted retries")
