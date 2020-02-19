/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var $submitButton = $('.submit', element);
    var blockId = init_args.block_id;
    var slickImagesSelector = '.image-wrapper-' + blockId;
    var slickSliderBarSelector = '.slidebar-wrapper-' + blockId;
    var slickSelectors = slickSliderBarSelector + ', ' +  slickImagesSelector;
    var showMessage = true;
    var slidebarSlideCount = 0;
    var imageSlideCount = 0;

    // click on the next arrow
    $(".button-prev", element).click(function(e){
        var currentImgSlideId = $(slickImagesSelector, element).slick('slickCurrentSlide');
        var currentContentSlideId = $(slickSliderBarSelector, element).slick('slickCurrentSlide');
        var slideId = currentImgSlideId < currentContentSlideId ? currentContentSlideId : currentImgSlideId;
        $(slickSelectors, element).slick('slickGoTo', slideId-1);
    });

    // click on the prev arrow
    $(".button-next", element).click(function(e){
        $(slickSelectors, element).slick('slickNext');
    });

    // get number of sliders
    $(slickImagesSelector, element).add(slickSliderBarSelector, element).on('beforeChange', function(event, slick) {
        if($( event.target ).is(slickSliderBarSelector)){
            slidebarSlideCount = slick.slideCount;
        } else if($( event.target ).is(slickImagesSelector)){
            imageSlideCount = slick.slideCount;
        }
    });

    // functionality to show/hide appropriate arrows
    $(slickImagesSelector, element).add(slickSliderBarSelector, element).on('afterChange', function(event, slick) {
        $(".button-prev, .button-next", element).removeClass('hidden');
        var imgSlideId = $(slickImagesSelector, element).slick('slickCurrentSlide');
        var contentSlideId = $(slickSliderBarSelector, element).slick('slickCurrentSlide');
        var slideId = imgSlideId < contentSlideId ? contentSlideId : imgSlideId;
        var slideCount = slidebarSlideCount < imageSlideCount ? imageSlideCount : slidebarSlideCount;
        if (slideId == 0) {
            $(".button-prev", element).addClass('hidden');
        } else if(slideId + 1 == slideCount){
            $(".button-next", element).addClass('hidden');
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
            // asNavFor: '.slider-nav'
        });
    });

    $submitButton.bind('click', function (e) {
        var $questionForm = $(".table-form", element);

        if (!$questionForm.is(':valid') && showMessage) {
            $(document).find('.js-show-hide-warning-message').show();
            showMessage = false;
        } else {
            $(document).find('.js-show-hide-warning-message').hide();
            var serializedForm = $questionForm.serializeArray();
            var userAnswers = [];

            for (var i = 0; i < $questionForm.length; i++) {
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
}
