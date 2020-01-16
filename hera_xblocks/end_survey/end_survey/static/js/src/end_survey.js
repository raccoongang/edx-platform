/* Javascript for EndSurveyXBlock. */
function EndSurveyXBlock(runtime, element) {
    let handlerUrl = runtime.handlerUrl(element, 'vote');
    const $questionForm = $(".survey-form", element);
    // TODO: Write function do not show button submit if user already answered
    //  $(document).ready(function() {check user already answered context have self.user_result or not});
    $('.slidebar-wrapper').slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        fade: true,
        adaptiveHeight: true,
        infinite: false
      });
    
    $(".button-next").click((e) => {
        $('.slidebar-wrapper').slick('slickNext')
    });
    
    $(".button-submit").click((e)=> {
        $('.button-submit').prop('disabled', true);
        const answer = $questionForm.serializeArray();
        let answersData = {};
        for (let i in answer) {
            let answerObj = answer[i];
            answersData[answerObj.name] = answerObj.value;
        };
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(answer), // TODO: send all data but could use answersData dict
            success: console.log('SUCCESS') // TODO: need to create logic for success response ?  
        })
    });
    
    $(".possible-answers").on('change', (e)=> {
        if ($(".possible-answers:valid").length === $(".possible-answers").length) {
            
            $('.button-next').attr('disabled', false);
            $('.button-submit').attr('disabled', false);
        } else {
            $('.button-next').attr('disabled', 'disabled');
            $('.button-submit').attr('disabled', 'disabled');
        }
    });
}
