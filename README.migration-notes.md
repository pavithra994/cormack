# Notes on Migration to Fix Docker

These are my notes when from when I inherited this project to fix some of the issues with the way in which the project was Dockerized. For questions, email Robert Howe, rc@rchowe.com.

## 1. Setup SSL

The project (rightly) does not ship with SSL certificates for docker-compose to use. Therefore, once the project is cloned to a new location, we have to generate the necessary files. Run the following commands to do so (if you do not have a machine with `openssl` or are running Windows, I suggest running `docker run --rm -v $(pwd)/config:/config -it ubuntu` to get a Linux console then `apt update && apt install openssl` to install `openssl`).

Once you have a Linux console with `openssl`, run the following commands to generate `.crt`, `.key`, and `dhparam.pem` files:

```bash
openssl req -new -x509 -sha256 -nodes \
    -out config/ssl/jms.cormackgroup.com.au.crt \
    -keyout config/ssl/jms.cormackgroup.com.au.key
openssl dhparam 2048 -out config/ssl/dhparam.pem
```

**NOTE: Be sure not to ship the generated SSL certs or commit them to git.**

## 2. Install necessary components

I had to run `bower install` in the project root directory and `npm install` in the `static` directory to get the Angular components downloaded. YMMV.

I also had to run `git submodule init; git submodule update` to install OCOM.

## 3. Run the app

To start the app the first time, run:

```bash
docker-compose up
```

If you make some changes and want them to be applied to the app in docker, you have to run `docker-compose build` and then `docker-compose down` and `docker-compose up`. Note that unless you run `docker-compose down -v`, certain persistent volumes will NOT be deleted and you will at least (a) still have the database from the old version and (b) may still have the SSL certs from the old version.