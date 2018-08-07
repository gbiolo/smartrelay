
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
from .exceptions import ArgumentException, AttachmentException


class Email:
    """Class that represent a mail that will be inserted into the sender pool."""

    def __init__(self):
        """Class constructor."""
        self.sender = ""
        self.recipients = {
            "to": [],
            "cc": [],
            "bcc": []
        }
        self.subject = ""
        self.body = ""
        self.attachments = []

    def _validate_address(self, address):
        """Validate an email address; return True if the address is valid, False instead."""
        if re.match("[^@]+@[^@]+\.[^@]+", address):
            return True
        else:
            return False

    def _update_recipients(self, group, new_recipients):
        """Replace the exists recipient list with a new one.

        The group argument select one of the recipient groups (to, cc, bcc),
        the new_recipients argument can be a string or a list.
        """
        if type(new_recipients) == str:
            if self._validate_address(new_recipients):
                self.recipients[group] = [new_recipients]
        elif type(new_recipients) == list:
            self.recipients[group] = []
            for new_recipient in new_recipients:
                if self._validate_address(new_recipient):
                    self.recipients[group].append(new_recipient)
        else:
            raise ArgumentException("Wrong format in update recipients new list")

    def set_sender(self, sender):
        """Setter of the mail sender field."""
        if self._validate_address(sender):
            self.sender = sender

    def set_recipients(self, to=None, cc=None, bcc=None):
        """Setter of the mail recipients."""
        if to:
            self._update_recipients("to", to)
        if cc:
            self._update_recipients("cc", cc)
        if bcc:
            self._update_recipients("bcc", bcc)

    def set_subject(self, subject):
        """Setter of the mail subject field."""
        self.subject = subject

    def set_message(self, message):
        """Setter of the mail message field."""
        self.body = message

    def add_attachment(self, attachment):
        """Attach to the mail an existing file."""
        if os.path.isfile(attachment):
            self.attachments.append(attachment)
        else:
            raise AttachmentException("Attachment \"" + attachment + "\" not accessible")
