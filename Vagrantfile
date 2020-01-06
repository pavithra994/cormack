# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  # This is the database box, which is just a postgres database.
  # We define the database first so that it is loaded before the web server.
  config.vm.define "db" do |db|
    db.vm.box = "ubuntu/bionic64"

    # Create a private network, which allows host-only access to the machine using a specific IP.
    db.vm.network "private_network", ip: "10.5.5.11"

    # The database server does not need to be particularly high-spec, so we run it with 1 GB of memory.
    db.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 1024 # 1 GB
    end

    # Install and configure postgres.
    config.vm.provision "shell", inline: <<-SHELL
      # Add the Postgres repository
      echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list
      wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -

      # Install Postgres
      apt-get update -qq &>/dev/null
      apt-get install -qq -o=Dpkg::Use-Pty=0 postgresql-11 &>/dev/null

      # Configure Postgres
      sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres'"
      sed -i.bak "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/11/main/postgresql.conf
      echo 'host  all  all 0.0.0.0/0 md5' >> /etc/postgresql/11/main/pg_hba.conf
      systemctl restart postgresql.service
    SHELL
  end

  # This is the primary web server box, which runs the app.
  config.vm.define "web", primary: true do |web|
    web.vm.box = "ubuntu/bionic64"

    # We forward port 8000 so that developers can access the web app through their local machine if they so wish, e.g.
    # by going to http://localhost:8000. Note that if you are trying to do multiple things at once, this will interfere
    # with other things on port 8000 on your local machine.
    web.vm.network "forwarded_port", guest: 8000, host: 8000

    # Create a private network, which allows host-only access to the machine using a specific IP.
    web.vm.network "private_network", ip: "10.5.5.5"

    web.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 4096 # 4 GB
    end
    
    # The default provisioner to install the dependencies and start the machine.
    web.vm.provision "shell", inline: <<-SHELL
      apt-get update -qq > /dev/null
      apt-get install -qq virtualenv libpq-dev python3-dev nodejs npm build-essential > /dev/null
      npm install -g bower

      # Add db to /etc/hosts
      echo '10.5.5.11 db' >> /etc/hosts
    SHELL

    # Set up virtualenv.
    #
    # Note that we remove env and replace it with one from the VM -- this is to attempt to avoid any conflicts with a
    # possible env from the host machine. If the user has done any environment customization it will be removed.
    web.vm.provision "virtualenv", type: "shell", inline: <<-VIRTUALENV
      cd /vagrant

      rm -rf env
      virtualenv -p python3 env
      source env/bin/activate
      pip install -q -r requirements.txt
    VIRTUALENV

    # Install bower dependencies
    web.vm.provision "bower", type: "shell", privileged: false, inline: <<-BOWER
      cd /vagrant
      bower install
    BOWER

    # An optional provisioner for performing the database migration, should the user not want to ssh into the machine
    # to perform the migration.
    #
    # We don't migrate by default because the user may have made cutomizations to the database.
    web.vm.provision "migrate", type: "shell", run: "never", privileged: false, inline: <<-MIGRATE
      cd /vagrant
      source env/bin/activate

      # Create the cormack_jms database if it does not exist
      export PGPASSWORD=postgres
      psql -h db -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'cormack_jms'" \
        | grep -q 1 \
        || psql -h db -U postgres -c "CREATE DATABASE cormack_jms"
      
      python manage.py migrate --no-input
    MIGRATE

    # An optional provisioner for creating the administrator user.
    # The default parameters are:
    #   username: admin
    #   email:    cormack@hordernit.com.au
    #   password: cormack
    #
    # We can't use `python manage.py createsuperuser` in this migration because there is no way of programmatically
    # setting the password.
    web.vm.provision "create-superuser", type: "shell", run: "never", privileged: false, inline: <<-ADMIN
      cd /vagrant
      source env/bin/activate

      username=admin
      email=cormack@hordernit.com.au
      password=cormack

      python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'cormack@hordernit.com.au', 'cormack')"
      if [ $? -eq 0 ]; then
        echo
        echo "Created superuser:"
        echo "  username: $username"
        echo "     email: $email"
        echo "  password: $password"
        echo
      else
        echo 1>&2
        echo "Unable to create superuser." 1>&2
        echo 1>&2
        exit 1
      fi
    ADMIN

    # An optional provisioner to drop the database.
    web.vm.provision "drop-database", type: "shell", run: "never", privileged: false, inline: <<-END
      PGPASSWORD=postgres psql -h db -U postgres -c "DROP DATABASE cormack_jms"
    END

    # A provisioner to start the server.
    web.vm.provision "start-server", type: "shell", run: "always", privileged: false, inline: <<-START
      cd /vagrant
      source env/bin/activate

      # Create the cormack_jms database if it does not exist
      export PGPASSWORD=postgres
      psql -h db -U postgres -tc "SELECT 1 FROM pg_database WHERE datname = 'cormack_jms'" \
        | grep -q 1 \
        || psql -h db -U postgres -c "CREATE DATABASE cormack_jms"

      mkdir -p /vagrant/logs
      python manage.py runserver 0:8000 &> /vagrant/logs/$(date +"%Y.%m.%d_%H%M%S")_cormack.log &
    START

    # A provisioner to start the server.
    web.vm.provision "stop-server", type: "shell", run: "never", privileged: false, inline: <<-STOP
      ps ax | grep "python manage.py runserver 0:8000" | grep -v "grep" | cut -f 1 -d' ' | xargs kill
    STOP

    # A message for new developers once the machine boots.
    web.vm.post_up_message = <<-MESSAGE
    The Vagrant environment is ready. The Cormack JMS web server is
    accessible at the following addresses:

      http://localhost:8000/
      http://10.5.5.5:8000/
    
    If this is your first setup for this environment, you will likely
    need to migrate the database. A Vagrant provisioner to do so is
    provided; on the host computer run the command:

      $ vagrant provision --provision-with migrate,create-superuser
    
    This will migrate the database and create the superuser in the
    database with the following credentials:

      username: admin
      password: cormack
    
    Once logged in, you will have to go to the Admin Dashboard and
    create a role for yourself to have access to the job schedule and
    other resources. This role should have the following permissions:

      - IsActive
      - Administrator
    
    Once the role is created, log out and log back in.

    The default configuration runs as a development environment
    (config/settings/dev.py), and will reload the web server when a
    change is detected. You should be able to use your favorite text
    editor to change project files on your machine and have your
    changes reflected in the virtual machine.

    Additional provisioners are available to control the web server,
    as well as `vagrant ssh` for more direct control. See the Vagrant
    section in README.md.

    Happy development!
    Robert Howe <rc@rchowe.com>
    Hordern IT

    MESSAGE
  end
end
