/* JavaScript for Vertical Student View. */
window.VerticalStudentView = function(runtime, element) {
    'use strict';
    var setSpentTime = runtime.handlerUrl(element, 'set_seating_time');
    var $element = $(element);
    var $forcedSeatingTimerElement = $element.find('.forced-seating-timer');
    var pingTimedelta = $forcedSeatingTimerElement.data('pingTimedelta');
    var forcedSeatingTime;
    var pingIdInterval;
    var timerIdInterval;

    var getFormattedTime = function(forcedSeatingTime) {
        if (forcedSeatingTime < 0)
            forcedSeatingTime = 0;
        var hours = parseInt(forcedSeatingTime / 3600);
        var minutes = parseInt(forcedSeatingTime / 60) % 60;
        var seconds = Math.floor(forcedSeatingTime % 60);
        return hours + ":" + (minutes < 10 ? "0" + minutes : minutes)
            + ":" + (seconds < 10 ? "0" + seconds : seconds);
    };

    var updateForcedSeatingTime = function() {
        forcedSeatingTime --;
        $forcedSeatingTimerElement.text(getFormattedTime(forcedSeatingTime));
        if (forcedSeatingTime <= 0){
            setSpendTime(true);
            clearInterval(timerIdInterval);
        }
    };

    function setSpendTime(pageClose=false) {
        if (pageClose) {
            clearTimeout(pingIdInterval);
        }

        $.ajax({
            type: "POST",
            url: setSpentTime,
            contentType: 'application/x-www-form-urlencoded ',
            data: {page_close: pageClose},
            headers: {
                'X-CSRFToken': $.cookie('csrftoken')
            },
            success: function(response) {
                var forcedSeatingTimeLeft = response.forced_seating_time_left;
                var isSeatingTimeFinished = response.is_seating_time_finished;
                clearTimeout(pingIdInterval);
                if (isSeatingTimeFinished) {
                    clearInterval(timerIdInterval);
                    $element.find('.forced-seating-timer-enabled').addClass('is-seating-time-finished');
                } else if (forcedSeatingTimeLeft) {
                    forcedSeatingTime = forcedSeatingTimeLeft;
                    clearInterval(timerIdInterval);
                    timerIdInterval = setInterval(updateForcedSeatingTime, 1000);
                    pingIdInterval = setTimeout(setSpendTime, pingTimedelta);
                    updateForcedSeatingTime();
                }
            }
        });
    }

    var onSequenceChange = function onSequenceChange() {
        setSpendTime(true);
        $('.sequence').off('sequence:change', onSequenceChange);
    };

    if ($forcedSeatingTimerElement.length) {
        $('.sequence').on('sequence:change', onSequenceChange);

        window.addEventListener('beforeunload', function() { setSpendTime(true) });
        pingIdInterval = setTimeout(setSpendTime, pingTimedelta);
        setSpendTime();
    }

    RequireJS.require(['course_bookmarks/js/views/bookmark_button'], function(BookmarkButton) {
        var $element = $(element);
        var $bookmarkButtonElement = $element.find('.bookmark-button');

        return new BookmarkButton({
            el: $bookmarkButtonElement,
            bookmarkId: $bookmarkButtonElement.data('bookmarkId'),
            usageId: $element.data('usageId'),
            bookmarked: $element.parent('#seq_content').data('bookmarked'),
            apiUrl: $bookmarkButtonElement.data('bookmarksApiUrl')
        });
    });
};
