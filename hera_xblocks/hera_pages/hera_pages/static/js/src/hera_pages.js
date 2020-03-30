/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var renderHTMLHandlerUrl = runtime.handlerUrl(element, 'render_html');
    var readyTableHMTLHandlerUrl = runtime.handlerUrl(element, 'render_correct_filled_tables');
    var allSlidesViewedHandlerUrl = runtime.handlerUrl(element, 'all_slides_viewed');
    var blockId = init_args.block_id;

    $.post(renderHTMLHandlerUrl, "{}").done(function(response) {
        $('#hera-pages-' + blockId, element).html($.parseHTML(response.content));

        $(function ($) {
            var slickImagesSelector = '.image-wrapper-' + blockId;
            var slickSliderBarSelector = '.slidebar-wrapper-' + blockId;
            var slickSelectors = slickSliderBarSelector + ', ' +  slickImagesSelector;
            var feedbackMessageCounter = 0;
            var contentSlideCount = $('.js-content-counter').length;
            var imageSlideCount = $('.js-image-counter').length;
            var theBiggestCount = Math.max(imageSlideCount, contentSlideCount);
            var $submitButton = $('.button-next-' + blockId, element);
            var $buttonPrevSlide = $(".button-prev", element);
            var $buttonNextSlide = $(".button-next", element);
            var $imageSlider = $(slickImagesSelector, element);
            var $contentSlider = $(slickSliderBarSelector, element);
            var $slidesTogether =  $(slickSelectors, element);
            var answerCounter = 0;
            var tableRendered = false;
            function getCurrentSlideId() {
                // if there is no $imageSlider - slick('slickCurrentSlide') returns jquery element but we need a number
                var currentImgSlideId = imageSlideCount ? $imageSlider.slick('slickCurrentSlide') : imageSlideCount;
                var currentContentSlideId = contentSlideCount ? $contentSlider.slick('slickCurrentSlide') : contentSlideCount;
                return Math.max(currentImgSlideId, currentContentSlideId);
            }

            function showFeedback() {
                $('.feedback-open', element).attr('disabled', false);
                $('.feedback-holder').addClass('tooltip-is-open');
            }

            function hideFeedback() {
                $('.feedback-holder').removeClass('tooltip-is-open');
            }

            function isFormValid($form) {
                var validValues = [];
                var trueCounter = 0;
                var inputFormCounter = 0;

                $form.each(function() {
                    var form = $(this);
                    if (form.find('input').length) {
                        inputFormCounter++;
                        form.validate();
                        validValues.push(form.valid());
                    }

                });
                validValues.forEach(function(el, ind) {
                    if (el) {
                        trueCounter++;
                    }
                });
                if (trueCounter === inputFormCounter) {
                    return true;
                }
                return false;
            }

            function getUserAnswers($form) {
                var serializedForm = $form.serializeArray();
                var userAnswers = [];
                // var answerCounter = 0;
                for (var i = 0; i < contentSlideCount; i++) {
                    userAnswers.push([]);
                }
                for (var i in serializedForm) {
                    var value = serializedForm[i].value;
                    if (value.length) {
                        answerCounter++;
                    }
                    var index = serializedForm[i].name.split('-')[0];
                    userAnswers[index].push(value);
                }
                return userAnswers;
            }

            function renderTablesWithCorrectAnswers() {
                $.post(
                    readyTableHMTLHandlerUrl,
                    JSON.stringify({})
                ).done(function(response) {
                    var tablesData = response.tables_html;
                    var $questionForm = $(".table-form", element);
                    findSlideWithTable();
                    $questionForm.each(function(index) {
                        if (tablesData[index]){
                            $(this).html(tablesData[index]);
                            tableRendered = true;
                        }
                    });
                }).error(function(error) {
                    console.log(error);
                });
            }

            function postUserAnswers(userAnswers) {
                $.post(
                    submithHandlerUrl,
                    JSON.stringify({"answers": userAnswers})
                ).error(function(error){
                    console.log(error);
                });
            }

            function clickNext() {
                $('.sequence-nav-button.button-next').get(0).click();
            }

            function changeFeedbackMessage(message) {
                $('#feedback-content-' + blockId).text(message);
            }

            /**
             * Find a table with input fields and make it active in slider to show correct
             * filled table.
             */
            function findSlideWithTable() {
                $(".table-form", element).each(function() {
                    if ($(this).find('input').length > 0) {
                        // find the index of the slick-item element
                        var theActiveSlideIndex = $('.single-item', element).index($(this).parent('.single-item'));
                        // go to that active slider
                        $slidesTogether.slick('slickGoTo', theActiveSlideIndex);
                        return false;
                    }
                });
            }

            // click on the prev arrow
            $buttonPrevSlide.click(function(e){
                $slidesTogether.slick('slickGoTo', getCurrentSlideId() - 1);
            });

            // click on the next arrow
            $buttonNextSlide.click(function(e){
                $slidesTogether.slick('slickNext');
            });

            // functionality to show/hide appropriate arrows
            $slidesTogether.on('afterChange', function(event, slick) {
                $(".button-prev, .button-next", element).removeClass('hidden');
                var slideId = getCurrentSlideId();

                if (slideId === 0) {
                    $buttonPrevSlide.addClass('hidden');
                } else if(slideId + 1 === theBiggestCount){
                    $buttonNextSlide.addClass('hidden');
                    $.post(
                        allSlidesViewedHandlerUrl,
                        JSON.stringify({})
                    ).done(
                        function(response) {
                            $('.button-next-' + blockId, element).removeAttr("disabled");
                        }
                    ).error(function(error){
                        console.log(error);
                    });
                }
            });

            if ($('input', element).length) {
                $('.submit-button-holder').show();
            } else {
                $('.submit-button-holder').hide();
            }
            $(slickSelectors).slick({
                slidesToShow: 1,
                slidesToScroll: 1,
                fade: true,
                adaptiveHeight: true,
                infinite: false,
                draggable: false,
            });

            // Feedback tooltip
            $(".feedback-close", element).on("click", hideFeedback);
            $(".feedback-open", element).on("click", showFeedback);

            $submitButton.bind('click', function (e) {
                var $questionForm = $(".table-form", element);
                if ($questionForm.length && !tableRendered) {
                    var userAnswers = getUserAnswers($questionForm);
                    feedbackMessageCounter++;
                    if (feedbackMessageCounter === 1) { // it seems like you havent interacted

                        if (!isFormValid($questionForm)) {
                            changeFeedbackMessage(
                                "It seems like you haven't fully interacted with the simulation." +
                                " Give it another try. If you'd like to exit the simulation instead, press next."
                            );
                            showFeedback();
                        } else {
                            postUserAnswers(userAnswers);
                            renderTablesWithCorrectAnswers();
                            changeFeedbackMessage("Alright. Let's move on. Here is the completed table.");
                            showFeedback();
                        }
                        return;
                    } else if (feedbackMessageCounter === 2) {  // alright let's move on

                            postUserAnswers(userAnswers);
                            renderTablesWithCorrectAnswers();
                            changeFeedbackMessage("Alright. Let's move on. Here is the completed table.");
                            showFeedback();

                        return;
                    }
                }
                clickNext();
            });
            $('.button-previous-' + blockId, element).click(function() {
                $('.sequence-nav-button.button-previous').get(0).click();
            });
        });
    })
}
