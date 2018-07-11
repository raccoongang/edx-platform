(function(define) {
    'use strict';
    define([
        'jquery',
        'js/student_account/views/FormView'
    ],
        function($, FormView) {
            return FormView.extend({
                el: '#password-reset-form',

                tpl: '#password_reset-tpl',

                events: {
                    'click .js-reset': 'submitForm'
                },

                formType: 'password-reset',

                requiredStr: '',
                optionalStr: '',

                submitButton: '.js-reset',

                preRender: function(data) {
                    this.googleRecaptchaSiteKey = data.googleRecaptchaSiteKey;
                    this.element.show($(this.el));
                    this.element.show($(this.el).parent());
                    this.listenTo(this.model, 'sync', this.saveSuccess);
                },

                render: function(html) {
                    var fields = html || '';

                    $(this.el).html(_.template(this.tpl)({
                        fields: fields,
                        googleRecaptchaSiteKey: this.googleRecaptchaSiteKey
                    }));

                    this.postRender();

                    return this;
                },

                saveSuccess: function() {
                    this.trigger('password-email-sent');

                // Destroy the view (but not el) and unbind events
                    this.$el.empty().off();
                    this.stopListening();
                }
            });
        });
}).call(this, define || RequireJS.define);
