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

                this.facetOptions = new Backbone.Collection([], {model: FacetOption});
            },

            parse: function(response) {
                var courses = response.results || [];
                var facets = response.facets || {};
                var programs = response.programs || [];

                _(programs).each(function(program, idx) {
                    program.courses = _.pluck(program.courses, 'data');
                });

                this.programCards.add(programs);

                this.set({
                    totalCount: response.total + response.programs_total,
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
            },
            

            reset: function() {
                this.set({
                    totalCount: 0,
                    latestCount: 0
                });
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
