function LessonSummaryXBlock(runtime, element, initArgs) {
    var blockId = initArgs.block_id;
    var userDashboardURL = initArgs.user_dashboard_url;
    var renderHtmlHandlerUrl = runtime.handlerUrl(element, 'render_html');

    $(function ($) {

        $.ajax({
            type: "POST",
            url: renderHtmlHandlerUrl,
            data: JSON.stringify(''),
            success: function(response) {
                $('#main-content-' + blockId, element).html(response.content);
                $('.button-previous-' + blockId, element).click(function() {
                    $('.sequence-nav-button.button-previous').get(0).click();
                });
                $('.button-next-' + blockId, element).click(function() {
                    window.location.href = userDashboardURL;
                });
            }
        });
    });
}
