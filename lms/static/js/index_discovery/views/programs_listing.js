(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'js/index_discovery/views/program_card'
    ], function($, _, Backbone, gettext, ProgramCardView) {
        'use strict';

        return Backbone.View.extend({

            el: 'div.programs',
            $window: $(window),
            $document: $(document),

            initialize: function() {
                this.$list = this.$el.find('.programs-listing');
                this.attachScrollHandler();
            },

            render: function() {
                this.$list.empty();
                this.renderItems();
                return this;
            },

            renderNext: function() {
                this.renderItems();
                this.isLoading = false;
            },

            renderItems: function() {
                /* eslint no-param-reassign: [2, { "props": true }] */
                var latest = this.model.latest();

                var items = latest.map(function(item) {
                    var itemView = new ProgramCardView({model: item, testParam: 'testParam'});
                    return itemView.render().el;
                });

                this.$list.append(items);

                /* eslint no-param-reassign: [2, { "props": false }] */
            },

            attachScrollHandler: function() {
                this.$window.on('scroll', _.throttle(this.scrollHandler.bind(this), 400));
            },

            scrollHandler: function() {
                if (this.isNearBottom() && !this.isLoading) {
                    this.trigger('next');
                    this.isLoading = true;
                }
            },

            isNearBottom: function() {
                var scrollBottom = this.$window.scrollTop() + this.$window.height();
                var threshold = this.$document.height() - 200;
                return scrollBottom >= threshold;
            }

        });
    });
}(define || RequireJS.define));
