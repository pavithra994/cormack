# dataService
This is the OLD original service.
**Please migrate code off this** 

# dataAPIService
**This is the service to USE**
This service provides methods to manage data without exposing HOW

## method: _getResource
Should not be used...

## method: list
Get a list of Items limited and offset to be paged.

## method: getItem
Get the item buy ID

## method: createItem
Create a new item in the database

## method: updateItem
Update the item in the database using the ID

## method: delete
Delete the item from the database.

## method: query
These are operations NOT available offline...

# offlineDataService
This service stores data in dexie and keeps it offline..

Each operations is recorded in the Synclog table

## SyncLog entries
Each syncLog entry has the following:
- modelName: The name of the model
- modelId: The Id of the item in the model on our database
- operation: What Operation happened (see below)
- when: the Date it happened so we can order the operations properly.

## Operations
- UPDATE : the most common update to existing data (assume data came from the REST API)
- CREATE : When a new item is created. This should not happen too often here
- DELETE: If the item is deleted it will be recorded here. 
- NOOP  : If the item is CREATED then DELETEd then it will be changed to NOOP as there is no need to send to server.


## method: getChanges
Get a list of SyncLog entries for changes.

Makes sure that only one operation per Item is in the list so that for example multiple "updates" become 1 operation.

## method: executeLog
Apply a change from the SyncLog back to the REST api using the dataResourceService

#dataResourceService
This service uses the $resource from Angular to talk to the Django Rest Services

