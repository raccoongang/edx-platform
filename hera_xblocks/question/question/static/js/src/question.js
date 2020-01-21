/* Javascript for QuestionXBlock. */
function QuestionXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');

    $(function ($) {
        var $confidenceInfo = $(".confidence-text.info", element);
        var $confidenceInput = $(".confidence-input", element);
        var $scaffolds = $(".scaffolds", element);
        var $blockScaffold = $(".scaffold-info", element);
        var $closeBtn = $(".js-close-scaffold-btn", element);
        var $skipBtn = $('.skip', element);
        var $questionForm = $(".question-form", element);
        var $questionSlider = $(".image-slider", element);
        var $scaffoldHelpImage = $(".scaffold_help_image", element);
        var $questionContent = $(".question__content", element);
        var $submit = $('.submit', element);

        $('[name=answer]', element).on("change blur keyup", function() {
            $confidenceInfo.removeClass("hidden");
            $confidenceInput.removeClass("hidden is-not-valid");
            $submit.removeAttr("disabled");
            $confidenceInfo.text(init_args.confidence_text);
        });

        $submit.bind('click', function (e) {
            if ($confidenceInput.val() && $confidenceInput.is(':valid')){
                var answer = $questionForm.serializeArray();
                var confidence = $(".confidence-input", element).val();
                if (init_args.question.questionType == "text" || init_args.question.questionType == "number"){
                    answer = answer[0].value;
                } else {
                    answer = answer.map(function(el) {
                        return el.value;
                    });
                }
                $.post(
                    submithHandlerUrl,
                    JSON.stringify({"answer": answer, "confidence": confidence})
                ).done(function (response) {
                    if (response === true) {
                        $skipBtn.addClass("hidden");
                        $scaffolds.addClass("hidden");
                        $confidenceInfo.text(init_args.correct_answer_text);
                    }
                    else {
                        $skipBtn.removeClass("hidden");
                        $scaffolds.removeClass("hidden");
                        $confidenceInfo.text(init_args.incorrect_answer_text);
                    }
                    $confidenceInput.addClass("hidden");
                    $(e.currentTarget).attr('disabled', 'disabled');
                });
            } else {
                $confidenceInput.addClass("is-not-valid");
            };
        });

        $('.scaffold', element).bind('click', function (event) {
            scaffoldData = $(event.target).data();

            $blockScaffold.removeClass("hidden");
            // TODO: need to substitute img and description for mascot
            // $(".scaffold-img", element).attr('src', scaffoldData.imgUrl);
            // $(".scaffold-description", element).html("Some text");

            $questionForm.addClass("hidden");
            $scaffoldHelpImage.html('');
            if (scaffoldData.imgUrls && scaffoldData.imgUrls.length) {
                var needShowImageBlock = false;
                scaffoldData.imgUrls.split(' ').forEach((el, ind) => {
                    if (el) {
                        needShowImageBlock = true;
                        $scaffoldHelpImage.append('<img src="' + el + '" alt="Scaffold help image"/>');
                    }
                });
                if (needShowImageBlock) {
                    $questionSlider.addClass("hidden");
                    $scaffoldHelpImage.removeClass("hidden");
                }
            }
            $questionContent.html(scaffoldData.content);
            $closeBtn.removeClass("hidden");
        });

        $('.try_again', element).bind('click', function (event) {
            $blockScaffold.addClass("hidden");
            $questionForm.removeClass("hidden");
            $questionContent.html(init_args.description);
        });

        $closeBtn.bind('click', function (event) {
            $scaffoldHelpImage.addClass("hidden");
            $questionSlider.removeClass("hidden");
            $closeBtn.addClass("hidden");
        });


        $(document).ready(function() {
            $('.show-simulation', element).click(function(e) {
                var iframeUrl = $(e.currentTarget).data('iframeUrl');
                $('.simulation-overlay', element).find('iframe').attr('src', iframeUrl);
                $('.simulation-overlay', element).fadeIn(300);
            });

            $('.simulation-close-btn', element).click(function() {
                $('.simulation-overlay', element).fadeOut(300);
            });

            $('.image-slider', element).slick({
                infinite: false,
                arrows: true,
                adaptiveHeight: true
            });
        });
    });
}
