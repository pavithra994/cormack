# Add these lines to index.html
Add these lines below to the index.html that loads resources from the ocom submodule

## CSS
for CSS
```
    <!--Styles-->
    <link href="node_modules/bootstrap/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="node_modules/bootstrap/dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <link href="node_modules/angular-loading-bar/build/loading-bar.min.css" rel="stylesheet">
    <link href="node_modules/angular-growl-v2/build/angular-growl.min.css" rel="stylesheet">
    <link href="node_modules/sweetalert/lib/sweet-alert.css" rel="stylesheet">
    <link href="node_modules/font-awesome/css/font-awesome.css" rel="stylesheet">
    <link href="node_modules/textangular/dist/textAngular.css" rel="stylesheet">
    <link href="node_modules/ng-tags-input/build/ng-tags-input.min.css" rel="stylesheet">
    <link href="node_modules/ng-tags-input/build/ng-tags-input.bootstrap.min.css" rel="stylesheet">
    <link href="node_modules/ui-select/dist/select.min.css" rel="stylesheet">
```

## JavaScript
For Javascript

```
    <!--Requirements-->
    <script src="node_modules/jquery/dist/jquery.min.js"></script>
    <script src="node_modules/lodash/lodash.min.js"></script>
    <script src="node_modules/moment/min/moment.min.js"></script>
    <script src="node_modules/moment/locale/en-au.js"></script>
    <script src="node_modules/moment-timezone/builds/moment-timezone-with-data.min.js"></script>
    <script src="node_modules/bootstrap/dist/js/bootstrap.min.js"></script>
    <script src="node_modules/angular/angular.min.js"></script>
    <script src="node_modules/@uirouter/angularjs/release/angular-ui-router.min.js"></script>
    <script src="node_modules/angular-messages/angular-messages.min.js"></script>
    <script src="node_modules/angular-animate/angular-animate.min.js"></script>
    <script src="node_modules/angular-resource/angular-resource.min.js"></script>
    <script src="node_modules/angular-loading-bar/build/loading-bar.min.js"></script>
    <!--<script src="node_modules/angular-bootstrap/ui-bootstrap.min.js"></script> &lt;!&ndash;0.12.1 &ndash;&gt;-->
    <!--<script src="node_modules/angular-bootstrap/ui-bootstrap-tpls.min.js"></script> &lt;!&ndash;0.12.1 &ndash;&gt;-->
    <script src="node_modules/angular-ui-bootstrap/dist/ui-bootstrap.js"></script> <!-- 2.5.6 -->
    <script src="node_modules/angular-ui-bootstrap/dist/ui-bootstrap-tpls.js"></script> <!-- 2.5.6 -->
    <script src="node_modules/angular-strap/dist/angular-strap.min.js"></script>
    <script src="node_modules/angular-strap/dist/angular-strap.tpl.min.js"></script>
    <script src="node_modules/angular-growl-v2/build/angular-growl.min.js"></script>
    <script src="node_modules/sweetalert/lib/sweet-alert.min.js"></script>
    <script src="node_modules/angular-sweetalert/SweetAlert.min.js"></script>
    <script src="node_modules/angular-sanitize/angular-sanitize.min.js"></script>
    <script src="node_modules/ngstorage/ngStorage.min.js"></script>

    <script src="node_modules/angular-moment/angular-moment.min.js"></script>
    <script src="node_modules/angular-jwt/dist/angular-jwt.min.js"></script>
    <script src="node_modules/ng-file-upload/dist/ng-file-upload.min.js"></script>
    <script src="node_modules/ng-file-upload/dist/ng-file-upload-all.min.js"></script>
    <script src="node_modules/angular-ui-date/dist/date.js"></script>
    <script src="node_modules/angular-ui-sortable/dist/sortable.min.js"></script>
    <script src="node_modules/angular-ui-sortable-multiselection/dist/sortable.min.js"></script>
    <script src='node_modules/textangular/dist/textAngular-rangy.min.js'></script>
    <script src='node_modules/textangular/dist/textAngular-sanitize.min.js'></script>
    <script src='node_modules/textangular/dist/textAngular.min.js'></script>
    <script src='node_modules/textangular/dist/textAngularSetup.js'></script>
    <script src="node_modules/dexie/dist/dexie.min.js"></script>
    <script src="node_modules/ng-dexie/build/ng-dexie.min.js"></script>
    <script src="node_modules/html2canvas/dist/html2canvas.min.js"></script>
    <script src="node_modules/angular-filter/dist/angular-filter.min.js"></script>
    <script src="node_modules/ng-tags-input/build/ng-tags-input.min.js"></script>
    <script src="node_modules/ui-select/dist/select.min.js"></script>
```

Ocom Javascript

