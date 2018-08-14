
"""smartrelay is a library to send email using a no-login Smart Relay Host.

Description:
    The main target of the project is to provide an easily way to send and email
    via SMTP protocol using a Smart Relay Host that doesn't require to login
    with an user authentication.

Author:
    Giuseppe Biolo <giuseppe.biolo@gmail.com> <https://github.com/gbiolo>

License:
    This file is part of smartrelay.

    pyproc is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    pyproc is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with pyproc. If not, see <http://www.gnu.org/licenses/>.
"""


import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from .email import Email
from .exceptions import ArgumentException, AttachmentException


class Sender:
    """Class representing an email sender using the SMTP protocol."""

    def __init__(self, server_address=None):
        """Sender object constructor accepting a server address."""
        self.conn = None
        self.mail_pool = []
        if server_address:
            if type(server_address) is str:
                self.server_address = server_address
            else:
                raise ArgumentException("Wrong format for server address in sender constructor")
        else:
            self.server_address = ""

    def set_server(self, server_address):
        """Set server address value."""
        self.server_address = server_address

    def new_mail(self, sender=None, to=None, cc=None, bcc=None, subject=None,
                 message=None, attachments=None):
        """Create a new mail object and insert it into the sender mail pool."""
        new_mail = Email()
        if sender:
            new_mail.set_sender(sender)
        else:
            raise ArgumentException("No sender address indicated")
        if to:
            new_mail.set_recipients(to=to)
        else:
            raise ArgumentException("Cannot send email to an empty recipient list")
        if cc:
            new_mail.set_recipients(cc=cc)
        if bcc:
            new_mail.set_recipients(bcc=bcc)
        if subject:
            new_mail.set_subject(subject)
        else:
            raise ArgumentException("Cannot send email with empty subject field")
        if message:
            new_mail.set_message(message)
        else:
            raise ArgumentException("Cannot send email with empty messege field")
        if attachments:
            if type(attachments) == str:
                new_mail.add_attachment(attachments)
            elif type(attachments) == list:
                for attachment in attachments:
                    new_mail.add_attachment(attachment)
            else:
                raise ArgumentException("Attachments argument must be str or list")
        self.mail_pool.append(new_mail)
        return new_mail

    def _conn_server(self):
        """Create the connection to the SMTP server."""
        try:
            self.conn = smtplib.SMTP(self.server_address)
        except Exception:
            return False
        if self.conn:
            return True
        else:
            return False

    def send(self):
        """Send all the mail inserted into the pool."""
        if self._conn_server():
            for mail in self.mail_pool:
                msg = MIMEMultipart()
                msg["Subject"] = mail.subject
                msg["To"] = ", ".join(mail.recipients["to"])
                msg["Cc"] = ", ".join(mail.recipients["cc"])
                msg["Bcc"] = ", ".join(mail.recipients["bcc"])
                msg["From"] = mail.sender
                # MIME type is based on the message body; if it starts with the
                # html tag (HTML, XHTML) the MIME type will be "html", "plain"
                # otherwise
                if re.match("<html[^>]*>", mail.body):
                    msg.attach(MIMEText(mail.body, "html"))
                else:
                    msg.attach(MIMEText(mail.body, "plain"))
                for attachment in mail.attachments:
                    if not os.path.exists(attachment):
                        raise AttachmentException("Attachment " + attachment +
                                                  " doesn't exists or not accessible")
                    try:
                        part = MIMEBase('application', "octet-stream")
                        part.set_payload(open(attachment, "rb").read())
                        encode_base64(part)
                        part.add_header("Content-Disposition", "attachment; filename=\"{}\"".format(
                                        os.path.basename(attachment)))
                        msg.attach(part)
                    except Exception:
                        raise AttachmentException("Cannot add attachment " + attachment)
                try:
                    recipients = (mail.recipients["to"] + mail.recipients["cc"] +
                                  mail.recipients["bcc"])
                    self.conn.sendmail(mail.sender, recipients, msg.as_string())
                except Exception as e:
                    raise e
            return True
        else:
            return False
