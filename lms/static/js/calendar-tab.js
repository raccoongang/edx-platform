(function ($) {
  $(document).ready(function () {

    scheduler.config.show_loading = true;
    scheduler.init('scheduler_here', new Date(), "month");
    scheduler.load("events/", "json");

    var dp = new dataProcessor("dataprocessor/");
    dp.init(scheduler);
    dp.setTransactionMode("POST", false);
  });
})(jQuery);
