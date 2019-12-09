# Ocom Base App
This app used django-rest-framework and django-rest-framework-jwt for authentication. 

## Features

### Authentication
The django-rest-framework-jwt library is used as the helper function for implementing jwt-based authentication. (See: https://github.com/GetBlimp/django-rest-framework-jwt)

````
# 1. Install auth framework: 

$ pip install djangorestframework-jwt
See docs at: http://getblimp.github.io/django-rest-framework-jwt/

The auth endpoints can now be accessed inside static app

# 2. Then, add the following in base settings file

REST_FRAMEWORK = {
    'COERCE_DECIMAL_TO_STRING': False,
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'DEFAULT_FILTER_BACKENDS': ('rest_framework.filters.DjangoFilterBackend',
                                'rest_framework.filters.OrderingFilter',
                                'rest_framework.filters.SearchFilter',),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ),
}


JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER':
    'ocom.utils.auth_override.jwt_response_payload_handler',

    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
````

### Base Models
Below is a short description of the Base Models to use

#### OcomModel
This model is the basis for all Ocom models. It adds Modified and Update dates. These can be useful to track changes to the models
 
#### ListModel
 A ListModel is a used in a Table/List of child objects. For example if we have an Invoice model the InvoiceLines which represents the lines in the invoice. This model should inherit from ListModel

#### ActiveModel
This model has Active Start Date and End Date. Use this model to add these fields. It also helps us later on to "detect" the fields so we can set ActiveEndDate instead of "deleting" the model
 
#### CodeModel
This model should be used for "Code" tables. Usually you don't need to add fields but it this Blue Print has a Code, Description and Active Date range this is the Model to use.


### Views
####OcomModelViewSet
The OcomModelViewSet will set the active_end_date to the current date/time instead of deleting the model.

### Admin
####ActiveListFilter
This filter can be used in the Admin section to show just Active models (ie ones that inherit from ActiveModel)


### Utility Functions

#### filter_queryset
This function can be use to filter the Model using the standard parameters we use. It also allows filtering by Active and All Items.



## How to use ocom base app in an existing django application: 
````
# Add ocom app as submodule inside project
git submodule add <https..git url>
git submodule update
git submodule sync

# Include urls in main app

````

## Dependencies
TODO: remove unnecessary libraries
* Python Backend
    * [Django](https://www.djangoproject.com/)
        Currently supports version 1.10
    * [Django REST Framework (DRF)](http://www.django-rest-framework.org)
        Ajax API Endpoints
    * [DRF JWT](https://github.com/GetBlimp/django-rest-framework-jwt)
        Json Web Token (JWT) Auth support for DRF
    * [pyJWT](https://github.com/jpadilla/pyjwt)
        JWT Implementation for python
    * [DRF Writable Nested](https://github.com/beda-software/drf-writable-nested)
        Serializer utility for DRF
    * [psycopg](http://initd.org/psycopg/)
        PostgresQL adapter for python
    * [coverage](https://coverage.readthedocs.io/)
        Testing and Code Coverage
    * [raven](https://docs.sentry.io/clients/python/)
        Error-reporting (Sentry)
    * [requests](http://docs.python-requests.org/en/master/)
        HTTP library/utility
    * [router](https://pypi.python.org/pypi/router/0.1)
        Routing utility
    * [bumpversion](https://github.com/peritus/bumpversion)
        App Versioning
    * [dateutil](https://dateutil.readthedocs.io/en/stable/)
        Date/time utility
    * [pytz](http://pytz.sourceforge.net/)
        Date/time utility
    * [Django Filter](https://django-filter.readthedocs.io/en/develop/guide/rest_framework.html)
        Filters for DRF
    * [Django Suit](http://djangosuit.com/)
        Django Admin page UI enhancement
* Javascript Frontend
    * [jQuery](http://jquery.com/)
        Library required by other js and angular packages listed
    * [lodash](https://lodash.com/)
        Object manipulation library
    * [jQuery UI](https://jqueryui.com/)
        UI library built on top of jQuery
    * [Bootstrap](http://getbootstrap.com/)
        Responsive UI Library
    * [AngularJs](https://angularjs.org/)
        Framework
    * [SweetAlert](http://t4t5.github.io/sweetalert/)
        Alert UI replacement. Required by ngSweetAlert
    * [Moment.js](https://momentjs.com/)
        Date/Time utility. Required by angular-moment
* External Angular Components 
    * [AngularUI Router](https://github.com/angular-ui/ui-router)
        SPA Routing
    * [angular-loading-bar](https://github.com/chieffancypants/angular-loading-bar)
        Loading/Progress Bar UI
    * [ui-date directive](https://github.com/angular-ui/ui-date)
        DatePicker UI
    * [AngularStrap](http://mgcrea.github.io/angular-strap/)        
        General UI
    * [angular-growl-2](https://github.com/JanStevens/angular-growl-2)        
        Notifications UI
    * [ngSweetAlert](https://github.com/oitozero/ngSweetAlert)        
        SweetAlert wrapper for Angular
    * [angular-moment](https://github.com/urish/angular-moment)
        Angular directive and filters for moment.js
    * [angular-jwt](https://github.com/auth0/angular-jwt)
        JWT Utility
    * [Cached Resource](https://github.com/goodeggs/angular-cached-resource)
        Caching
    * [Angular-filter] (https://www.npmjs.com/package/angular-filter)
        A set of filters already written

# Permission UI

## Include in index.html and dev_index.html
### For new projects or ui-router version >= 1.0
```html
<script src="app/group_permissions/module.js?ver=0.00.0"></script>
<script src="app/group_permissions/list.controller.js?ver=0.00.0"></script>
<script src="app/group_permissions/form.controller.js?ver=0.00.0"></script>
```
### If ui-router version < 1.0
```html
<script src="app/group_permissions/module.pre-v.1.0.js?ver=0.00.0"></script>
<script src="app/group_permissions/list.controller.js?ver=0.00.0"></script>
<script src="app/group_permissions/form.controller.js?ver=0.00.0"></script>
```

## Add to /static/app.module.js
    'app.group_permissions',

## Yarn
The Ocom submodule require AngularJs packages that are installed via *yarn*. Instructions on how to install *yarn* 
on your local dev server are located [here](https://yarnpkg.com/lang/en/docs/install/#windows-stable).

In order for the packages to be installed, proceed to the ocom/static subdirectory and run:
```bash
yarn
```

## Notes
On production, don't forget to set DEBUG=False on settings.py (unless you don't want to use a web server to serve static 
content). You may also want to generate a different secret key so auth data and encrypted content is exclusive to that 
application.