"""tests.mail.py - TestMail class"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import re

from django.conf import settings
from django.core import mail
from .utils import console


def extract_activation_key(email):
    """Extract activation key from email

    :param str email: the email message to get activation key from
    :return: the activation key
    """

    # noinspection PyUnresolvedReferences
    stripped = str(email.body).replace('\n', '')
    matches = re.search(r'/accounts/activate/(\w+)/', stripped)
    return matches.group(0)


def extract_password_reset_key(email):
    """Extract password reset key from email

    :param str email: the email message to get password key from
    :return: the activation key
    """

    # noinspection PyUnresolvedReferences
    matches = re.search(r'/accounts/password/reset/confirm/(.*)/', email.body)
    return matches.group(0)


class TestMail(object):
    """TestMail class for e-mail outbox and stuff"""

    outbox = []

    @property
    def mail_path(self):
        """Get the mail save path/directory

        :return: the mail save path based on settings
        :rtype: str
        """

        return '/vagrant/tests/mail/' if getattr(settings, 'LOCAL_SERVER', False) else '/home/rof/mail/'

    def refresh(self):
        """Update mail outbox"""

        self.outbox = mail.outbox

    def save_message(self, filename_without_path, index=0):
        """Save mail dump of the current page. Path is determined by LOCAL_SERVER setting

        :param str filename_without_path: The base filename without the absolute path
        :param int index: the outbox mail index to save
        """

        if getattr(settings, 'TAKE_TEST_MAIL', False):
            console("Saving outbox mail at index {}: {}".format(index, filename_without_path))
            with open(self.mail_path + filename_without_path, 'w') as mail_file:
                if len(self.outbox) < index:
                    mail_file.write('')
                else:
                    data = self.outbox[index]
                    mail_file.write((
                        "From: {}\n"
                        "To: {}\n"
                        "CC: {}\n"
                        "BCC: {}\n"
                        "Subject: {}\n"
                        "------------------------------------------------------------------------------------------\n"
                        "{}"
                    ).format(
                        data.from_email,
                        ", ".join(data.to),
                        ", ".join(data.cc),
                        ", ".join(data.bcc),
                        data.subject,
                        data.body)
                    )
