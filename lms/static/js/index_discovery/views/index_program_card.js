(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'edx-ui-toolkit/js/utils/date-utils',
        'js/index_discovery/models/index_course_card',
        'js/index_discovery/views/index_courses_listing'
    ], function($, _, Backbone, gettext, DateUtils, IndexCourseCard, IndexCoursesListing) {
        'use strict';

        function formatDate(date, userLanguage, userTimezone) {
            var context;
            context = {
                datetime: date,
                language: userLanguage,
                timezone: userTimezone,
                format: DateUtils.dateFormatEnum.shortDate
            };
            return DateUtils.localize(context);
        }

        return Backbone.View.extend({

            tagName: 'div',
            templateId: '#program_card-tpl',
            className: 'program-listing-item',

            initialize: function() {
                this.tpl = _.template($(this.templateId).html());
            },

            render: function() {
                var data = _.clone(this.model.attributes);

                this.renderTemplate(data);
                this.renderCourseCards(data.courses);

                return this;
            },

            renderTemplate: function(data) {
                this.$el.html(this.tpl(data));
            },

            renderCourseCards: function(courses) {
                var programCoursesCards = new Backbone.Collection([], IndexCourseCard);

                programCoursesCards.add(courses);

                var programCoursesCardsListing = new IndexCoursesListing({model: programCoursesCards});
                programCoursesCardsListing.$list = this.$('.courses-listing');

                programCoursesCardsListing.render();


            }

        });
    });
}(define || RequireJS.define));
