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
        var $scaffoldContent = $('.author-block__content', element);
        var invalidChars = ["-", "+", "e", "E"];

        $('input', element).on("change blur keyup", function() {
            $confidenceInfo.removeClass("hidden");
            $confidenceInput.removeClass("hidden is-not-valid");
            $submit.removeAttr("disabled");
            $confidenceInfo.text(init_args.confidence_text);
        });

        $submit.bind('click', function (e) {
            if ($confidenceInput.val() && $confidenceInput.is(':valid')){
                var confidence = $confidenceInput.val();
                var serializedForm = $questionForm.serializeArray();
                var userAnswers = [];
                for (var i in init_args.problem_types) {
                    userAnswers.push([]);
                }
                for (var i in serializedForm) {
                    userAnswers[serializedForm[i].name].push(serializedForm[i].value);
                }
                $.post(
                    submithHandlerUrl,
                    JSON.stringify({"answers": userAnswers, "confidence": confidence})
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

        $('input[type=number]').on('keypress', function(e) {
            if (invalidChars.includes(e.key)) {
                e.preventDefault();
            }
        });

        $('.scaffold', element).bind('click', function (event) {
            var scaffoldData = $(this).data();
            $blockScaffold.removeClass("hidden");
            $scaffoldContent.removeClass('is-teach is-break is-rephrase');
            var contentID = '#' + scaffoldData.scaffoldName + '-' + init_args.location_id;
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
            $scaffoldContent.addClass(scaffoldData.scaffoldClassName);
            $questionContent.html($(contentID).html());
            $closeBtn.removeClass("hidden");
        });

        $('.try_again', element).bind('click', function (event) {
            $blockScaffold.addClass("hidden");
            $questionForm.removeClass("hidden");
            $questionContent.html(init_args.description);
            $scaffoldContent.removeClass('is-teach is-break is-rephrase');
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
