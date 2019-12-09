# Installation

## Download

> git submodule add query https://ocom.repositoryhosting.com/git/ocom/django_query.git

## Add to INSTALLED_APPS
in config/settings/base.py

> 'query',

## Add Resources to index.html

        <script src="js/query/services/angular.query.service.js?ver=X.XX.XX"></script>
        <script src="js/query/services/dexie.query.js?ver=X.XX.XX"></script>
        <script src="js/query/directives/query.directives.js?ver=X.XX.XX"></script>

## Migrations

Make sure you run

> manage.py migrate query


## In static/js/app.module.js add
To the modules to include in angularjs

> 'ocom.query',

## Add to urls
```
from query.router import urlpatterns as query_routes

...

url(r'^query/', include(query_routes)),
```


## To use Query_Def CRUD
Add to index.html
```
        <script src="app/query_def/module.js?ver=0.00.0"></script
        <script src="app/query_def/list.controller.js?ver=0.00.0"></script>
        <script src="app/query_def/form.controller.js?ver=0.00.0"></script>
```

# Usage in Client

When calling dataAPIService.getDataApi(..).list()

Pass a {query:queryJSON} where queryJSON is the Query in JSON format to use.

# Usage in Django

Add to ViewSets

> filter_backends = (QueryFilter,)

# Add filter UI to /list pages

    <query-ui model-name="api.Job" query="listOptions.query" apply="reloadList()"></query-ui>

o model-name = The name of the model
o query = Is Query in JSON format to "edit"
o apply = The Function to call when the user clicks apply

# UI-Router
You will need to adjust your ui-router route to add a parameter like so

> url: "/list?offset&limit&ordering&sort&order&q&searchField&filter&{query:json}",

Where "query" is your parameter for the Query. This will enable the JSON to be in the URL.