/* Javascript for QuestionXBlock. */
function QuestionXBlock(runtime, element) {

    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');

    $(function ($) {
        // Initialize the plugin
        $('#iframe').popup();

        // Set default `pagecontainer` for all popups (optional, but recommended for screen readers and iOS*)
        $.fn.popup.defaults.pagecontainer = '.author-block__content'


        $(element).find('#submit').bind('click', function () {
            var answer = $('#question').serializeArray();
            debugger;
            $.post(submithHandlerUrl, JSON.stringify(answer)).done(function (response) {
                if (response === true) {
                    alert('OK');
                }
                else {
                    alert('Not OK');
                }
            });
        });
    });
}
