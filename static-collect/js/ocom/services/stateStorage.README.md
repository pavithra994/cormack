#State Storage
There are two implementations.

stateStorage.service.js is for the older pre 1.0 version of ui-router ie v0.3.2
stateStorage.service.ui-router-v1.0.js is for ui-router 1.0

*Please try and use ui-router 1.X in new projects *

# Version Pre 1.X
The way this works is we notify the stateStorage service we are going to change state using the "storeStateThenGo" method

We also use the updateStateParams method in the onEnter method of the state to configure the params based on the last $stateParams value.

This code will not work in ui-router 1.0 for various reasons.

# Version 1.X and Beyond    .

This code has a stateStorageService for backwards compatility of the storeStateThenGo method.

The way this works is it uses the transitions.onBefore hook to do all the work.

If the state names to and from are the same then we don't do anything. This could be a change in the list filter for example..

If the from State has the following in the config ie
```javascript
                .state('item.list', {
                    url: "/list?offset&limit&ordering&sort&order&searchField&filter&q",
                    templateUrl: "app/item/list.html",
                    controller: "ItemListController",
                    data: {
                        store_state:true
                    }
                })
```

If the state we are leaving has data.store_state == true then we store the current state into the sessionStorage

Finally it will look for params for the To State in session storage and will set the params to the value in sessionstorage. If the params changed (ie an undefined param is set to a value from the sessionStorage param) then it will tell ui-router change again.
