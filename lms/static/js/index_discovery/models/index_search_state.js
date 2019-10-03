(function(define) {
    define([
        'underscore',
        'backbone',
        'js/index_discovery/models/index_course_discovery',
    ], function(_, Backbone, IndexCourseDiscovery) {
        'use strict';


        return Backbone.Model.extend({

            page: 0,
            pageSize: 100,
            searchTerm: '',
            terms: {},
            jqhxr: null,

            initialize: function() {
                this.discovery = new IndexCourseDiscovery();
                this.listenTo(this.discovery, 'sync', this.onSync, this);
                this.listenTo(this.discovery, 'error', this.onError, this);
            },

            performSearch: function(searchTerm, otherTerms) {
                this.reset();
                this.searchTerm = searchTerm;
                if (otherTerms) {
                    this.terms = otherTerms;
                }
                this.sendQuery(this.buildQuery(0));
            },

            refineSearch: function(terms) {
                this.reset();
                this.terms = terms;
                this.sendQuery(this.buildQuery(0));
            },

            loadNextPage: function() {
                if (this.hasNextPage()) {
                    this.sendQuery(this.buildQuery(this.page + 1));
                }
            },

            filterFacets: function(filterWord) {
                this.discovery.filterFacetOptions(filterWord);
            },

            resetFacets: function() {
                this.discovery.resetFacetOptions();
            },

        // private

            hasNextPage: function() {
                var total = this.discovery.get('totalCount');
                return total - ((this.page + 1) * this.pageSize) > 0;
            },

            sendQuery: function(data) {
                this.jqhxr && this.jqhxr.abort();
                this.jqhxr = this.discovery.fetch({
                    type: 'POST',
                    data: data
                });

                return this.jqhxr;
            },

            buildQuery: function(pageIndex) {
                var data = {
                    search_string: this.searchTerm,
                    page_size: this.pageSize,
                    page_index: pageIndex
                };
                _.extend(data, this.terms);
                return data;
            },

            reset: function() {
                this.discovery.reset();
                this.page = 0;
                this.errorMessage = '';
            },

            onError: function(collection, response, options) {
                if (response.statusText !== 'abort') {
                    this.errorMessage = response.responseJSON.error;
                    this.trigger('error');
                }
            },

            onSync: function(collection, response, options) {
                var total = this.discovery.get('totalCount');
                var programsTotal = this.discovery.get('programsTotalCount');
                var originalSearchTerm = this.searchTerm;
                if (options.data.page_index === 0) {
                    if (total === 0) {
                    // list all courses
                        this.cachedDiscovery().done(function(cached) {
                            this.discovery.programCards.reset(cached.programCards.toJSON());
                            this.discovery.facetOptions.reset(cached.facetOptions.toJSON());
                            this.discovery.set('latestCount', cached.get('latestCount'));
                            this.trigger('search', originalSearchTerm, total, programsTotal);
                        });
                        this.searchTerm = '';
                        this.terms = {};
                    } else {
                        _.each(this.terms, function(term, facet) {
                            if (facet !== 'search_query') {
                                var option = this.discovery.facetOptions.findWhere({
                                    facet: facet,
                                    term: term
                                });
                                if (option) {
                                    option.set('selected', true);
                                }
                            }
                        }, this);
                        this.trigger('search', this.searchTerm, total, programsTotal);
                    }
                } else {
                    this.page = options.data.page_index;
                    this.trigger('next');
                }
            },

        // lazy load
            cachedDiscovery: function() {
                var deferred = $.Deferred();
                var self = this;

                if (this.cached) {
                    deferred.resolveWith(this, [this.cached]);
                } else {
                    this.cached = new IndexCourseDiscovery();
                    this.cached.fetch({
                        type: 'POST',
                        data: {
                            search_string: '',
                            page_size: this.pageSize,
                            page_index: 0
                        },
                        success: function(model, response, options) {
                            deferred.resolveWith(self, [model]);
                        }
                    });
                }
                return deferred.promise();
            }

        });
    });
}(define || RequireJS.define));
