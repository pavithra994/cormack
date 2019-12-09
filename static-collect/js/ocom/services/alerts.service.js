/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    /**
     * A service for show messages and alerts - Handles all it for the scope
     */
    angular
        .module('app.ocom')
        .factory('alerts', alerts);

    function alerts(growlMessages, growl) {
        var alerts = {};

        alerts.flash = {};

        var growlMapping = {
            danger: "error", // Used to translate BS to growl
            error: "error",
            warning: "warning",
            success: "success",
            info: "info"
        };


        function _showMessageNow(message) {
            var serverity = message.severity = growlMapping[message.severity] || "error"; // Normalize

            growl[serverity](message.text); // Show NOW
        }

        alerts.getMessage = function () {
            var value = this.flash.messages;
            this.flash.messages = null;

            console.log(value);

            return value;
        };

        function alreadyPubished(message, list) {
            var found = false;
            angular.forEach(list, function (msg) {
                if (msg.text == message.text && msg.severity == message.severity)
                    found = true;
            });

            return found;
        }

        alerts.push = function (message) {
            if (this.flash.messages === null || angular.isUndefined(this.flash.messages)) {
                this.flash.messages = [];
            }

            message.severity = growlMapping[message.severity] || "danger"; // Normalize

            _showMessageNow(message);

            if (!alreadyPubished(message, this.flash.messages))
                this.flash.messages.push(message);
        };

        alerts.error = function (text, later) {
            if (typeof later === 'undefined') later = false;

            this.addMessage({severity: 'danger', text: text}, later);
        };
        alerts.danger = function (text, later) { // Alias
            alerts.error(text, later);
        };
        alerts.success = function (text, later) {
            if (typeof later === 'undefined') later = false;

            this.addMessage({severity: 'success', text: text}, later);
        };
        alerts.info = function (text, later) {
            if (typeof later === 'undefined') later = false;

            this.addMessage({severity: 'info', text: text}, later);
        };
        alerts.warning = function (text, later) {
            if (typeof later === 'undefined') later = false;

            this.addMessage({severity: 'warning', text: text}, later);
        };

        /* Clear all the Growl Messages */
        alerts.clearMessages = function () {
            growlMessages.destroyAllMessages();
        };

        alerts.showNow = function () {
            var flashMessage = alerts.getMessage();
            if (flashMessage) {
                alerts.addMessages(flashMessage, false);
            }
        };

        alerts.currentScope = null;

        alerts.addMessage = function (message, later) {
            console.log(message);

            message.severity = growlMapping[message.severity] || "danger"; // Normalize

            if (later) {
                alerts.push(message);
            }
            else { // Show Now
                _showMessageNow(message);

                if (alerts.currentScope && !alreadyPubished(message, alerts.currentScope.messages)) {
                    alerts.currentScope.messages.push(message);
                }
            }
        };

        alerts.addMessages = function (messages, later) {
            angular.forEach(messages, function (msg) {
                alerts.addMessage(msg, later);
            });
        };

        /* Handle NEW Scope - setup Scope for Alert directive and growl messages*/
        alerts.changeScope = function ($scope) {
            alerts.currentScope = $scope;

            if (angular.isUndefined($scope.message)) {
                $scope.messages = [];
            }

            $scope.closeMessage = function (index) { // For the Close/Cross on the screen
                $scope.messages.splice(index, 1);
            };

            // If there are message in Flash then show them NOW.
            this.showNow();
        };

        return alerts;
    }
})();
