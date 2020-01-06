# Cormack Concreting Job Management System

These instructions contain information on setting up a development environment for this Django app using Vagrant, a tool
for provisioning virtual machines in a reproducable way. Although Vagrant is wonderful, you may desire a development
environment in which the application server runs on your local machine, in which case you may want to read `README.md`
and the Wiki on BitBucket.

These instructions should work equally well on Windows, Linux, or macOS once Vagrant is installed, however they were
developed on macOS so slight modifications may be necessary for Windows or Linux.

## Dependencies

To obtain the Cormack JMS source code from BitBucket, you can download a ZIP, however the suggested method is to use
git, which you may need to install.

You will need both VirtualBox and Vagrant installed on the host machine. At present (6 Jan 2020), Vagrant does not yet
support VirtualBox 6.1; the recommended alternative is to use VirtualBox 6.0 instead.

- [Download VirtualBox from virtualbox.org](https://www.virtualbox.org/wiki/Downloads)
- [Download Vagrant from vagrantup.com](https://www.vagrantup.com/downloads.html)

Run `vagrant -v` and `VBoxManage -v` in a terminal window to ensure that they were installed correctly.

## Build the Environment

Obtain the source code from BitBucket, then open a terminal/command prompt window, change directory into the source code
directory, and run:

```bash
vagrant up
```

A number of things will happen. The `Vagrantfile` in the source directory defines two virtual machines named `db` and
`web`, and it will start both of them (`db` first then `web`, because the app will attempt to connect to the database
when it starts):

- The `db` machine is a fairly standard PostgreSQL 11 server configured to allow access over TCP.
- The `web` machine is configured with the necessary tools to manage the database and run this app. Specifically, those
  tools are:
    - **virtualenv**, for managing python versions and dependencies.
    - **bower**, for managing static asset dependencies in the `static/bower_components` folder.
    - Python and Postgres header files to allow `pip` from virtualenv to build `psycopg2`.

Once configured, Vagrant will display a message that the server is running, but it is necessary to setup the database.

Two things are worth noting about the setup environment at this point:

1. The web server is running at [http://localhost:8000/](http://localhost:8000/) or
   [http://10.5.5.5:8000/](http://10.5.5.5:8000/), but there are no tables in the database and you will not be able to
   log in.
2. The database is accessible at [10.5.5.11:5432](postgresql://postgres:postgres@10.5.5.11:5432/cormack_jms) with a
   postgres client; username `postgres`, password `postgres`.
3. The `/vagrant` folder is synced to the repository folder, so any changes made in the repository folder while the VM
   is running will be synced to the VM and any changes made in `/vagrant` will be synced to the host.
   
   This is useful because Django will automatically reload the server when a file is changed, so you can use a text
   editor on the host machine (e.g. in Windows) to edit files and then the changed code will appear on the Linux server
   and the web app will reload itself.

   The logs for the web app are synced as well to the `logs` folder. On a UNIX host machine, you can run
   `tail -f logs/20200106_163001.log` (for example) and find live output from the Django app server.
4. It is possible to get a BASH console on the web server by running `vagrant ssh` should you wish to do some manual
   provisioning.

## Setup the Database

At this point, the app server is running, so it is possible to go to http://localhost:8000 and see the web app, but:

1. No tables for the database are present.
2. No users are in the database, so we can't log in.

Experienced Django users may recognize that the reason for (1) is that we have not migrated the database. There are two
ways to do so: the classical Django way and via a provisioner in the Vagrantfile.

### Migrate: The Django Way

To migrate using the builtin Django tools, we need to be able to run commands on the server. Run `vagrant ssh` and you
will be presented with a command prompt. Run the following commands to change directory to the source directory and
activate the python 3 virtualenv for this web app:

```bash
cd /vagrant
source env/app/activate
```

Now, you can migrate the database with

```bash
python manage.py migrate
```

Once the database is migrated, create a superuser with:

```bash
python manage.py createsuperuser
```

You will be asked for a username, email, and password.

### Migrate: The Vagrant Way

For reproducability reasons, we provide a non-default provisioner in Vagrant to perform the migration. On the host
machine, run:

```bash
vagrant provision --provision-with migrate,create-superuser
```

This will do the same thing as above, but without having to ssh into the machine. Since this provisioner is not
interactive, the default values for the superuser are:

- username: admin
- password: cormack
- email: cormack@hordernit.com.au

## In-App Setup

Regardless of which migration method you use, you will need to add a role for the admin user to allow access to the job
schedule and other resources.

1. Point your web browser at http://localhost:8000/ and log in as the admin user you just set up.
2. Click on the menu in the navbar at the top right, which should show the admin user's email address. Then click on
   __Admin Dashboard__; another login screen will open in a new tab.
3. Log in again, and click on __Users and Roles__. Click on the gray __Add a User and Role__ button at top right.
4. Fill out the form as follows:
   - In the __User__ dropdown, choose `admin`.
   - Check the __Is Active__ checkbox.
   - Check the __Administrator__ checkbox.
5. Press Save
6. Close the new tab, click on the menu in the navbar at the top right again, and click __Logout__.
7. Log in again using the admin credentials.

If everything went right, you should see new options for Jobs and Repairs.

**At this point, the app should be ready for testing.**

----

## Available Provisioners

There are several provisioners in the `Vagrantfile` that are not strictly necessary to get the app running but are
useful for software development. Due to the nature of software and the speed at which code changes, it may be more
expedient to read the `Vagrantfile` to find out what they do, however some documentation is provided here as well.

### bower

The bower provisioner is used to install static dependencies; usually this is run using `bower install`, but should you
not have bower installed on the host machine, you can run it in the virtual machine with

```bash
vagrant provision --provision-with bower
```

Note that this provisioner is run by default when the VM is set up for the first time, so any changes that you may have
made in the `static/bower_components` folder will be overwritten.

### drop-database

The drop-database provisioner drops the `cormack_jms` database.

```bash
vagrant provision --provision-with drop-database
```

### start-server

The start-server provisioner creates the `cormack_jms` database if it does not exist, then starts the Django server.
This is run every time the VM starts up, so you should not need to run it unless you have used `stop-server` or the app
server has crashed.

Note that it is necessary to run with the option `0:8000` to bind to all addresses; if starting the server manually you
may have to pass this option to allow the web browser on the host computer to access the app.

```bash
vagrant provision --provision-with start-server
```

### stop-server

The stop-server provisioner stops the application server, which may be desirable if you make some major changes.

```bash
vagrant provision --provision-with stop-server
```

### migrate

The migrate provisioner ensures that the Postgres database includes a database named `cormack_jms`, then applies the
Django migrations with `python manage.py migrate`.

```bash
vagrant provision --provision-with migrate
```

### create-superuser

The create superuser provisioner creates a superuser with the username `admin`, email `cormack@hordernit.com.au`, and
password `cormack`.

```bash
vagrant provision --provision-with create-superuser
```

