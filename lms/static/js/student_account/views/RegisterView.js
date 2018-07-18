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
                    'keypress #register-mobile': 'onlyNumbers',
                    'keyup #register-mobile': 'trimFirstZero',
                    'keypress #register-nationality_id': 'onlyNumbers',
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
                    this.hideAuthWarnings = data.hideAuthWarnings;
                    this.googleRecaptchaSiteKey = data.googleRecaptchaSiteKey;
                    this.isSSO = data.isSSO;

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
                            platformName: this.platformName,
                            googleRecaptchaSiteKey: this.googleRecaptchaSiteKey
                        }
                    }));

                    if (this.isSSO) {
                        $($(this.el).find('#register-username')[0]).attr('type', 'hidden');
                        $($(this.el).find('label[for="register-username"]')[0]).hide();
                    }

                    this.postRender();

                    // Must be called after postRender, since postRender sets up $formFeedback.
                    if (this.errorMessage) {
                        this.renderErrors(formErrorsTitle, [this.errorMessage]);
                        if (typeof grecaptcha !== 'undefined') grecaptcha.reset();
                    } else if (this.currentProvider && !this.hideAuthWarnings) {
                        this.renderAuthWarning();
                        if (typeof grecaptcha !== 'undefined') grecaptcha.reset();
                    }

                    this.addWrapMobile();

                    if (this.autoSubmit) {
                        $(this.el).hide();
                        $('#register-honor_code').prop('checked', true);
                        this.submitForm();
                    }

                    return this;
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
                    if (typeof grecaptcha !== 'undefined') grecaptcha.reset();
                    this.toggleDisableButton(false);
                },

                postFormSubmission: function() {
                    if (_.compact(this.errors).length) {
                    // The form did not get submitted due to validation errors.
                        $(this.el).show(); // Show in case the form was hidden for auto-submission
                        if (typeof grecaptcha !== 'undefined') grecaptcha.reset();
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
                },

                getFormData: function() {
                    var obj = FormView.prototype.getFormData.apply(this, arguments),
                        $form = this.$form,
                        $label,
                        $emailElement,
                        $passwordElement,
                        $confirmEmailElement,
                        $confirmPasswordElement,
                        email = '',
                        password = '',
                        confirmEmail = '',
                        confirmPassword = '';

                    $emailElement = $form.find('input[name=email]');
                    $passwordElement = $form.find('input[name=password]');
                    $confirmEmailElement = $form.find('input[name=confirm_email]');
                    $confirmPasswordElement = $form.find('input[name=confirm_password]');

                    if ($confirmEmailElement.length) {
                        email = $emailElement.val();
                        confirmEmail = $confirmEmailElement.val();
                        $label = $form.find('label[for=' + $confirmEmailElement.attr('id') + ']');

                        if (confirmEmail !== '' && email !== confirmEmail) {
                            this.errors.push('<li>' + $confirmEmailElement.data('errormsg-required') + '</li>');
                            $confirmEmailElement.addClass('error');
                            $label.addClass('error');
                        } else if (confirmEmail !== '') {
                            obj.confirm_email = confirmEmail;
                            $confirmEmailElement.removeClass('error');
                            $label.removeClass('error');
                        }
                    }

                    if ($confirmPasswordElement.length) {
                        password = $passwordElement.val();
                        confirmPassword = $confirmPasswordElement.val();
                        $label = $form.find('label[for=' + $confirmPasswordElement.attr('id') + ']');

                        if (confirmPassword !== '' && password !== confirmPassword) {
                            this.errors.push('<li>' + $confirmPasswordElement.data('errormsg-required') + '</li>');
                            $confirmPasswordElement.addClass('error');
                            $label.addClass('error');
                        } else if (confirmPassword !== '') {
                            obj.confirm_password = confirmPassword;
                            $confirmPasswordElement.removeClass('error');
                            $label.removeClass('error');
                        }
                    }

                    return obj;
                },

                onlyNumbers: function(e) {
                    //Only accepts digits
                    if (e.which != 8 && e.which != 0 && (e.which < 48 || e.which > 57)) {
                        return false;
                    }
                },

                trimFirstZero: function(e) {
                    var str = $(e.currentTarget).val();
                    $(e.currentTarget).val(str.replace(/^[ 0]/g,''));
                },

                addWrapMobile: function() {
                    var $registerMobile = $(this.el).find('#register-mobile');
                    $registerMobile.wrap("<div class='wrap-register-mobile'></div>");
                    $registerMobile.before("<span>+966</span>");
                }
            });
        });
}).call(this, define || RequireJS.define);
