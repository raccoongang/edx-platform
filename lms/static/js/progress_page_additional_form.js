$("#profile-form-save-action").on("click", function (e) {
    e.preventDefault();
    let form = $("#progress-form"),
        formElements = form[0].elements,
        formUrl = form.data('url'),
        ajaxData = {};

    for (let prop in formElements) {
        if (typeof formElements[prop].id === "string" && formElements[prop].id.length) {
            let fieldName = formElements[prop].id.replace('field-input-', '').replace('u-field-select-', '');
            ajaxData[fieldName] = formElements[prop].value
        }
    }

    $.ajax({
        url: formUrl,
        method: "PATCH",
        dataType: "json",
        data: JSON.stringify(ajaxData),
        contentType: 'application/merge-patch+json',
        success: function (data, textStatus) {
            form.find('.u-field').removeClass('progress-form-error');
            if (!data.empty_fields.length) {
                $(".progress-form-modal").modal('hide');
                $("#modal-button").hide();
                $("#btn_generate_cert").removeAttr('hidden');
            } else {
                form.find(".form-incomplete-error").text("All fields are required");
                $('.progress-form-modal').first().animate({scrollTop: 0}, 'slow');
                data.empty_fields.forEach(function(field) {
                  form.find("div[class*='u-field-" + field + "']").addClass("progress-form-error")
                });
            }
        },
        error: function (xhr) {
            let errors = JSON.parse(xhr.responseText);
            for (let i in errors.field_errors) {
                let span = `<span class="fa fa-exclamation-triangle message-validation-error"></span>`;
                $("#u-field-message-" + i).find(".u-field-message-notification").html(
                    span + errors.field_errors[i].user_message
                );
                $("#u-field-message-help-" + i).text('')
            }
        }
    });
});
