
#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

#
#
#

from os import makedirs

from django.contrib.auth.models import AnonymousUser, User
from django.core.management import CommandError, BaseCommand
from rest_framework.renderers import JSONRenderer

from api.models import Job
from api.serializers import JobSerializer
from django.test.client import RequestFactory
from ocom.viewsets import SESSION_USER_ID


class Command(BaseCommand):

    def handle(self, *args, **options):
        ids = [    34 ,
                   38,
                   53,
                   71,
                   73,
                   85,
                   89,
                  161,
                  224,
                  252,
                  362,
                  456,
                  476,
                  513,
                  572,
                  584,
                  606,
                  644,
                  652,
                  788,
                  789,
                  904,
                  936,
                  970,
                 1161
        ]

        jobs = Job.objects.filter(id__in=ids)

        makedirs("jobs_dump", exist_ok=True)

        request = RequestFactory().get('/api/job')
        request.user = User.objects.get(pk=1)

        context = {
            'request': request
        }

        for job in jobs:
            serializer = JobSerializer(job, context=context)

            json = JSONRenderer().render(serializer.data)

            filename = "./jobs_dump/%d.json" % (job.id)

            print ("Writing %s" % (filename))

            f = open(filename, 'wb')
            f.write (json)
            f.close()
