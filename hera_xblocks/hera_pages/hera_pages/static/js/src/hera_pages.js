/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element, init_args) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var isFormValid;
    var $questionForm = $(".table-form", element);
    var $submit = $('.submit', element);
    var blockId = init_args.block_id;
    var slickImagesSelector = '.image-wrapper-' + blockId;
    var slickSliderBarSelector = '.slidebar-wrapper-' + blockId;
    var slickSelectors = slickSliderBarSelector + ', ' +  slickImagesSelector;

    $('#slider-popup').popup();

    let shouldShowMessage = true;

    $(".button-prev", element).click(function(e){
        var imgSlideId = $(slickImagesSelector, element).slick('slickCurrentSlide');
        var contentSlideId = $(slickSliderBarSelector, element).slick('slickCurrentSlide');
        var slideId = imgSlideId < contentSlideId ? contentSlideId : imgSlideId;
        $(slickSelectors, element).slick('slickGoTo', slideId-1)
    });

    $(".button-next", element).click(function(e){
        if(shouldShowMessage && !isFormValid()) {
            shouldShowMessage = false;
            $('#slider-popup', element).popup('show')
        } else {
            $(slickSelectors, element).slick('slickNext')
        }
    });

    var slidebarSlideCount = 0;
    var imageSlideCount = 0;
    $(slickImagesSelector, element).add(slickSliderBarSelector, element).on('beforeChange', function(event, slick) {
        if($( event.target ).is(slickSliderBarSelector)){
            slidebarSlideCount = slick.slideCount;
        } else if($( event.target ).is(slickImagesSelector)){
            imageSlideCount = slick.slideCount;
        }
    });

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


    isFormValid = function () {
        const $inputElements = $('.slick-active .column-input', element);
        let result = true;
        if ($inputElements.length) {
            $inputElements.each(function(i, el){
                if(!$(el).val()) {
                    result = false;
                }
            });
        }
        return result;
    };

    $(document).ready(function() {
        $('#slider-popup').popup();
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

    $questionForm.on('change blur keyup', function(e) {
        var serializedForm = $questionForm.serializeArray();
        var emptyFormChecker = [];

        $(serializedForm).each(function( index, element ) {
            if (element.value) {
                emptyFormChecker.push(true)
            } else {
                emptyFormChecker.push(false)
            }
        });

        const every = (element) => element === true;

        if (emptyFormChecker.every(every)) {
            $submit.removeAttr("disabled");
        } else {
            $submit.attr("disabled", 'disabled');
        }
    });


    $submit.bind('click', function (e) {
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
        )
    });

}
