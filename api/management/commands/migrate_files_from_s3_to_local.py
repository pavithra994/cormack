from django.core.management.base import BaseCommand

from boto.exception import S3ResponseError

from django.conf import settings


class Command(BaseCommand):
    help = 'Migrate Files From S3 To Local'

    def handle(self, *args, **options):
        print("Working")

        DOWNLOAD_LOCATION_PATH = "media/"

        import os
        import boto

        # # AWS Settings
        AWS_STORAGE_BUCKET_NAME = "ocom-cormack"
        AWS_ACCESS_KEY_ID = "AKIAIFWLNM6ETZ27QEXQ"
        AWS_SECRET_ACCESS_KEY = "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"
        # AWS_S3_FILE_OVERWRITE = False
        # AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME

        # MEDIAFILES_LOCATION = ''
        # MEDIAFILES_LOCATION = '/dev'
        # MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, MEDIAFILES_LOCATION)
        # DEFAULT_FILE_STORAGE = 'custom_storages.MediaStorage'

        connect = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
        bucket = connect.get_bucket(AWS_STORAGE_BUCKET_NAME)

        bucket_list = bucket.list()

        for l in bucket_list:
            key_string = str(l.key)
            s3_path = DOWNLOAD_LOCATION_PATH + key_string

            if "/dev/" in s3_path or "/live/" in s3_path:
                s3_path = s3_path.replace("/dev/", "/")
                s3_path = s3_path.replace("/live/", "/")

                try:
                    print ("Current File is ", s3_path)
                    l.get_contents_to_filename(s3_path)
                except (OSError,S3ResponseError) as e:
                    pass
                    # check if the file has been downloaded locally  
                    if not os.path.exists(s3_path):
                        try:
                            os.makedirs(s3_path)
                        except OSError as exc:
                            # let guard againts race conditions
                            import errno
                            if exc.errno != errno.EEXIST:
                                raise