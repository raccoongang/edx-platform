function LessonSummaryXBlock(runtime, element, initArgs) {
    var blockId = initArgs.block_id;
    var userDashboardURL = initArgs.user_dashboard_url;
    $(function ($) {
        $('.button-previous-' + blockId, element).click(function() {
            $('.sequence-nav-button.button-previous').get(0).click();
        });
        $('.button-next-' + blockId, element).click(function() {
            window.location.href = userDashboardURL;
        });
    });
}
