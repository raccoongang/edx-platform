(function(define) {
    'use strict';

    define([], function() {
        return function(options) {
            if (!options.enabled) {
                return;
            }

            var checkActivity = function() {
                var timer;
                var events = ['click', 'mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

                window.addEventListener('load', resetTimer, true);
                events.forEach(function(event) {
                    document.addEventListener(event, resetTimer, true);
                });

                function redirect() {
                    location.href = '/';
                }

                function resetTimer() {
                    clearTimeout(timer);
                    timer = setTimeout(redirect, options.timeout || 600000);
                }
            };

            window.onload = checkActivity;
        };
    });
}).call(this, define || RequireJS.define);
