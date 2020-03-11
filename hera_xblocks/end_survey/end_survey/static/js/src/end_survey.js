/* Javascript for EndSurveyXBlock. */
function EndSurveyXBlock(runtime, element, init_args) {
    var handlerUrl = runtime.handlerUrl(element, 'vote');
    var $questionsForm = $(".survey-form-questions", element);
    var $confidenceForm = $(".survey-form-confidence", element);
    var blockId = init_args.block_id;
    var sclickSliderSelector = '.slidebar-wrapper-' + blockId;
    $(sclickSliderSelector).slick({
        slidesToShow: 1,
        slidesToScroll: 1,
        fade: true,
        adaptiveHeight: true,
        infinite: false
      });

    $(".survey-button-next").click(function(e) {
        $(sclickSliderSelector).slick('slickNext');
    });

    $(".button-submit").click(function(e) {
        $('.button-submit').prop('disabled', true);
        const answers = $questionsForm.serializeArray();
        const confidence = $confidenceForm.serializeArray();
        let answersData = {};
        for (let i in answers) {
            let answerObj = answers[i];
            answersData[answerObj.name] = answerObj.value;
        };
        let confidenceData = {};
        confidenceData[confidence[0].name] = confidence[0].value;
        data = {
            answersData: answersData,
            confidenceData: confidenceData
        }
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(data),
            success: function(response) {
                $("#wrapper-page").html(response);
                $(".button-next").prop('disabled', false);
            }
        })
    });

    $(".possible-answers").change(function(e) {
        if ($(".possible-answers:checked").length === $(".question-title").length) {
            $('.survey-button-next').attr('disabled', false);
        } else {
            $('.survey-button-next').attr('disabled', 'disabled');
        }
    });
    $(".confidence-answers").change(function(e) {
        if ($(".confidence-answers:checked").length === $(".confidence-title").length) {
            $('.button-submit').attr('disabled', false);
        } else {
            $('.button-submit').attr('disabled', 'disabled');
        }
    });
}
