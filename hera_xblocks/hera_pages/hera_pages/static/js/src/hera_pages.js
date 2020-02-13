/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element) {
    var isFormValid;
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

    $(".button-prev").click((e) => {
        var imgSlideId = $('.image-wrapper').slick('slickCurrentSlide');
        var contentSlideId = $('.slidebar-wrapper').slick('slickCurrentSlide');
        var slideId = imgSlideId < contentSlideId ? contentSlideId : imgSlideId;
        $('.image-wrapper, .slidebar-wrapper').slick('slickGoTo', slideId-1)
    });

    $(".button-next").click((e) => {
        if(shouldShowMessage && !isFormValid()) {
            shouldShowMessage = false;
            $('#slider-popup').popup('show')
        } else {
            $('.image-wrapper, .slidebar-wrapper').slick('slickNext')
        }
    })  
    
    isFormValid = function () {
        const $inputElements = $('.slick-active .column-input');
        let result = true;
        if ($inputElements.length) {
            $inputElements.each((i, el) => {
                if(!$(el).val()) {
                    result = false;
                }
            });
        }
        return result;
    }
}
