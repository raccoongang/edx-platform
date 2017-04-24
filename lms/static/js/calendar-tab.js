(function ($) {
  $(document).ready(function () {
    $('#calendar-init').on('click', function () {
      var jqxhr = $.post(initCalendarUrl, {courseId: courseId})
        .done(function () {
          location.reload();
        })
        .fail(function () {
          console.error("An error occured during google calendar initialization.");
        })
    });

    scheduler.config.show_loading = true;
    scheduler.init('scheduler_here', new Date(), "month");
    scheduler.load("events/", "json");

    var dp = new dataProcessor("dataprocessor/");
    dp.init(scheduler);
    dp.setTransactionMode("POST", false);
  });
})(jQuery);
