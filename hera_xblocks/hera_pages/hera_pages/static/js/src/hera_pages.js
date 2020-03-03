/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var renderHTMLHandlerUrl = runtime.handlerUrl(element, 'render_html');
    var readyTableHMTLHandlerUrl = runtime.handlerUrl(element, 'render_correct_filled_tables');
    var blockId = init_args.block_id;

    $.post(renderHTMLHandlerUrl, "{}").done(function(response) {
        $('#hera-pages-' + blockId, element).html($.parseHTML(response.content));

        $(function ($) {
            var slickImagesSelector = '.image-wrapper-' + blockId;
            var slickSliderBarSelector = '.slidebar-wrapper-' + blockId;
            var slickSelectors = slickSliderBarSelector + ', ' +  slickImagesSelector;
            var showMessage = true;
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
                var $inputs = $form.find('input');
                $inputs.validate();
                return $inputs.valid();
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
                    userAnswers[serializedForm[i].name].push(value);
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
                    $questionForm.each(function(index) {
                        if (tablesData[index]){
                            $(this).html(tablesData[index]);
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
                ).done(function(response) {
                    $('.sequence-nav-button.button-next').get(0).click();
                }).error(function(error){
                    console.log(error);
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
                var userAnswers = getUserAnswers($questionForm);
                if (answerCounter > 3 && showMessage) {
                    renderTablesWithCorrectAnswers();
                    $('#feedback-content-' + blockId).text("Alright. Let's move on. Here is the completed table.");
                    showFeedback();
                } else if (!isFormValid($questionForm) && showMessage) {
                    showFeedback();
                    showMessage = false;
                } else {
                    hideFeedback();
                    postUserAnswers(userAnswers);
                }
            });
            $('.button-previous-' + blockId, element).click(function() {
                $('.sequence-nav-button.button-previous').get(0).click();
            });
        });
    })
}
