/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

(function () {
    angular
        .module('app.ocom')
        .factory("formStateService", [function () {
            var _loaded = [];
            var _formState = defaultFormState();

            return {
                isLoaded: isLoaded,
                setLoaded: setLoaded,
                formState: getFormState, // DO NOT USE use getFormState
                getFormState: getFormState,
                setFormState: setFormState,
                resetFormState: resetFormState
            };

            /**
             * Set Loaded status for model
             * @param {string} model: the model name
             * @param {boolean} status: the status to set
             */
            function setLoaded(model, status) {
                _loaded[model] = status;
            }

            /**
             * Used by loaded function for checking if api was called and loaded
             * @param {string } name the key (or api name)
             */

            function _isloaded(name) {
                if (angular.isDefined(_loaded[name])) {
                    return _loaded[name];
                } else {
                    return false;
                }
            }

            /**
             * Return if api name or list of names are loaded previously (either through cache or api)
             * @param {string | Array} nameOrList
             */
            function isLoaded(nameOrList) {
                if (typeof nameOrList === "string") {
                    return _isloaded(nameOrList)
                } else {
                    for (var i = 0; i < nameOrList.length; i++) {
                        if (!_isloaded(nameOrList[i])) {
                            return false;
                        }
                    }
                    return true;
                }
            }

            /**
             * Return Form state flag
             * @param {string} state the name of the flag to check
             * @returns {boolean | null} the flag state
             */
            function getFormState(state) {
                if (_formState.hasOwnProperty(state)) {
                    return _formState[state];
                } else {
                    return null;
                }
            }

            /**
             * Set form states based on flagObj
             * @param {object} flagObj the state to set as an object of boolean flags
             */
            function setFormState(flagObj) {
                for (var attribute in flagObj) {
                    if (_formState.hasOwnProperty(attribute)) {
                        _formState[attribute] = flagObj[attribute];
                    }
                }
            }

            /**
             * Return default values for form state
             */
            function defaultFormState() {
                return {
                    loading: false,
                    saving: false,
                    deleting: false,
                    saveOk: false,
                    deleteOk: false,
                    gotError: false,
                    invalid: false,     // we may also rely on form.$invalid but this flag can handle custom validation
                    loadedLookups: false
                };
            }

            /**
             * Reset form state to default value
             */
            function resetFormState() {
                _formState = defaultFormState();
            }
        }])
})();
