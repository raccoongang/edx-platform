/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element) {

    var isFormValid;
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
}
