/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

// inspired by https://stackoverflow.com/a/9236351/150953
angular.module('app.ocom').directive('scollSync', function($document) {

	/* usage <div scroll-sync="#otherDiv" scroll-x="true" scroll-y="false">..

		Will scroll the otherDiv on the X axis if this div is scrolled on X
		using scroll-x and scroll-y you can limit to just the ONE axis.

		IMPROVEMENTS: Handle attributes better..
	 */
	return function($scope, $element, $attrs) {
		var scrollX = !($attrs.scrollX === "false");
		var scrollY = !($attrs.scrollY === "false");

		$element.on('scroll', function(event) {

			var other = $attrs.scollSync;

			if (scrollX) {
                $(other).scrollLeft($(event.target).scrollLeft());
            }
            if (scrollY) {
                $(other).scrollTop($(event.target).scrollTop());
            }
		});
	};
});
