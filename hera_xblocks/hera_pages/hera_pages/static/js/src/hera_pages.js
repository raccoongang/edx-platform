/* Javascript for HeraPagesXBlock. */
function HeraPagesXBlock(runtime, element) {
    var isFormValid;
    $('#slider-popup').popup();
    $('.slidebar-wrapper').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        arrows: true,
        fade: true,
        adaptiveHeight: true
        // asNavFor: '.slider-nav'
      });

    let shouldShowMessage = true;
      
    $(".button-prev").click((e) => {
        $(".slick-prev").trigger("click")
    });

    $(".button-next").click((e) => {
        if(shouldShowMessage && !isFormValid()) {
            shouldShowMessage = false;
            $('#slider-popup').popup('show')
        } else {
            $(".slick-next").trigger("click")
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
