(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'js/index_discovery/views/course_card',
        'js/index_discovery/views/program_card'
    ], function($, _, Backbone, gettext, CourseCardView, ProgramCardView) {
        'use strict';

        return Backbone.View.extend({

            el: 'div.courses',
            $window: $(window),
            $document: $(document),

            initialize: function() {
                this.$list = this.$el.find('.courses-listing');
                this.attachScrollHandler();
            },

            render: function() {
                console.log('Rendering course listing...');
                console.log('Something else is going on...');

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
                console.log('Rendering items (latest): ', latest);
                var programs = this.model.getPrograms();
                console.log('Rendering items (programs): ', programs);

                var items = latest.map(function(result) {
                    result.userPreferences = this.model.userPreferences;
                    var item = new CourseCardView({model: result});
                    return item.render().el;
                }, this);

                console.log('Rendering items: ', items);

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
