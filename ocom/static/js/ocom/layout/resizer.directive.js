/*
 * Copyright (C) 2019 Ocom Software- All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Written by Ocom Software <licence@ocom.com.au, 2019
 *
 */

// from http://plnkr.co/edit/Zi2f0EPxmtEUmdoFR63B?p=preview
angular.module('app.ocom').directive('resizer', function($document, $localStorage) {

	return function($scope, $element, $attrs) {

		var storageKey = null;

		var newSize = 0;

		if ("resizerDefault" in $attrs) {
			newSize = parseInt($attrs.resizerDefault || "300"); // Get init size from here if there is one or use 300 so it's not 0
		}

		if ("resizerKey" in $attrs) {
			resizerKey = $attrs.resizerKey;
			var newSize = $localStorage[resizerKey] || newSize; // From storage OR from default
		}

		if (newSize) {
			if ($attrs.resizer == 'vertical') {
				resizeVertical(newSize);
			}
			else {
				resizeHorizontal(newSize);
			}
			// set size to key
		}

		$element.on('mousedown', function(event) {
			event.preventDefault();

			$document.on('mousemove', mousemove);
			$document.on('mouseup', mouseup);
		});

		function resizeVertical(x) {
			if ($attrs.resizerMax && x > $attrs.resizerMax) {
				x = parseInt($attrs.resizerMax);
			}

			if (resizerKey) {
				$localStorage[resizerKey] = x;
			}

			$element.css({
				left: x + 'px'
			});

			$($attrs.resizerLeft).css({
				width: x + 'px'
			});
			$($attrs.resizerRight).css({
				left: (x + parseInt($attrs.resizerWidth)) + 'px'
			});
        }

		function resizeHorizontal(y) {
			if (resizerKey) {
				$localStorage[resizerKey] = y;
			}

			$element.css({
				bottom: y + 'px'
			});

			$($attrs.resizerTop).css({
				bottom: (y + parseInt($attrs.resizerHeight)) + 'px'
			});
			$($attrs.resizerBottom).css({
				height: y + 'px'
			});
		}

		function mousemove(event) {

			if ($attrs.resizer == 'vertical') {
				// Handle vertical resizer
				var x = event.pageX;

				resizeVertical(x);

			} else {
				// Handle horizontal resizer
				var y = window.innerHeight - event.pageY;

				resizeHorizontal(y);
			}
		}

		function mouseup() {
			$document.unbind('mousemove', mousemove);
			$document.unbind('mouseup', mouseup);
		}
	};
});
