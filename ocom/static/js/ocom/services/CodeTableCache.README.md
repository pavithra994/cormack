# CodeTableCache Service

This service is to assistin loading Code tables uses the "modified_date" to determine if the entries are updated


## Service
Fetched the code table from the $localstorage and using $http. If there is data in localstorage calls the callback twice.
Once with the results from localstorage and then again with the ajax response (because that should be slower)

When the ajax response comes back it updates localstorage so its has it for next time.


### method: primeCache(uri, modelName)

Use the dataAPIService to load the data for the model into $localstorage

### method: fetchFromCache(uri, modelName, callback)

This is the main method. It will call the callback when it has data from $localstorae and the ajax call

### method: processLoadTables(loadTables, scope)

Process the loadTables array (from cacheService) into the scope variable (usually $scope.options)

The loadTables expects an array of Objects like

{uri: "", name:"", keyBy""}

Where
- uri is the URI to use ie '/api/'
- name is the Name of the model ie "code_item"
- keyBy is optional and if specifies creates an dict in the scope with the name of the field ie item_code_by_id
- callback - is Optional (and not recommended as this prefilters data) runs the response through this callback
- params (is optional) is passed to the callback above.


## Directive load-code-table
Usage:
```html
    <div load-code-table="code_items" options="options" uri="/api/" key-by="id">

        <select ng-if="!options.loading_code_items" ng-option="... from options.code_items">
        <span ng-if="options.loading_code_items">Loading...</span>
    </div>
```

The directive will load data from /api/code_items the results will be put into option.code_items
If the optional key-by attribute is present it will also add to options the key "code_items_by_id" which is a dict of the items keyed by the ID

While it's loading it will set the ```options.loading_code_items = true``` so the UI can show a loading message.
Once it has some data (ie from localstorage or Ajax it will set this key to ```false```