#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

import json
import os

from django.core.management import CommandError, BaseCommand
from rest_framework.renderers import JSONRenderer

from api.models import Job
from api.serializers import JobSerializer


class Command(BaseCommand):

    def cleanUpIDs(self, json_data):
        for key in json_data.copy():
            if type(json_data[key]) == list:
                if not key == "files":
                    for item in json_data[key]:
                        item.pop('id', None)
                        item.pop('pk', None)

                        self.cleanUpIDs(item)

            if type(json_data[key]) == dict:
                self.cleanUpIDs(json_data[key]) # clean this up also..

    def handle(self, *args, **options):
        files = os.listdir("./jobs_dump")

        for file_name in files:
            print ("importing.. %s" % (file_name))

            f = open("./jobs_dump/%s" % (file_name), 'r')

            json_data = json.load(f)
            f.close()

            try:
                job = Job.objects.get(pk=json_data['id'])
            except Job.DoesNotExist:
                job = Job(id=json_data['id'])

                self.cleanUpIDs(json_data)

                json_data['job_number'] = json_data['job_number'] + "(OLD)"

                serializer = JobSerializer(job, data=json_data)
                if (serializer.is_valid(True)):
                    serializer.save()

