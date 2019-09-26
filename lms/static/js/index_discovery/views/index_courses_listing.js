(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'js/index_discovery/views/index_course_card',
    ], function($, _, Backbone, gettext, IndexCourseCardView) {
        'use strict';

        return Backbone.View.extend({

            el: 'section.courses',
            $window: $(window),
            $document: $(document),

            initialize: function() {
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
                var items = this.model.models.map(function(item) {
                    item.userPreferences = this.model.userPreferences;
                    var courseItem = new IndexCourseCardView({model: item});
                    return courseItem.render().el;
                }, this);

                this.$list.append(items)
                return this.el;
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
