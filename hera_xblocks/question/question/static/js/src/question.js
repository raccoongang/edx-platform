function QuestionXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var skipHandlerUrl = runtime.handlerUrl(element, 'skip');
    var renderHtmlHandlerUrl = runtime.handlerUrl(element, 'render_html');
    var scaffoldPaymentHandlerUrl = runtime.handlerUrl(element, 'scaffold_payment');
    var getFilledTablesHandlerUrl = runtime.handlerUrl(element, 'get_filled_tables');

    var scaffolds = init_args.scaffolds;
    var blockId = init_args.block_id;
    var skipped = false;
    var tablesRendered = false;

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

    function enableNextButton() {
        $('.button-next-' + blockId, element).attr('disabled', false);
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
                    $('.scaffold__price.'+scaffoldName).html('<i class="fa fa-check" aria-hidden="true"></i>');
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
            var $confidenceInput = $(".confidence-select", element);
            var $confidenceHolder = $('.confidence-holder', element);
            var $confidenceError = $('.confidence-text.error', element);
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
            var isSubmissionAllowed = response.is_submission_allowed;
            var $buttonFillTables = $('#fill-tables-' + blockId, element);
            var isThereTableInputs = $('table', element).find('input').length > 0;

            // conditions have been separated to make it easier to read the code (but not sure it helped)
            if (!isSubmissionAllowed && ((response.has_many_types && isThereTableInputs) || response.has_many_types || (!response.has_many_types && !isThereTableInputs) )) {
                if (response.user_answer && !response.is_scaffolds_enabled) {
                    changeFeedbackMessage("You have submitted your answer.");
                } else if (!response.user_answer_correct) {
                    changeFeedbackMessage(`The correct answer is "${response.correct_answers}". Let’s move on.`);
                }
            } else if (response.user_answer && !response.is_scaffolds_enabled) { // !response.has_many_types && isThereTableInputs
                changeFeedbackMessage("You have submitted your answer.");
            }
            if (response.is_scaffolds_enabled && !isSubmissionAllowed && isThereTableInputs && !response.user_answer_correct) {
                $buttonFillTables.show();
            }

            if (response.submission_counter == 1 && isSubmissionAllowed && response.is_any_scaffold_paid) {
                $skipBtn.removeClass('hidden');
            }

            function hideConfidence() {
                $confidenceInput.val(null).trigger('change');
                $confidenceHolder.addClass('hidden');
            }

            function showConfidence() {
                $confidenceHolder.removeClass("hidden");
                $confidenceError.hide();
            }

            function hideScaffoldImg() {
                $questioonsImageWrapper.removeClass('is-teach is-break is-rephrase');
                $scaffoldHelpImage.addClass("hidden");
                $questionSlider.removeClass("hidden");
                $closeBtn.addClass("hidden");
            }

            $('input, select', element).on("change blur keyup", function() {
                if (isSubmissionAllowed) {
                    showConfidence();
                    $submit.removeAttr("disabled");
                }
            });

            $buttonFillTables.click(function() {
                if (!tablesRendered) {
                    $.post(getFilledTablesHandlerUrl, JSON.stringify({})).done(function(response) {
                        var tables = response.tables_html;
                        $('.table-wrapper').each(function(index) {
                            if (tables[index]) {
                                $(this).html(tables[index]);
                            }
                        });
                        tablesRendered = true;
                    }).error(function(error) {
                        console.log(error);
                    });
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
                        var submissionCount = response.submission_counter;
                        var isScaffoldsEnabled = response.is_scaffolds_enabled;
                        if (response.correct) {
                            enableNextButton();
                            $skipBtn.addClass("hidden");
                            $scaffolds.addClass("hidden");
                            changeFeedbackMessage("Correct.");
                        }
                        else if (isSubmissionAllowed) {
                            $scaffolds.removeClass("hidden");
                        }
                        if (!isSubmissionAllowed) {
                            $('input', element).attr('disabled', true);
                            enableNextButton();
                        }
                        if (submissionCount > 1 && !response.correct && isScaffoldsEnabled) {
                            $skipBtn.addClass("hidden");
                            // also separated conditions to eas reading a code
                            if (
                                (response.has_many_types && isThereTableInputs) ||
                                response.has_many_types ||
                                (!response.has_many_types && !isThereTableInputs)
                            ) {
                                changeFeedbackMessage(`The correct answer is "${response.correct_answers}". Let’s move on.`);
                            }
                            if (isThereTableInputs) {
                                if (!response.has_many_types) {
                                    changeFeedbackMessage('');
                                }
                                $buttonFillTables.show();
                            }
                        } else if (!isScaffoldsEnabled) {
                            changeFeedbackMessage('You have submitted your answer.');
                        }
                        showFeedback();
                        hideConfidence();
                        $(e.currentTarget).attr('disabled', 'disabled');
                    });
                } else {
                    $confidenceError.show();
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
                hideScaffoldImg();
            });

            $closeBtn.bind('click', hideScaffoldImg);

            $skipBtn.bind('click', function (event) {
                if (!skipped) {
                    $.post(
                        skipHandlerUrl, JSON.stringify({"skip": true})
                    ).done(function(response) {
                        skipped = true;
                        isSubmissionAllowed = response.is_submission_allowed;
                        if ((response.has_many_types && isThereTableInputs) || response.has_many_types || (!response.has_many_types && !isThereTableInputs) ) {
                            changeFeedbackMessage(`The correct answer is "${response.correct_answers}". Let’s move on.`);
                        } else {
                            changeFeedbackMessage('');
                        }
                        if (isThereTableInputs && !isSubmissionAllowed) {
                            $buttonFillTables.show();
                        }
                        hideConfidence();
                        $submit.attr('disabled', 'disabled');
                        enableNextButton();
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

            // In your Javascript (external .js resource or <script> tag)
            $(document).ready(function() {
                $confidenceInput.select2({
                    placeholder: "Select",
                    minimumResultsForSearch: -1,
                });
            });
        });
    });
}
