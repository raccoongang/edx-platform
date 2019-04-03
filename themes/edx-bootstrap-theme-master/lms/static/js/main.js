jQuery(function($) {
    'use strict',
    //#main-slider
    $(function() {
        $('#main-slider.carousel').carousel({
            interval: 8000
        });
        if ($('.js-partner-carousel').length) {
            partnerSlider();
        }
        if ($('.js-topic-carousel').length) {
            topicSlider();
        }
        if ($('.js-courses-slider').length) {
            if ($(window).width() < 768) {
                coursesSlider();

            }
        }
        $(".mat-input").focus(function(){
  $(this).parent().addClass("is-active is-completed");
});

$(".mat-input").focusout(function(){
  if($(this).val() === "")
    $(this).parent().removeClass("is-completed");
  $(this).parent().removeClass("is-active");
})

    });
    // accordian
    $('.accordion-toggle').on('click', function() {
        $(this).closest('.panel-group').children().each(function() {
            $(this).find('>.panel-heading').removeClass('active');
        });

        $(this).closest('.panel-heading').toggleClass('active');
    });

    //Initiat WOW JS
    new WOW().init();

    // portfolio filter
    $(window).load(function() {
        'use strict';
        var $portfolio_selectors = $('.portfolio-filter >li>a');
        var $portfolio = $('.portfolio-items');
        try {

            $portfolio.isotope({
                itemSelector: '.portfolio-item',
                layoutMode: 'fitRows'
            });

            $portfolio_selectors.on('click', function() {
                $portfolio_selectors.removeClass('active');
                $(this).addClass('active');
                var selector = $(this).attr('data-filter');
                $portfolio.isotope({ filter: selector });
                return false;
            });
        } catch (e) {

        }
    });

    // Contact form
    var form = $('#main-contact-form');
    form.submit(function(event) {
        event.preventDefault();
        var form_status = $('<div class="form_status"></div>');
        $.ajax({
            url: $(this).attr('action'),

            beforeSend: function() {
                form.prepend(form_status.html('<p><i class="fa fa-spinner fa-spin"></i> Email is sending...</p>').fadeIn());
            }
        }).done(function(data) {
            form_status.html('<p class="text-success">' + data.message + '</p>').delay(3000).fadeOut();
        });
    });


    //goto top
    $('.gototop').click(function(event) {
        event.preventDefault();
        $('html, body').animate({
            scrollTop: $("body").offset().top
        }, 500);
    });

    //Pretty Photo
    $("a[rel^='prettyPhoto']").prettyPhoto({
        social_tools: false
    });



});
// responsive menu
$('.navbar-toggle').on('click',function(){
$('.mob-menu').addClass('active');
});
$('.close-mob-menu').on('click',function(e){
    e.preventDefault();
    $('.mob-menu').removeClass('active');
    });


//partner slider
function partnerSlider() {
    $('.js-partner-carousel').owlCarousel({
        loop: true,
        margin: 25,
        responsiveClass: true,
        responsive: {
            0: {
                items: 2,
                nav: true,
                stagePadding: 50
            },
            600: {
                items: 2,
                nav: false
            },
            1000: {
                items: 5,
                nav: true,
                loop: false
            }
        }
    })

}



//partner slider
function topicSlider() {
    $('.js-topic-carousel').owlCarousel({
       loop:true,
    margin:10,
    nav:true,
    stagePadding: 50,
    responsive:{
        0:{
            items:1
        },
        600:{
            items:3
        },
        1000:{
            items:5
        }
    }
    })

}
$('.js-about-tabs li').on('click',function(e){
    e.preventDefault();
    var index = $(this).index();
    $(this).addClass('active').siblings().removeClass('active');
    $('.content-wrapper .content-item').removeClass('active');
    $('.content-wrapper .content-item').eq(index).addClass('active');
    });
//course slider
//partner slider
function coursesSlider() {
    $('.js-courses-slider').owlCarousel({
        loop: true,
        margin: 15,
        responsiveClass: true,
        items: 1,
        nav: false,
        stagePadding: 25

    })

}