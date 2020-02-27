function QuestionXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var skipHandlerUrl = runtime.handlerUrl(element, 'skip');
    var renderHtmlHandlerUrl = runtime.handlerUrl(element, 'render_html');

    $.post(renderHtmlHandlerUrl, '{}').done(function(response) {
        $('#main-question-content', element).html($.parseHTML(response.content))

        $(function ($) {
            var $confidenceInfo = $(".confidence-text.info", element);
            var $confidenceInput = $(".confidence-input", element);
            var $scaffolds = $(".scaffolds", element);
            var $blockScaffold = $(".scaffold-info", element);
            var $closeBtn = $(".js-close-scaffold-btn", element);
            var $skipBtn = $('.skip', element);
            var $questionForm = $(".question-form", element);
            var $questionSlider = $(".image-holder", element);
            var $scaffoldHelpImage = $(".scaffold_help_image", element);
            var $questionContent = $(".question__content", element);
            var $submit = $('.submit', element);
            var $questioonsImageWrapper = $('.questions-image-wrapper', element);
            var $questionWrapper = $('.questions-wrapper', element);
            var invalidChars = ["-", "+", "e", "E"];
            var isSubmissionAllowed = init_args.is_submission_allowed;
            var blockId = init_args.block_id;

            $('input', element).on("change blur keyup", function() {
                if (isSubmissionAllowed) {
                    $confidenceInfo.removeClass("hidden");
                    $confidenceInput.removeClass("hidden is-not-valid");
                    $submit.removeAttr("disabled");
                    $confidenceInfo.text(init_args.confidence_text);
                }
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
                        isSubmissionAllowed = response.is_submission_allowed;
                        if (response.correct) {
                            $skipBtn.addClass("hidden");
                            $scaffolds.addClass("hidden");
                            $confidenceInfo.text(init_args.correct_answer_text);
                        }
                        else if (isSubmissionAllowed) {
                            $scaffolds.removeClass("hidden");
                            $confidenceInfo.text(init_args.incorrect_answer_text);
                        }
                        $confidenceInput.addClass("hidden");
                        $confidenceInfo.addClass("hidden");
                        $(e.currentTarget).attr('disabled', 'disabled');
                    });
                } else {
                    $confidenceInput.addClass("is-not-valid");
                }
            });

            $('input[type=number]').on('keypress', function(e) {
                if (invalidChars.includes(e.key)) {
                    e.preventDefault();
                }
            });

            $('.js-scaffold-button', element).bind('click', function (event) {
                var scaffoldData = $(this).data();
                var contentID = '#' + scaffoldData.scaffoldName + '-' + blockId;
                var scaffoldimages = '';
                var needShowImageBlock = false;
                $skipBtn.removeClass("hidden");

                var scaffoldContent = $(contentID).html();

                $questionWrapper.removeClass('is-teach is-break is-rephrase');

                if (scaffoldData.imgUrls && scaffoldData.imgUrls.length) {
                    scaffoldData.imgUrls.split(' ').forEach((el, ind) => {
                        if (el) {
                            needShowImageBlock = true;
                            scaffoldimages+='<img src="' + el + '" alt="Scaffold help image"/>';
                        }
                    });
                }
                // do we need to rerender the images block
                if (needShowImageBlock) {
                    $questioonsImageWrapper.removeClass('is-teach is-break is-rephrase');
                    $questioonsImageWrapper.addClass(scaffoldData.scaffoldClassName);
                    $scaffoldHelpImage.html(scaffoldimages);
                    $questionSlider.addClass("hidden");
                    $scaffoldHelpImage.removeClass("hidden");
                    $closeBtn.removeClass("hidden");
                }
                // do we need to rerender the content block
                if (scaffoldContent.trim().length > 0) {
                    $questionWrapper.addClass(scaffoldData.scaffoldClassName);
                    $questionContent.html(scaffoldContent);
                    $blockScaffold.removeClass("hidden");
                    $questionForm.addClass("hidden");
                    $scaffolds.addClass('hidden');
                }
            });

            $('.try_again', element).bind('click', function (event) {
                $blockScaffold.addClass("hidden");
                $questionForm.removeClass("hidden");
                $questionContent.html(init_args.description);
                $questionWrapper.removeClass('is-teach is-break is-rephrase');
                $scaffolds.removeClass('hidden');
            });

            $closeBtn.bind('click', function (event) {
                $questioonsImageWrapper.removeClass('is-teach is-break is-rephrase');
                $scaffoldHelpImage.addClass("hidden");
                $questionSlider.removeClass("hidden");
                $closeBtn.addClass("hidden");
            });

            $skipBtn.bind('click', function (event) {
                $.post(
                    skipHandlerUrl, JSON.stringify({"skip": true})
                ).done(function(response) {
                    isSubmissionAllowed = response.is_submission_allowed;
                    $confidenceInput.addClass("hidden");
                    $confidenceInfo.addClass("hidden");
                    $submit.attr('disabled', 'disabled');
                    }
                ).error(function(error){
                    console.log(error);
                });
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
            });

            $('.button-next-' + blockId, element).click(function() {
                console.log('click')
                $('.sequence-nav-button.button-next').get(0).click();
            });
            $('.button-previous-' + blockId, element).click(function() {
                $('.sequence-nav-button.button-previous').get(0).click();
            });
        });
    });
}
