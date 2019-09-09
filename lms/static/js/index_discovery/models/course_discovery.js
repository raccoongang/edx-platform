(function(define) {
    define([
        'underscore',
        'backbone',
        'js/index_discovery/models/program_card',
        'js/index_discovery/models/course_card',
        'js/index_discovery/models/facet_option'
    ], function(_, Backbone, ProgramCard, CourseCard, FacetOption) {
        'use strict';

        return Backbone.Model.extend({
            url: '/search/course_discovery/',
            jqhxr: null,

            defaults: {
                totalCount: 0,
                latestCount: 0
            },

            initialize: function() {
                this.programCards = new Backbone.Collection([], {model: ProgramCard})
                this.courseCards = new Backbone.Collection([], {model: CourseCard});
                this.facetOptions = new Backbone.Collection([], {model: FacetOption});
            },

            parse: function(response) {
                console.log('Parsing Course Discovery: ', response);

                var programs_dummies = [
                    {
                        'title': 'Test Program',
                        'subtitle': 'Test Program subtitle',
                        'courses': [
                            'course-v1:edX+DemoX+2019_Kirill_Test_2',
                            'course-v1:edX+DemoX+2019_Kirill_Test_3',
                        ]
                    },
                    {
                        'title': 'Second Test Program',
                        'subtitle': 'Second Test Program subtitle',
                        'courses': [
                            'course-v1:TestRG+TestRG+TestRG',
                            'course-v1:edX+DemoX+2019_Kirill_Test_4',
                            'course-v1:edX+DemoX+2019_Kirill_Test_5',
                            'course-v1:edX+DemoX+2019_Kirill_Test_5',
                        ]
                    },
                ]
                var courses = response.results || [];
                var facets = response.facets || {};
                var programs = response.programs || programs_dummies || [];

                this.courseCards.add(_.pluck(courses, 'data'));
                this.programCards.add(programs);

                this.set({
                    totalCount: response.total,
                    latestCount: courses.length
                });

                var options = this.facetOptions;
                _(facets).each(function(obj, key) {
                    _(obj.terms).each(function(count, term) {
                        options.add({
                            facet: key,
                            term: term,
                            count: count
                        }, {merge: true});
                    });
                });

                console.log('Course cards: ', this.courseCards);
                console.log('Program cards: ', this.programCards);
                console.log('Facets: ', facets);
                console.log('this.facetOptions(options): ', options);
            },
            

            reset: function() {
                this.set({
                    totalCount: 0,
                    latestCount: 0
                });
                this.courseCards.reset();
                this.programCards.reset();
                this.facetOptions.reset();
            },

            latest: function() {
                return this.programCards;
            },

            getPrograms: function() {
                return this.programCards.rest(0);
            }
        });
    });
}(define || RequireJS.define));
