/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element) {
    var submithHandlerUrl = runtime.handlerUrl(element, 'submit');
    var isFormValid;
    var $questionForm = $(".table-form", element);
    var $submit = $('.submit', element);

    $('#slider-popup').popup();
    $('.slidebar-wrapper, .image-wrapper').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        fade: true,
        adaptiveHeight: true,
        infinite: false,
        draggable: false,
        // asNavFor: '.slider-nav'
      });

    let shouldShowMessage = true;

    $(".button-prev", element).click(function(e){
        var imgSlideId = $('.image-wrapper', element).slick('slickCurrentSlide');
        var contentSlideId = $('.slidebar-wrapper', element).slick('slickCurrentSlide');
        var slideId = imgSlideId < contentSlideId ? contentSlideId : imgSlideId;
        $('.image-wrapper, .slidebar-wrapper', element).slick('slickGoTo', slideId-1)
    });

    $(".button-next", element).click(function(e){
        if(shouldShowMessage && !isFormValid()) {
            shouldShowMessage = false;
            $('#slider-popup', element).popup('show')
        } else {
            $('.image-wrapper, .slidebar-wrapper', element).slick('slickNext')
        }
    });

    var slidebarSlideCount = 0;
    var imageSlideCount = 0;
    $('.slidebar-wrapper, .image-wrapper', element).on('beforeChange', function(event, slick) {
        if($( event.target ).is('.slidebar-wrapper')){
            slidebarSlideCount = slick.slideCount;
        } else if($( event.target ).is('.image-wrapper')){
            imageSlideCount = slick.slideCount;
        }
    });

    $('.slidebar-wrapper, .image-wrapper', element).on('afterChange', function(event, slick) {
        $(".button-prev, .button-next", element).removeClass('hidden');
        var imgSlideId = $('.image-wrapper', element).slick('slickCurrentSlide');
        var contentSlideId = $('.slidebar-wrapper', element).slick('slickCurrentSlide');
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
        $('.slidebar-wrapper, .image-wrapper').slick({
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
