(function(define) {
    'use strict';
    define([
        'jquery',
        'underscore',
        'gettext',
        'js/student_account/views/FormView',
        'text!templates/student_account/form_status.underscore'
    ],
        function($, _, gettext, FormView, formStatusTpl) {
            return FormView.extend({
                el: '#register-form',

                tpl: '#register-tpl',

                events: {
                    'click .js-register': 'submitForm',
                    'click .login-provider': 'thirdPartyAuth',
                    'change #register-country': 'showRegions'
                },

                formType: 'register',

                formStatusTpl: formStatusTpl,

                authWarningJsHook: 'js-auth-warning',

                defaultFormErrorsTitle: gettext('We couldn\'t create your account.'),

                submitButton: '.js-register',

                preRender: function(data) {
                    this.providers = data.thirdPartyAuth.providers || [];
                    this.hasSecondaryProviders = (
                        data.thirdPartyAuth.secondaryProviders && data.thirdPartyAuth.secondaryProviders.length
                    );
                    this.currentProvider = data.thirdPartyAuth.currentProvider || '';
                    this.errorMessage = data.thirdPartyAuth.errorMessage || '';
                    this.platformName = data.platformName;
                    this.autoSubmit = data.thirdPartyAuth.autoSubmitRegForm;

                    this.listenTo(this.model, 'sync', this.saveSuccess);
                },

                render: function(html) {
                    var fields = html || '',
                        formErrorsTitle = gettext('An error occurred.');

                    $(this.el).html(_.template(this.tpl)({
                    /* We pass the context object to the template so that
                     * we can perform variable interpolation using sprintf
                     */
                        context: {
                            fields: fields,
                            currentProvider: this.currentProvider,
                            providers: this.providers,
                            hasSecondaryProviders: this.hasSecondaryProviders,
                            platformName: this.platformName
                        }
                    }));

                    this.postRender();

                    // Must be called after postRender, since postRender sets up $formFeedback.
                    if (this.errorMessage) {
                        this.renderErrors(formErrorsTitle, [this.errorMessage]);
                    } else if (this.currentProvider) {
                        this.renderAuthWarning();
                    }

                    if (this.autoSubmit) {
                        $(this.el).hide();
                        $('#register-honor_code').prop('checked', true);
                        this.submitForm();
                    }

                    return this;
                },

                addDropDownMenu: function(elementsForShow){
                    let countryClass = $("#register-country").attr("class");
                    let stateLabel = $("<label>", {for: "usa-regions", id: "region-label"}).text("Regions * ")
                    let select = $("<select>", {id: "usa-regions", "class": countryClass})
                    for (let state in elementsForShow){
                        select.append($("<option>", {
                            value: elementsForShow[state],
                            text: elementsForShow[state]
                        }))
                    }

                    $("#register-country").after(select)
                    $("#register-country").after(stateLabel)

                },

                hideDropdownMenu: function(objectSelector){
                    objectSelector.html("");
                    objectSelector.hide();
                    $("#region-label").hide()
                },

                showRegions: function(event) {
                    let usaStates =  [
                        "Alabama",
                        "Alaska",
                        "Arizona",
                        "Arkansas",
                        "California",
                        "Colorado",
                        "Connecticut",
                        "Delaware",
                        "Florida",
                        "Georgia",
                        "Hawaii",
                        "Idaho",
                        "Illinois Indiana",
                        "Iowa",
                        "Kansas",
                        "Kentucky",
                        "Louisiana",
                        "Maine",
                        "Maryland",
                        "Massachusetts",
                        "Michigan",
                        "Minnesota",
                        "Mississippi",
                        "Missouri",
                        "Montana Nebraska",
                        "Nevada",
                        "New Hampshire",
                        "New Jersey",
                        "New Mexico",
                        "New York",
                        "North Carolina",
                        "North Dakota",
                        "Ohio",
                        "Oklahoma",
                        "Oregon",
                        "Pennsylvania Rhode Island",
                        "South Carolina",
                        "South Dakota",
                        "Tennessee",
                        "Texas",
                        "Utah",
                        "Vermont",
                        "Virginia",
                        "Washington",
                        "West Virginia",
                        "Wisconsin",
                        "Wyoming",
                        ]

                    if (event.target.value === "US") {
                        this.addDropDownMenu(usaStates);
                    }
                    else {
                        this.hideDropdownMenu($("#usa-regions"));
                    }

                },

                thirdPartyAuth: function(event) {
                    var providerUrl = $(event.currentTarget).data('provider-url') || '';

                    if (providerUrl) {
                        window.location.href = providerUrl;
                    }
                },

                saveSuccess: function() {
                    this.trigger('auth-complete');
                },

                saveError: function(error) {
                    $(this.el).show(); // Show in case the form was hidden for auto-submission
                    this.errors = _.flatten(
                        _.map(
                            // Something is passing this 'undefined'. Protect against this.
                            JSON.parse(error.responseText || '[]'),
                            function(errorList) {
                                return _.map(
                                    errorList,
                                    function(errorItem) { return '<li>' + errorItem.user_message + '</li>'; }
                                );
                            }
                        )
                    );
                    this.renderErrors(this.defaultFormErrorsTitle, this.errors);
                    this.toggleDisableButton(false);
                },

                postFormSubmission: function() {
                    if (_.compact(this.errors).length) {
                    // The form did not get submitted due to validation errors.
                        $(this.el).show(); // Show in case the form was hidden for auto-submission
                    }
                },

                renderAuthWarning: function() {
                    var msgPart1 = gettext('You\'ve successfully signed into %(currentProvider)s.'),
                        msgPart2 = gettext(
                            'We just need a little more information before you start learning with %(platformName)s.'
                        ),
                        fullMsg = _.sprintf(
                            msgPart1 + ' ' + msgPart2,
                            {currentProvider: this.currentProvider, platformName: this.platformName}
                        );

                    this.renderFormFeedback(this.formStatusTpl, {
                        jsHook: this.authWarningJsHook,
                        message: fullMsg
                    });
                }
            });
        });
}).call(this, define || RequireJS.define);
