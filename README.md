# Cormack Concreting Job Management System 


## Admin Access
In order to gain access to the Administrator dashboard (in the case of vagrant/local dev setup, it is usually in 
[http://127.0.0.1/admin/](http://127.0.0.1/admin/)), you need to add a superuser account using the console command:
````
python manage.py createsuperuser
```` 
Afterwards, you can use that account to log in thru the Admin Dashboard. Take note that in order for this account to have 
regular access, you need to assign a <strong>Role</strong> for it in the Admin Dashboard (check out the Roles & User menu).

## Versioning
After every major / minor / patch, run the commands to update the version. 
Workflow example [here](http://kylepurdon.com/blog/a-python-versioning-workflow-with-bumpversion.html).
````
bumpversion patch --commit --allow-dirty
git push origin master --tags
````

##  Application
In order to run the application, you'll just have to
1. Create a virtualenv
```
pip virtualenv env
```
2. Activate the virtualenv
```
source env/bin/activate
```
3. Install python packages
```
pip install -r requirements.txt
```
4. Create the initial data
```
sudo -u postgres -i psql -f Your Project Dir/provision/clear_db.sql
python manage.py migrate
```
5. For deployment with a web server, set DEBUG = False on your settings.py and run the following
```
python manage.py collectstatic
```
6. For local development, run the server with Django and check the output
```
python manage.py runserver
```

## Required Records
The following CodeTable records need to exist in order to allow full-functionality of the JMS. 
Use The Admin Dashboard and add these records below:
### CodeSubbieType
```
1.  Code: supplier
    Description: Supplier (or any other description)

2.  Code: employee
    Description: Employee (or any other description)

3.  Code: subcontractor
    Description: Sub-Contractor (or any other description)
```

You may also run the following command on the console to upload these records to the database:
```
python manage.py loaddata api/fixtures/codeSubbieType.json
```

For testing purposes, you may also run the following command on the console for the source used in Email Loader:
```
python manage.py loaddata api/fixtures/django_inbox_dev.json
```

Optionally, you may run the command below to add pre-defined data for the CodeTaskType table:
```
python manage.py loaddata api/fixtures/codeTaskType.json
```

 
##  Bower modules
The bower packages required by this project can be installed by doing
```
bower install
```

## Django REST Framework
Sample Query Parameters
````
http://localhost:8000/employee/?limit=5&offset=0&ordering=[-]code&%3Cfilter_field%3E=%3Cfilter_q%3E
# Filtering by descending order - add (-) to the ordering field
````

## More Notes
AngularJS Structure
- Scaffold
	- utils/errorHandling
	- utils/listHandling
	- /directives/alertModule
	- /directives/date-picker
	- /directives/listModule
	- /directives/select-key
	- /services/flashService
	- /services/djangoService

## PostgreSQL DB Setup
```
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
```

## Coverage
```
coverage run --source='.' manage.py test api
```

## Submodules
For this application:
* Django-ocom
    
```
git submodule init
git submodule update
```

## JWT-based Authentication
Repository: https://github.com/GetBlimp/django-rest-framework-jwt

Documentation: http://getblimp.github.io/django-rest-framework-jwt/

Frontend: https://github.com/auth0/angular-jwt

Obtaining a token for access
````
curl -X POST -d "username=admin&password=password123" http://localhost:8000/api-token-auth/

# access restricted endpoint via:
curl -H "Authorization: JWT <your_token>" http://localhost:8000/protected-url/
````

Verifying validity of token
````
curl -X POST -H "Content-Type: application/json" -d '{"token":"<EXISTING_TOKEN>"}' http://localhost:8000/api-token-verify/
````

## Bower Save Packages
Use the supplied bower.json file or create your own with the command

    bower init

Then save new dependencies to your bower.json with 

    bower install <PACKAGE> --save


## Running Tests
1. Live Test (Selenium)
    ````
    python manage.py test tests.live
    ````
    Note: Live tests make use of selenium and google chrome as the browser. Screenshots
    can be found in the tests/screenshots folder and html dumps can be found in the tests/html folder.

2. Standard Test
    ````
    python manage.py test tests.standard
    ````
3. Unit Test (In Progress)
    ````
    python manage.py test tests.unit
    ````
