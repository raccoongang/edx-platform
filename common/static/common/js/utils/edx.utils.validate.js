(function(define) {
    'use strict';
    define([
        'jquery',
        'underscore',
        'underscore.string',
        'gettext'
    ],
        function($, _, _s, gettext) {
            var utils;
            // NOTE: figure out a way to pass with $el attributes. For now,
            //  duplicated in `openedx/core/djangoapps/user_api/accounts/__init__.py`.
            var USERNAME_MIN_LENGTH = 2;
            var USERNAME_MAX_LENGTH = 30;

        /* Mix non-conflicting functions from underscore.string
         * (all but include, contains, and reverse) into the
         * Underscore namespace. In practice, this mixin is done
         * by the access view, but doing it here helps keep the
         * utility self-contained.
         */
            _.mixin(_s.exports());

            utils = (function() {
                var _fn = {
                    validate: {

                        template: _.template('<li><%- content %></li>'),

                        msg: {
                            // NOTE: Ignoring i18n (strings weren't updated in po files)
                            email: gettext("The email address or username you've provided isn't formatted correctly."),
                            min: gettext('%(field)s must have at least %(count)d characters.'),
                            max: gettext('%(field)s can only contain up to %(count)d characters.'),
                            required: gettext('Please enter your %(field)s.')
                        },

                        field: function(el) {
                            var $el = $(el),
                                required = true,
                                min = true,
                                max = true,
                                email = true,
                                response = {},
                                isBlank = _fn.validate.isBlank($el);

                            if (_fn.validate.isRequired($el)) {
                                if (isBlank) {
                                    required = false;
                                } else {
                                    min = _fn.validate.str.minlength($el);
                                    max = _fn.validate.str.maxlength($el);
                                    email = _fn.validate.email.valid($el);
                                }
                            } else if (!isBlank) {
                                min = _fn.validate.str.minlength($el);
                                max = _fn.validate.str.maxlength($el);
                                email = _fn.validate.email.valid($el);
                            }

                            response.isValid = required && min && max && email;

                            if (!response.isValid) {
                                _fn.validate.removeDefault($el);

                                response.message = _fn.validate.getMessage($el, {
                                    required: required,
                                    min: min,
                                    max: max,
                                    email: email
                                });
                            }

                            return response;
                        },

                        str: {

                            minlength: function($el) {
                                var min;
                                var isEmailValue =  _fn.validate.email.regex.test($el.val());
                                var isUsernameValue = _fn.validate.username.ascii_regex.test($el.val());

                                if ($el.attr('type') === 'email') {
                                    if (isEmailValue) {
                                        min = $el.attr('minlength');
                                    } else if (isUsernameValue) {
                                        min = USERNAME_MIN_LENGTH;
                                    } else {
                                        min = 0;
                                    }
                                } else {
                                    min = 0;
                                }

                                return min <= $el.val().length;
                            },

                            maxlength: function($el) {
                                var max;
                                var isEmailValue =  _fn.validate.email.regex.test($el.val());
                                var isUsernameValue = _fn.validate.username.ascii_regex.test($el.val());

                                if ($el.attr('type') === 'email') {
                                    if (isEmailValue) {
                                        max = $el.attr('maxlength');
                                    } else if (isUsernameValue) {
                                        max = USERNAME_MAX_LENGTH;
                                    } else {
                                        max = 0;
                                    }
                                } else {
                                    max = 0;
                                }

                                return (!!max) ? max >= $el.val().length : true;
                            }
                        },

                        isRequired: function($el) {
                            return $el.attr('required');
                        },

                        isBlank: function($el) {
                            var type = $el.attr('type'),
                                isBlank;

                            if (type === 'checkbox') {
                                isBlank = !$el.prop('checked');
                            } else if (type === 'select') {
                                isBlank = ($el.data('isdefault') === true);
                            } else {
                                isBlank = !$el.val();
                            }

                            return isBlank;
                        },

                        // To support login by username
                        username: {
                            // In general case, username can only contain letters (A-Z, a-z), numerals (0-9), underscores (_), and hyphens (-)
                            ascii_regex: new RegExp('^([A-Za-z0-9-_]+)$'),
                            // If the `ENABLE_UNICODE_USERNAME` feature enabled, username can only contain letters, numerals, and @/./+/-/_ characters
                            // unicode_regex: new RegExp('^([A-Za-z0-9_@.+-]+)$'),
                        },

                        email: {
                        // This is the same regex used to validate email addresses in Django 1.11
                            regex: new RegExp(
                            [
                                '(^[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+(\\.[-!#$%&\'*+/=?^_`{}|~0-9A-Z]+)*',
                                '|^"([\\001-\\010\\013\\014\\016-\\037!#-\\[\\]-\\177]|\\\\[\\001-\\011\\013\\014\\016-\\177])*"', // eslint-disable-line max-len
                                ')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\\.)+)(?:[A-Z0-9-]{2,63})',
                                '|\\[(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)(\\.(25[0-5]|2[0-4]\\d|[0-1]?\\d?\\d)){3}\\]$'
                            ].join(''), 'i'
                        ),

                            valid: function($el) {
                                return $el.attr('type') === 'email' ? _fn.validate.email.format($el.val()) : true;
                            },

                            format: function(str) {
                                const isValidEmail = _fn.validate.email.regex.test(str);
                                const isValidAsciiUsername = _fn.validate.username.ascii_regex.test(str);
                                // Neglecting the `ENABLE_UNICODE_USERNAME` feature
                                // const isValidUnicodeUsername = _fn.validate.username.unicode_regex.test(str);
                                return isValidEmail || isValidAsciiUsername;
                            }
                        },

                        getLabel: function(id) {
                        // Extract the field label, remove the asterisk (if it appears) and any extra whitespace
                            return $('label[for=' + id + '] > span.label-text').text().split('*')[0].trim();
                        },

                        getMessage: function($el, tests) {
                            var txt = [],
                                label,
                                context,
                                content,
                                customMsg,
                                liveValidationMsg,
                                isEmailValue,
                                isUsernameValue;

                            _.each(tests, function(value, key) {
                                if (!value) {
                                    label = _fn.validate.getLabel($el.attr('id'));
                                    customMsg = $el.data('errormsg-' + key) || false;
                                    liveValidationMsg =
                                        $('#' + $el.attr('id') + '-validation-error-msg').text() || false;
                                    isEmailValue =  _fn.validate.email.regex.test($el.val());

                                // If the field has a custom error msg attached, use it
                                    if (customMsg) {
                                        content = customMsg;
                                    } else if (liveValidationMsg) {
                                        content = liveValidationMsg;
                                    } else {
                                        context = {field: label};

                                        if (key === 'min') {
                                            context.count = isEmailValue ? parseInt($el.attr('minlength'), 10) : USERNAME_MIN_LENGTH;
                                        } else if (key === 'max') {
                                            context.count = isEmailValue ? parseInt($el.attr('maxlength'), 10) : USERNAME_MAX_LENGTH;
                                        }

                                        content = _.sprintf(_fn.validate.msg[key], context);
                                    }

                                    txt.push(_fn.validate.template({
                                        content: content
                                    }));
                                }
                            });

                            return txt.join(' ');
                        },

                    // Removes the default HTML5 validation pop-up
                        removeDefault: function($el) {
                            if ($el.setCustomValidity) {
                                $el.setCustomValidity(' ');
                            }
                        }
                    }
                };

                return {
                    validate: _fn.validate.field
                };
            }());

            return utils;
        });
}).call(this, define || RequireJS.define);
