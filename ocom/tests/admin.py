"""tests.admin.py - AdminAction

These are used by Ocom Test module for performing Admin-level commands, including command-line stuff
"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.auth.models import User
from . import app, utils


class AdminAction(app.Foundation, app.OcomTestUtils):
    """Back-end Admin action"""

    def _call_command(self, instruction, message=''):
        """Convenience function to run management.call_command

        :param str or list instruction: the instruction or instruction set to run
        :param str message: the dump message to display
        """

        response = utils.call_command_silent(instruction, message=message, verbosity=self.verbosity)
        self.console(response, tabs=1)

    def check_permissions(self):
        """Update test DB on permissions of accounts (Userena command)"""

        self.start_timer('permissions', self.timers)
        self._call_command('check_permissions', "Updating permissions for accounts in db...")
        self.time_elapsed('permissions', self.timers, tabs=1)

    def activate_account(self, username):
        """Activate a user account

        :param str username: account username
        """

        self.console("Activating user account: {}".format(username))
        user = User.objects.get(username=username)
        user.is_active = True
        user.save()
