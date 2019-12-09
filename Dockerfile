#pull official base image
FROM python:3.7.4-alpine

RUN mkdir -p /opt/services/cormack/src

# set work directory
WORKDIR /opt/services/cormack/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip install --upgrade pip && \
    pip install virtualenv

RUN apk update && apk add libpq

# Installing build dependencies
# For python3 you need to add python3-dev *please upvote the comment
# of @its30 below if you use this*
# RUN apk add --virtual .build-deps gcc python3-dev musl-dev postgresql-dev

RUN apk add --no-cache gcc python3-dev musl-dev postgresql-dev libffi-dev build-base py2-pip && pip install cffi

#copy requirements.txt
COPY requirements.txt /opt/services/cormack/src/requirements.txt

# Creating python venv
RUN python3 -m virtualenv --python=/usr/bin/python3 /opt/venv

# Installing and build python module
RUN /opt/venv/bin/pip install -r requirements.txt

# Delete build dependencies
# RUN apk del .build-deps

# copy project
COPY . /opt/services/cormack/src

RUN pip install gunicorn django
RUN /opt/venv/bin/python manage.py collectstatic --no-input

EXPOSE 8002

ENTRYPOINT /opt/venv/bin/python manage.py runserver 0.0.0.0:8002
# define the default command to run when starting the container
#CMD ["gunicorn", "--chdir", "config", "--bind", ":8002", "config.wsgi:application"]
