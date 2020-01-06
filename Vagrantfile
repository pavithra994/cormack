# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure("2") do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # This is the primary web server box, which runs the app.
  config.vm.define "web", primary: true do |web|

    # Every Vagrant development environment requires a box. You can search for
    # boxes at https://vagrantcloud.com/search.
    web.vm.box = "ubuntu/bionic64"

    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine. In the example below,
    # accessing "localhost:8080" will access port 80 on the guest machine.
    # NOTE: This will enable public access to the opened port
    web.vm.network "forwarded_port", guest: 8000, host: 8000

    # Create a private network, which allows host-only access to the machine
    # using a specific IP.
    web.vm.network "private_network", ip: "10.5.5.5"

    # Provider-specific configuration so you can fine-tune various
    # backing providers for Vagrant. These expose provider-specific options.
    web.vm.provider "virtualbox" do |vb|
      # Display the VirtualBox GUI when booting the machine
      vb.gui = false
    
      # Customize the amount of memory on the VM:
      vb.memory = "4096" # 4 GB
    end
    #
    # View the documentation for the provider you are using for more
    # information on available options.

    # Enable provisioning with a shell script. Additional provisioners such as
    # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
    # documentation for more information about their specific syntax and use.
    web.vm.provision "shell", inline: <<-SHELL
      wget -qO - 'https://download.docker.com/linux/ubuntu/gpg' | apt-key add
      add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

      apt-get update
      apt-get install -y docker-ce docker-compose virtualenv libpq-dev python3-dev nodejs npm build-essential
      npm install -g bower

      # Configure docker so that the vagrant user can use it.
      systemctl start docker
      systemctl enable docker
      groupadd docker
      usermod -aG docker vagrant

      # Add db to /etc/hosts
      echo '10.5.5.11 db' >> /etc/hosts

      cd /vagrant

      # Configure virtualenv
      rm -rf env
      virtualenv -p python3 env
      source env/bin/activate
      pip install -r requirements.txt
    SHELL

    web.vm.post_up_message = <<-MESSAGE
      The environment is ready. However, you still need to log in, possibly
      migrate the database, and start the web server. On the host machine, run
      `vagrant ssh` to get in, then:
      
        cd /vagrant
        source env/bin/activate
        python manage.py migrate
        python manage.py runserver 0:8000
      
      Once the server is running, it is accessible at one of the following
      addresses:

        http://localhost:8000/
        http://10.5.5.5:8000/
      
      Happy development!
      Robert Howe <rc@rchowe.com>
      Hordern IT
    MESSAGE
  end

  # This is the database box, which is just a postgres database.
  config.vm.define "db" do |db|

    # Every Vagrant development environment requires a box. You can search for
    # boxes at https://vagrantcloud.com/search.
    db.vm.box = "ubuntu/bionic64"

    # Create a forwarded port mapping which allows access to a specific port
    # within the machine from a port on the host machine. In the example below,
    # accessing "localhost:8080" will access port 80 on the guest machine.
    # NOTE: This will enable public access to the opened port
    #db.vm.network "forwarded_port", guest: 5432, host: 15432

    # Create a private network, which allows host-only access to the machine
    # using a specific IP.
    db.vm.network "private_network", ip: "10.5.5.11"

    # Provider-specific configuration so you can fine-tune various
    # backing providers for Vagrant. These expose provider-specific options.
    db.vm.provider "virtualbox" do |vb|
      vb.gui = false
      vb.memory = 1024
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
      sed -i.bak "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/11/main/postgresql.conf
      echo 'host  all  all 0.0.0.0/0 md5' >> /etc/postgresql/11/main/pg_hba.conf
      systemctl restart postgresql.service
    SHELL
  end
end
