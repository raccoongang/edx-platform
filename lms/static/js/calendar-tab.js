(function ($) {
  $(document).ajaxStart(function () {
    $("#loading").show("slow");
  });
  $(document).ready(function () {
    $('#event-btn').on('click', function () {
      $('#event-form').toggleClass("hidden");
    });
    $('#calendar-init').on('click', function () {
      var jqxhr = $.post(initCalendarUrl, {courseId: courseId})
        .done(function () {
          location.reload();
        })
        .fail(function () {
          console.error("An error occured during google calendar initialization.");
        })

    })

  });
})(jQuery);
