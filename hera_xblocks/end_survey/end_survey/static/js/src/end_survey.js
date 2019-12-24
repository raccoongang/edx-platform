/* Javascript for EndSurveyXBlock. */
function EndSurveyXBlock(runtime, element) {
    let handlerUrl = runtime.handlerUrl(element, 'vote');
    
    $(".button-submit").click((e)=> {
        $('.button-submit').prop('disabled', true);
        const userForm = $('#end_survey_form').serializeArray();
        $.ajax({
            type: "POST",
            url: handlerUrl,
            data: JSON.stringify(userForm),
            success: console.log('SUCCESS')
        })
    })
}
