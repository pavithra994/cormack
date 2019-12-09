"""tests.fixtures.py - Factory Fixtures declarations"""

#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.contrib.auth.models import User
from django.test import RequestFactory
from api import models
from faker import Faker

import factory
import datetime

fake = Faker()
nuke_mapper = {
    'jobs': ("Jobs", models.Job, None),
    'repairs': ("Repairs", models.Repair, None),
}


class UserFactory(factory.DjangoModelFactory):
    """Auth User Factory"""

    # noinspection PyClassicStyleClass
    class Meta:
        """Django Auth user model"""

        model = User

    username = factory.Sequence(lambda n: "user0{}-{}".format(n, fake.hex_color()[1:]))
    email = factory.Sequence(lambda n: "user0{}@testing.net".format(n))
    password = 'testing123'
    first_name = factory.Iterator([fake.first_name_male(), fake.first_name_female(), fake.first_name()])
    last_name = factory.LazyAttribute(lambda x: fake.last_name())

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""
        manager = cls._get_manager(model_class)
        # The default would use ``manager.create(*args, **kwargs)``
        return manager.create_user(*args, **kwargs)


class DefaultUserFactory(UserFactory):
    """Auth User Factory"""

    username = 'testing2'
    email = 'testing2@testing.com'


class AdminUserFactory(UserFactory):
    """Admin Auth User Factory"""

    username = 'the_admin'
    email = 'the_admin@ocomsoft.com'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default ``_create`` with our custom call."""

        manager = cls._get_manager(model_class)
        return manager.create_superuser(*args, **kwargs)


class DrainTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Drain Type model"""
        model = models.CodeDrainType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class FileTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """File Type model"""
        model = models.CodeFileType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class JobTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Job Type model"""
        model = models.CodeJobType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.job())


class PavingColourFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Paving Colour model"""
        model = models.CodePavingColour

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class PavingTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Paving Type model"""
        model = models.CodePavingType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class RepairTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Repair Type model"""
        model = models.CodeRepairType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class SubbieTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Subbie Type model"""
        model = models.CodeSubbieType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class TaskTypeFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Task Type model"""
        model = models.CodeTaskType

    code = factory.LazyAttribute(lambda x: fake.word() + str(fake.random_number(3)))
    description = factory.LazyAttribute(lambda x: fake.text(30))


class JobFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Business Opportunity model"""
        model = models.Job
        # exclude = ('active_start_date',)

    description = factory.LazyAttribute(lambda x: fake.company())
    date_received = factory.LazyFunction(datetime.datetime.utcnow)
    address = factory.LazyAttribute(lambda x: fake.address())
    purchase_order_number = factory.LazyAttribute(lambda x: fake.random_number(12))


class SubbieFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Client model"""
        model = models.Subbie

    name = factory.LazyAttribute(lambda x: fake.name())
    xero_supplier = factory.LazyAttribute(lambda x: fake.random_letter())


class ClientFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Client model"""
        model = models.Client

    name = factory.LazyAttribute(lambda x: fake.name())
    xero_customer = factory.LazyAttribute(lambda x: fake.random_letter())


class RoleFactory(factory.DjangoModelFactory):
    # noinspection PyClassicStyleClass
    class Meta:
        """Role model"""
        model = models.Role


class Sampler(object):
    """Factory runner"""

    request = RequestFactory()

    def __init__(self):
        """runner initialization routines"""

        self.utils = None

    def set_utils(self, utils):
        """set utils reference

        :param ocom.tests.app.OcomTestUtils utils: the utilities object to refer from
        """

        self.utils = utils

    def nuke(self, record_type):
        """Remove all records from a specified type matched against a model from nuke mapper

        :param str record_type: the record type to match against the nuke mapper
        """

        label, model, model_filter = nuke_mapper[record_type]
        self.utils.console("Removing all {} contents...".format(label))
        model.objects.all().delete()

    def admin_user(self, username=None, password=None):
        """Add a default admin user account and return its reference

        :param str or None username: the account name to set
        :param str or None password: the account password to set (None will use the default)
        :return: the default admin user record
        :rtype: User
        """

        kwargs = {}

        if username is not None:
            kwargs['username'] = username

        if password is not None:
            kwargs['password'] = password

        self.utils.console("Adding admin user...")
        return AdminUserFactory(**kwargs)

    def user(self, username=None, password=None, superuser=False, **kwargs):
        """Add a user account and return its reference

        :param str or None username: the account name to set
        :param str or None password: the account password to set (None will use the default)
        :param bool superuser: If true, account is super user
        :return: the new user record
        :rtype: User
        """

        if username is not None:
            kwargs['username'] = username

        if password is not None:
            kwargs['password'] = password

        if superuser:
            self.utils.console("Adding superuser...")
            return AdminUserFactory(**kwargs)
        else:
            self.utils.console("Adding user...")
            return UserFactory(**kwargs)

    def drain_type(self, **kwargs):
        """Add a Drain Type and return its reference

        :return: the Drain Type record
        :rtype: Drain Type
        """

        self.utils.console("Adding drain type...")
        return DrainTypeFactory(**kwargs)

    def file_type(self, **kwargs):
        """Add a File Type and return its reference

        :return: the File Type record
        :rtype: File Type
        """

        self.utils.console("Adding file type...")
        return FileTypeFactory(**kwargs)

    def job_type(self, **kwargs):
        """Add a Job Type and return its reference

        :return: the Job Type record
        :rtype: Job Type
        """

        self.utils.console("Adding job type...")
        return JobTypeFactory(**kwargs)

    def paving_colour(self, **kwargs):
        """Add a Paving Colour and return its reference

        :return: the Paving Colour record
        :rtype: Paving Colour
        """

        self.utils.console("Adding paving colour...")
        return PavingColourFactory(**kwargs)

    def paving_type(self, **kwargs):
        """Add a Paving Type and return its reference

        :return: the Paving Type record
        :rtype: Paving Type
        """

        self.utils.console("Adding paving type...")
        return PavingTypeFactory(**kwargs)

    def repair_type(self, **kwargs):
        """Add a Repair Type and return its reference

        :return: the Repair Type record
        :rtype: Repair Type
        """

        self.utils.console("Adding repair type...")
        return RepairTypeFactory(**kwargs)

    def subbie_type(self, **kwargs):
        """Add a Subbie Type and return its reference

        :return: the Subbie Type record
        :rtype: Subbie Type
        """

        self.utils.console("Adding subbie type...")
        return SubbieTypeFactory(**kwargs)

    def task_type(self, **kwargs):
        """Add a Task Type and return its reference

        :return: the Task Type record
        :rtype: Task Type
        """

        self.utils.console("Adding task type...")
        return TaskTypeFactory(**kwargs)

    def job(self, **kwargs):
        """Add a Job and return its reference

        :return: the Job record
        :rtype: Job
        """

        self.utils.console("Adding job...")
        return JobFactory(**kwargs)

    def subbie(self, **kwargs):
        """Add a Subbie and return its reference

        :return: the Subbie record
        :rtype: Subbie
        """

        self.utils.console("Adding subbie...")
        return SubbieFactory(**kwargs)

    def client(self, **kwargs):
        """Add a Client and return its reference

        :return: the Client record
        :rtype: Client
        """

        self.utils.console("Adding client...")
        return ClientFactory(**kwargs)

    def role(self, **kwargs):
        """Add a Role and return its reference

        :return: the Role Source record
        :rtype: Role
        """

        self.utils.console("Adding role...")
        return RoleFactory(**kwargs)

    @staticmethod
    def version():
        return '0.91.0'      # updated using bumpversion