```
    <!-- Ocom Module -->
    <script src="js/ocom/ocom.module.js?ver=0.00.0"></script> <!-- the base Module -->
    <script src="js/ocom/services/platform.web.service.js?ver=0.00.0"></script> <!-- Use for Web based app. Use platform.mobile for offline apps-->
    <!-- <script src="js/ocom/services/platform.mobile.service.js?ver=0.00.0"></script> --> <!-- Use for Mobile based app. Use platform.web for online only apps-->
    <script src="js/ocom/ocom.config.js?ver=0.00.0"></script> <!-- Basic app configs and defaults -->
    <script src="js/ocom/ocom.filters.js?ver=0.00.0"></script> <!-- Set of basic Filters to use -->
    <script src="js/ocom/authentication/auth.alt.module.js?ver=0.00.0"></script> <!-- Services etc for Authentication using jwt -->
    <script src="js/ocom/authentication/role.service.js?ver=0.00.0"></script> <!-- Role service - to be replaced with PermissionService -->
    <script src="js/ocom/services/alerts.service.js?ver=0.00.0"></script> <!-- The Service to show Alerts etc -->
    <script src="js/ocom/services/input.service.js?ver=0.00.0"></script> <!-- Directives for Widgets -->
    <script src="js/ocom/services/stateStorage.service.js?ver=0.00.0"></script> <!-- Stores State of UI-Route changes to return back to list etc -->
    <script src="js/ocom/services/cache.service.js?ver=0.00.0"></script> <!-- A hash caching service -->
    <script src="js/ocom/services/formstate.service.js?ver=0.00.0"></script> <!-- Formstate service - I think we need to remove this -->
    <script src="js/ocom/services/CodeTableCache.service.js?ver=0.00.0"></script> <! Service to cache getting Code tables -->
    <script src="js/ocom/services/dataAPI.service.js?ver=0.00.0"></script> <!-- DataAPIService -->
    <script src="js/query/services/angular.query.service.js?ver=0.00.0"></script> <!-- Angular service to use query json -->
    <script src="js/query/services/dexie.query.js?ver=0.00.0"></script> <!-- Code to use querys on Dexie data -->
    <script src="js/query/directives/query.directives.js?ver=0.00.0"></script> <!-- Directives to Edit a Query -->
    <!-- <script src="js/ocom/services/data.service.js?ver=0.00.0"></script> --><!-- OLD data service please stop using -->
    <script src="js/ocom/services/widget.service.js?ver=0.00.0"></script> <!-- Widget Services -->
    <!-- <script src="js/ocom/widgets/ocom-update.alt.js?ver=0.00.0"></script> --><!-- Use ocom-form-buttons instead -->
    <!-- <script src="js/ocom/widgets/ocom-create.js?ver=0.00.0"></script> --><!-- don't use - use ocom-form-buttons instead -->
    <script src="js/ocom/widgets/forms/ocom-form-buttons.js?ver=0.00.0"></script> <!-- The Action buttons at the bottom of forms for Update/Save and close etc -->
    <script src="js/ocom/widgets/ocom-table.js?ver=0.00.0"></script><!-- Ocom Table directive for /list pages -->
    <!-- <script src="js/ocom/widgets/ocom-list-group.directive.js?ver=0.00.0"></script> --> <!-- Not sure this is used -->
    <script src="js/ocom/widgets/ocom-file-upload.js?ver=0.00.0"></script> <!-- Use file_upload submodule instead -->
    <script src="js/ocom/widgets/dates/ocom-datetime-picker.js?ver=0.00.0"></script> <!-- Ocom Date and Time pickers -->
    <!-- <script src="js/ocom/widgets/dates/ocom-required-datetime-picker.js?ver=0.00.0"></script> --><!-- Don't use this use the above and set required attribute Ocom Date and Time pickers for fields required-->
    <!-- <script src="js/ocom/widgets/forms/ocom-input.js?ver=0.00.0"></script> --><!-- DONT Use this! :) -->
    <script src="js/ocom/widgets/forms/input-focus.directive.js?ver=0.00.0"></script> <!-- Directive to change focus on forms -->
    <script src="js/ocom/widgets/forms/dirty-tracking.directive.js?ver=0.00.0"></script> <!-- Provides message if they try and close a dirty form screen -->
    <script src="js/ocom/widgets/forms/list.directive.js?ver=0.00.0"></script> <!-- Directives to add/remove and move items in a table/list. -->
    <script src="js/ocom/widgets/lists/sortable.directive.js?ver=0.00.0"></script> <!-- Directives to sort table contents -->
    <script src="js/ocom/layout/footer.controller.js?ver=0.00.0"></script> <!-- Controller for footer in layout -->
    <script src="js/ocom/layout/nav.controller.js?ver=0.00.0"></script> <!--Controller for the Nav in the layout -->
    <script src="js/ocom/layout/content.controller.js?ver=0.00.0"></script> <!-- Controller for the Content of the Layout -->
    <script src="js/ocom/layout/resizer.directive.js?ver=0.00.0"></script> <!-- Directive to have reszier on the screen -->
    <script src="js/ocom/layout/scrollSync.directive.js?ver=0.00.0"></script> <!-- Directive to Sync the Scrolling of two divs -->
    <script src="js/ocom/widgets/ui-select-infinite.directive.js?ver=0.00.0"></script> <!-- Directive to ui-select to keep loading data for scrolling??? -->
    <script src="js/ocom/layout/profile/profile.controller.js?ver=0.00.0"></script> <!-- Controller to View Profile -->
    <script src="js/ocom/layout/profile/change_password.controller.js?ver=0.00.0"></script> <!-- Controller to Change Password -->
```