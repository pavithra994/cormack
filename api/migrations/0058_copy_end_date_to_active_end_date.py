#
#  Copyright (C) 2019 Ocom Software- All Rights Reserved
#  Unauthorized copying of this file, via any medium is strictly prohibited
#  Proprietary and confidential
#  Written by Ocom Software <licence@ocom.com.au, 2019
#
#

from django.db import migrations
from api.models import Job


def copy_end_date_to_active_date(apps, schema_editor):
    for job in Job.objects.all():
        if job.active_end_date is None:
            job.active_end_date = job.end_date
            job.save()


class Migration(migrations.Migration):
    dependencies = [
        ('api', '0057_merge_20180405_0926'),
    ]

    operations = [
#        migrations.RunPython(copy_end_date_to_active_date)
    ]
