$("#profile-form-save-action").on("click", function (e) {
    e.preventDefault();
    let form = $("#progress-form"),
        formElements = form[0].elements,
        formUrl = form.data("url"),
        ajaxData = {};

    for (let prop in formElements) {
        if (typeof formElements[prop].id === "string" && formElements[prop].id.length) {
            let fieldName = formElements[prop].id.replace("field-input-", "").replace("u-field-select-", "");
            ajaxData[fieldName] = formElements[prop].value
        }
    }

    function checkEmptyFields() {
        var errorCount = 0;

        form.find("div[class*='u-field-']").removeClass("progress-form-error");
        form.find(".u-field-message-help").show();
        form.find(".u-field-message-notification").hide();

        var nonRequiredFields = ['sub-position', 'spec', 'diploma-number', 'additional_email', 'other-position'];

        for (key in ajaxData) {
            if(ajaxData[key] === "" && !nonRequiredFields.includes(key)) {
                errorCount++;
                $(".u-field-" + key).addClass("progress-form-error");
            }
        }

        if(errorCount) {
            form.find(".form-incomplete-error").text("All fields are required");
            $(".progress-form-modal .modal-body").first().animate({scrollTop: 0}, "slow");
            return errorCount;
        }
    }

    if(!checkEmptyFields() || checkEmptyFields() === undefined) {
        $.ajax({
            url: formUrl,
            method: "PATCH",
            dataType: "json",
            data: JSON.stringify(ajaxData),
            contentType: "application/merge-patch+json",
            success: function () {
                $(".progress-form-modal").first().removeClass("show").fadeOut();
                $("body").removeClass("not-scrollable");
                $("#modal-button").hide();
                $("#certificate-actions").removeClass("hidden");
            },
            error: function (xhr) {
                let errors = JSON.parse(xhr.responseText);
                for (let i in errors.field_errors) {
                    let span = `<span class="fa fa-exclamation-triangle message-validation-error"></span>`;
                    $("#u-field-message-" + i).find(".u-field-message-notification").html(
                        span + errors.field_errors[i].user_message
                    ).show();
                    form.find("div[class*='u-field-" + i + "']").addClass("progress-form-error");
                    form.find(".form-incomplete-error").text("All fields are required");
                    $("#u-field-message-help-" + i).hide();
                    $(".progress-form-modal .modal-body").first().animate({scrollTop: 0}, "slow");
                }
            }
        });
    } 
});
