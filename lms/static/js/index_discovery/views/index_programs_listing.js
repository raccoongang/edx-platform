(function(define) {
    define([
        'jquery',
        'underscore',
        'backbone',
        'gettext',
        'js/index_discovery/views/index_program_card'
    ], function($, _, Backbone, gettext, IndexProgramCardView) {
        'use strict';

        return Backbone.View.extend({

            el: 'div.programs',
            $window: $(window),
            $document: $(document),

            /**
            * Sort a group of courses as per custom rules.
            *
            * Workaround for FLS-499.
            */
            reorderCourses: function() {
              const COURSES_ORDER = [
               "course-v1:Lakeside+TE101+2019",  // The Essentials of Trauma - The Opioid Crisis
               "course-v1:NeuroLogic+NL101+2020Q2",  // The Trauma-Informed Classroom
               "course-v1:Neurologic+NL105+2021_T1", // Resilience: Increasing Students' Tolerance for Stress
               "course-v1:LakesideGlobalInstitute+2000+2020_T1",  // Enhancing Trauma Awareness
               "course-v1:Lakeside+PRE1101+2020",  // PRESENCE - Introductory Track
               "course-v1:Lakeside+PRE1101+2020_T2",  // PRESENCE-Leadership Track
               "course-v1:Lakeside+PRE1103+2029_T2",  // PRESENCE - Clinical Track
              ]

              for (let j = 0; j < $(".courses-listing").children.length; j++) {

               const el = $(".courses-listing")[j];
               const firstCoursesHtml = [];
               const remainingCoursesHtml = [];
               let allCourses = [];

               const getCourseKey = function (element) {
                 // e.g. "/courses/course-v1:Lakeside+PRE1103+2029_T2/about"
                 let href = element.childNodes[1].childNodes[1].attributes["href"];
                 if (typeof (href) === "object") {
                   // Not sure why object in some cases
                   href = String(href.value);
                 }
                 let courseKey = null;
                 const courseKeyMatch = href.match(/(?<=courses\/)(.*?)(?=\/)/);
                 if (courseKeyMatch === null) {
                   // Might not be a course (a product, probably).
                   // Shouldn't run into this in the courses-listing section of interest.
                   return;
                 } else {
                   courseKey = courseKeyMatch[0];
                 }
                 // e.g. "course-v1:Lakeside+PRE1103+2029_T2"
                 return courseKey;
               }

               // Add all the courses from the current courses-listing, excluding the ones configured in COURSES_ORDER
               for (let i = 0; i < el.children.length; i++) {
                 const li = el.children[i];
                 const courseKey = getCourseKey(li);
                 if (COURSES_ORDER.indexOf(courseKey) === -1) {
                   remainingCoursesHtml.push("<li class='courses-listing-item' test-attr='attr'>" + li.innerHTML + "</li>");
                 }
               }

               // Populate the first batch of courses (the one we want sorted as per COURSES_ORDER)
               for (let k = 0; k < COURSES_ORDER.length; k++) {
                 for (let i = 0; i < el.children.length; i++) {
                   const li = el.children[i];
                   const courseKey = getCourseKey(li);
                   if (courseKey === COURSES_ORDER[k]) {
                     firstCoursesHtml.push("<li class='courses-listing-item' test-attr='attr'>" + li.innerHTML + "</li>");
                   }
                 }

               }

               // Replace the courses-listing section's content with a new one
               if (firstCoursesHtml.length > 0) {
                 allCourses = firstCoursesHtml.concat(remainingCoursesHtml);
                 el.innerHTML = allCourses.join("");
               } else {
                 console.info("Didn't sort a certain group of courses, and it's fine.")
               }

              }
            },

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
                    var itemView = new IndexProgramCardView({model: item});
                    return itemView.render().el;
                });

                this.$list.append(items);
                this.reorderCourses();
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
