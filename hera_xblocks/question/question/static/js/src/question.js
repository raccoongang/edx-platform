function QuestionXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var skipHandlerUrl = runtime.handlerUrl(element, 'skip');
    var renderHtmlHandlerUrl = runtime.handlerUrl(element, 'render_html');
    var scaffoldPaymentHandlerUrl = runtime.handlerUrl(element, 'scaffold_payment');

    var scaffolds = init_args.scaffolds;
    var blockId = init_args.block_id;
    var skipped = false;

    function getUserAnswers($form) {
        var userAnswers = [];
        var serializedForm = $form.serializeArray();
        for (var i in init_args.problem_types) {
            userAnswers.push([]);
        }
        for (var i in serializedForm) {
            userAnswers[serializedForm[i].name].push(serializedForm[i].value);
        }
        return userAnswers;
    }

    function changeFeedbackMessage(message) {
        $('#feedback-message-' + blockId, element).text(message);
    }

    function showFeedback() {
        $('.feedback-open', element).attr('disabled', false);
        $('.feedback-holder').addClass('tooltip-is-open');
    }

    function hideFeedback() {
        $('.feedback-holder').removeClass('tooltip-is-open');
    }

    function scaffoldPayment(scaffoldName){
        var isScaffoldPaid = true;
        if (!scaffolds[scaffoldName].paid){
            $.ajax({
                method: "POST",
                url: scaffoldPaymentHandlerUrl,
                data: JSON.stringify({"scaffold_name": scaffoldName}),
                async: false,
            }).done(function(response) {
                isScaffoldPaid = response.scaffold_paid;
                scaffolds[scaffoldName].paid = response.scaffold_paid;
                if (response.scaffold_paid){
                    $('.user-coins').html(response.coins);
                    $('.scaffold__price.'+scaffoldName).html('&#10004');
                }
            }).error(function(error){
                console.log(error);
            });
        }
        return isScaffoldPaid;
    }

    $.post(renderHtmlHandlerUrl, '{}').done(function(response) {
        $('#main-question-content', element).html($.parseHTML(response.content));

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
                    var userAnswers = getUserAnswers($questionForm);

                    $.post(
                        submithHandlerUrl,
                        JSON.stringify({"answers": userAnswers, "confidence": confidence})
                    ).done(function (response) {
                        isSubmissionAllowed = response.is_submission_allowed;
                        var submissionCount = response.submission_count;
                        if (response.correct) {
                            $skipBtn.addClass("hidden");
                            $scaffolds.addClass("hidden");
                            changeFeedbackMessage("Correct!");
                        }
                        else if (isSubmissionAllowed) {
                            $scaffolds.removeClass("hidden");
                        }
                        if (submissionCount > 1 && !response.correct) {
                            $skipBtn.addClass("hidden");
                            changeFeedbackMessage(`The correct answer is "${response.correct_answers}". Let’s move on.`);
                        }
                        showFeedback();
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
                var isScaffoldPaid = scaffoldPayment(scaffoldData.scaffoldName);
                if (isScaffoldPaid){
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
                if (!skipped) {
                    $.post(
                        skipHandlerUrl, JSON.stringify({"skip": true})
                    ).done(function(response) {
                        skipped = true;
                        isSubmissionAllowed = response.is_submission_allowed;
                        changeFeedbackMessage(`The correct answer is ${response.correct_answers}. Let’s move on.`);
                        $confidenceInput.addClass("hidden");
                        $confidenceInfo.addClass("hidden");
                        $submit.attr('disabled', 'disabled');
                        showFeedback();
                        }
                    ).error(function(error){
                        console.log(error);
                    });
                }
            });

            $(document).ready(function() {
                $('.author-block__wrapper', element).get(0).style.setProperty('--color-repharse', init_args.scaffolds[init_args.rephrase_name].color);
                $('.author-block__wrapper', element).get(0).style.setProperty('--color-break', init_args.scaffolds[init_args.break_it_down_name].color);
                $('.author-block__wrapper', element).get(0).style.setProperty('--color-teach', init_args.scaffolds[init_args.teach_me_name].color);

                $('.show-simulation', element).click(function(e) {
                    var iframeUrl = $(e.currentTarget).data('iframeUrl');
                    $('.simulation-overlay', element).find('iframe').attr('src', iframeUrl);
                    $('.simulation-overlay', element).fadeIn(300);
                });

                $('.simulation-close-btn', element).click(function() {
                    $('.simulation-overlay', element).fadeOut(300);
                });
            });

            // Feedback tooltip
            $(".feedback-holder .feedback-open", element).on("click", showFeedback);

            $(".feedback-close", element).on("click", hideFeedback);

            $('.button-next-' + blockId, element).click(function() {
                $('.sequence-nav-button.button-next').get(0).click();
            });
            $('.button-previous-' + blockId, element).click(function() {
                $('.sequence-nav-button.button-previous').get(0).click();
            });
        });
    });
}
