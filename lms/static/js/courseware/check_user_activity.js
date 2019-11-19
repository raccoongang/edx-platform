(function(define) {
    'use strict';

    define([], function() {
        return function(options, url) {
            if (!options.enabled) {
                return;
            }

            var timerIdInterval;

            var checkActivity = function() {
                var timerIdTimeout;
                var events = ['click', 'mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'];

                resetTimer();
                events.forEach(function(event) {
                    document.addEventListener(event, resetTimer, true);
                });

                function redirect() {
                    location.href = '/';
                }

                function resetTimer() {
                    clearTimeout(timerIdTimeout);
                    timerIdTimeout = setTimeout(redirect, options.timeout || 600000);
                }
            };

            function setSpendTime(pageClose=false) {
                if (pageClose) {
                    clearTimeout(timerIdInterval);
                }
                $.ajax({
                    url: url,
                    type: 'POST',
                    contentType: 'application/x-www-form-urlencoded ',
                    data: {page_close: pageClose},
                    headers: {
                        'X-CSRFToken': $.cookie('csrftoken')
                    },
                })
            }

            window.onload = checkActivity;
            window.addEventListener('beforeunload', function() { setSpendTime(true) });
            timerIdInterval = setInterval(setSpendTime, 60000);
            setSpendTime();
        };
    });
}).call(this, define || RequireJS.define);
