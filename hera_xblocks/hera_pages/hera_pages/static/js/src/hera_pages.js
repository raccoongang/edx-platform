/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var blockId = init_args.block_id;
    var slickImagesSelector = '.image-wrapper-' + blockId;
    var slickSliderBarSelector = '.slidebar-wrapper-' + blockId;
    var slickSelectors = slickSliderBarSelector + ', ' +  slickImagesSelector;
    var showMessage = true;
    var contentSlideCount = $('.js-content-counter').length;
    var imageSlideCount = $('.js-image-counter').length;
    var theBiggestCount = Math.max(imageSlideCount, contentSlideCount);

    var $submitButton = $('.submit', element);
    var $buttonPrevSlide = $(".button-prev", element);
    var $buttonNextSlide = $(".button-next", element);
    var $warningMessage = $('.js-show-hide-warning-message');
    var $imageSlider = $(slickImagesSelector, element);
    var $contentSlider = $(slickSliderBarSelector, element);
    var $slidesTogether =  $(slickSelectors, element);

    function getCurrentSlideId() {
        // if there is no $imageSlider - slick('slickCurrentSlide') returns jquery element but we need a number
        var currentImgSlideId = imageSlideCount ? $imageSlider.slick('slickCurrentSlide') : imageSlideCount;
        var currentContentSlideId = contentSlideCount ? $contentSlider.slick('slickCurrentSlide') : contentSlideCount;
        return Math.max(currentImgSlideId, currentContentSlideId);
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

    $(document).ready(function() {
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
    });

    $submitButton.bind('click', function (e) {
        var $questionForm = $(".table-form", element);
        $questionForm.find('input').validate();
        if (!$questionForm.find('input').valid() && showMessage) {
            $warningMessage.show();
            showMessage = false;
        } else {
            $warningMessage.hide();
            var serializedForm = $questionForm.serializeArray();
            var userAnswers = [];
            for (var i = 0; i < contentSlideCount; i++) {
                userAnswers.push([]);
            }
            for (var i in serializedForm) {
                userAnswers[serializedForm[i].name].push(serializedForm[i].value);
            }
            $.post(
                submithHandlerUrl,
                JSON.stringify({"answers": userAnswers})
            ).error(function(error){
                console.log(error);
            });
        }
    });
    $('.button-next-' + blockId, element).click(function() {
        $('.sequence-nav-button.button-next').get(0).click();
    });
    $('.button-previous-' + blockId, element).click(function() {
        $('.sequence-nav-button.button-previous').get(0).click();
    });
}
