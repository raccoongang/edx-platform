(function(define) {
    define([
        'underscore',
        'backbone',
        'js/index_discovery/models/index_program_card',
        'js/index_discovery/models/index_course_card',
        'js/index_discovery/models/index_facet_option'
    ], function(_, Backbone, IndexProgramCard, IndexCourseCard, IndexFacetOption) {
        'use strict';

        return Backbone.Model.extend({
            url: '/search/course_discovery/',
            jqhxr: null,

            defaults: {
                totalCount: 0,
                programsTotalCount: 0,
                latestCount: 0
            },

            initialize: function() {
                this.programCards = new Backbone.Collection([], {model: IndexProgramCard});

                this.facetOptions = new Backbone.Collection([], {model: IndexFacetOption});
                this.originalFacetOptions = new Backbone.Collection([], {model: IndexFacetOption})
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
                    totalCount: response.total,
                    programsTotalCount: response.programs_total,
                    latestCount: courses.length
                });

                var options = this.facetOptions;
                var originalOptions = this.originalFacetOptions;

                _(facets).each(function(obj, key) {
                    _(obj.terms).each(function(count, term) {
                        options.add({
                            facet: key,
                            term: term,
                            count: count
                        }, {merge: true});
                        originalOptions.add({
                            facet: key,
                            term: term,
                            count: count
                        }, {merge: true})
                    });
                });
            },

            filterFacetOptions: function(filterWord) {
                var filteredFacets = this.originalFacetOptions.filter(function(facet) {
                    if (facet.id.toLowerCase().includes(filterWord)) {
                        return facet;
                    }
                });

                this.facetOptions.set(filteredFacets);
            },

            resetFacetOptions: function() {
                var originalFacetOptionsCollection = this.originalFacetOptions.filter(function(facet) {
                    return facet;
                });

                this.facetOptions.reset(originalFacetOptionsCollection);
            },

            reset: function() {
                this.set({
                    totalCount: 0,
                    programsTotalCount: 0,
                    latestCount: 0
                });
                this.programCards.reset();
                this.facetOptions.reset();
                this.originalFacetOptions.reset()
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
