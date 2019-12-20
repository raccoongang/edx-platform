/* Javascript for QuestionXBlock. */
function QuestionXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');

    $(function ($) {
        var $confidenceInfo = $(".confidence-text.info", element);
        var $confidenceInput = $(".confidence-input", element);
        var $scaffolds = $(".scaffolds", element);
        var $blockScaffold = $(".scaffold-info", element);
        var $close = $(".scaffold-img-close-btn", element);
        var $skip = $('.skip', element);
        var $questionForm = $(".question-form", element);
        var $questionImage = $(".question__image", element);
        var $questionContent = $(".question__content", element);
        var $submit = $('.submit', element);

        $('[name=answer]', element).on("change blur keyup", function() {
            $confidenceInfo.removeClass("hidden");
            $confidenceInput.removeClass("hidden is-not-valid");
            $submit.removeAttr("disabled");
            $confidenceInfo.text(init_args.confidence_text)
        });

        $submit.bind('click', function () {
            if ($confidenceInput.val() && $confidenceInput.is(':valid')){
                var answers = $questionForm.serializeArray();
                var confidence = $(".confidence-input", element).val();
                $.post(submithHandlerUrl, JSON.stringify({"answers":answers, "confidence":confidence})).done(function (response) {
                    if (response === true) {
                        $skip.addClass("hidden");
                        $scaffolds.addClass("hidden");
                        $confidenceInfo.text(init_args.correct_answer_text);
                    }
                    else {
                        $skip.removeClass("hidden");
                        $scaffolds.removeClass("hidden");
                        $confidenceInfo.text(init_args.incorrect_answer_text);
                    }
                    $confidenceInput.addClass("hidden");
                });
            } else {
                $confidenceInput.addClass("is-not-valid");
            };
        });

        $('.scaffold', element).bind('click', function (event) {
            scaffoldData = $(event.target).data();

            $blockScaffold.removeClass("hidden");
            // TODO: need to substitute img and description for mascot
            // $(".scaffold-img", element).attr('src', scaffoldData.img_url);
            // $(".scaffold-description", element).html("Some text");

            $questionForm.addClass("hidden");
            $questionImage.attr('src', scaffoldData.img_url);
            $questionContent.html(scaffoldData.content);
            $close.removeClass("hidden");
        });

        $('.try_again', element).bind('click', function (event) {
            $blockScaffold.addClass("hidden");

            $questionForm.removeClass("hidden");
            $questionContent.html(init_args.description);
        });

        $close.bind('click', function (event) {
            $close.addClass("hidden");
            $questionImage.attr('src', init_args.img_url);
        });


        $(document).ready(function() {
            $('.show-simulation', element).click(function() {
               $('.simulation-overlay', element).fadeIn(300);
            });
         
            $('.simulation-close-btn', element).click(function() {
               $('.simulation-overlay', element).fadeOut(300);
            });
        });
    });
}
