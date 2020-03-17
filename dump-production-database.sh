#!/bin/bash

ssh root@jms-prod-db.cormackgroup.com.au sudo -u postgres pg_dump -d cormack_jms > cormack.populated.sql

