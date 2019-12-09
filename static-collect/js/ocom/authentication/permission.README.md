# Permission Service

This code takes the Group permissions and the User's permissions and creates and access_map that is used checked to see if access to a state or field is denied.

# NOTE
The permission.service.ui-router.v1.0.js file is for use with ui-router 1.X and above. Please try and upgrade to 1.X

## Events: $stateChangeStart

The code will catch this UI-Router event and till check for a DENY permission.

If the user has DENY permission for the State then a sweetAlert will pop up telling them Access is denied

If the state has the field "allow_annonymous" set to true then the user will be allowed to go to that state (this is for Login etc)
## Methods

### can_goto_state (stateName)

Checks if the user can go to that State.
Use this method to determine if an <a> should be visible.

Used by the ui-router "beforeChange" event to check if the user can


### get_has_permission (modelName)

Returns a Curried function that can be added to a $scope that has the current State already set.
The function will call has_permission with the statename already filled in


### has_permission (stateName, model, field, action)

Checks if there is a permission entry for the StateName, modelName, Field Name and Action

Action is "READ" or "UPDATE"

## Directive: can-goto-state

Usage
```html
<div can-go-to-state="item.list">.. <div>
```

If the user can go to the state specified by name then it will show render the contents else nothing appears
Uses ng-if.


## Directive: disabled-can-goto-state

Usage
```html
<div disabled-can-go-to-state="item.list">.. <div>
```

If the user cannot go to the state specified by name then it will use ng-disable to disable the HTML
Uses ng-disabled.


## Directive: perm-can-read
Usage
```html
<div perm-can-read="fieldnameFromModel" model="model-name" >,,,</div>
```

Will show/hide the contents if the user has permission for the field in the model for the current state.

uses ng-if interally.

## Directive: perm-can-update
Usage
```html
<input perm-can-update="fieldnameFromModel" model="model-name" >,,,</input>
```

Will disable the input if the user doesn't have permission for the field in the model for the current state.

uses ng-disabled internally.
NOTE: will not work on ocom-date=picker etc..