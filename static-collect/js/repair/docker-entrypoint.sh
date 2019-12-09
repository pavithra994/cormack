#!/bin/bash

cd /usr/src/app

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput > static_list.txt
OUT=$?
if [ $OUT -ne 0 ];then
    echo "Fix static collection - it failed with status: $OUT"
    exit 1
fi

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput
OUT=$?
if [ $OUT -ne 0 ];then
    echo "Fix Migrations - failed with status: $OUT"
    exit 1
fi

supervisord -n
