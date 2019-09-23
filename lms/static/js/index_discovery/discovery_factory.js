(function(define) {
    'use strict';

    define(['backbone',
            'js/index_discovery/models/search_state',
            'js/index_discovery/collections/filters',
            'js/index_discovery/views/search_form',
            'js/index_discovery/views/facet_filter/form',
            'js/index_discovery/views/programs_listing',
            'js/index_discovery/views/courses_listing',
            'js/index_discovery/views/course_card',
            'js/index_discovery/views/filter_bar',
            'js/index_discovery/views/refine_sidebar'],
        function(Backbone, SearchState, Filters, SearchForm, FacetFilterForm, ProgramsListing, CoursesListing, CourseCard, FilterBar, RefineSidebar) {
            return function(meanings, searchQuery, userLanguage, userTimezone) {
                var dispatcher = _.extend({}, Backbone.Events);
                var searchState = new SearchState();
                var filters = new Filters();
                var searchForm = new SearchForm();
                var facetFilterForm = new FacetFilterForm();
                var filterBar = new FilterBar({collection: filters});
                var refineSidebar = new RefineSidebar({
                    collection: searchState.discovery.facetOptions,
                    meanings: meanings
                });
                var programListingModel = searchState.discovery;

                programListingModel.userPreferences = {
                    userLanguage: userLanguage,
                    userTimezone: userTimezone
                };

                programListingModel.coursesListing = {
                    cardViewClass: CourseCard,
                    viewClass: CoursesListing,
                };

                var listing = new ProgramsListing({model: programListingModel});

                dispatcher.listenTo(searchForm, 'search', function(query) {
                    filters.reset();
                    searchForm.showLoadingIndicator();
                    searchState.performSearch(query, filters.getTerms());
                });

                dispatcher.listenTo(refineSidebar, 'selectOption', function(type, query, name) {
                    searchForm.showLoadingIndicator();
                    if (filters.get(type)) {
                        removeFilter(type);
                    } else {
                        filters.add({type: type, query: query, name: name});
                        searchState.refineSearch(filters.getTerms());
                    }
                });

                dispatcher.listenTo(filterBar, 'clearFilter', removeFilter);

                dispatcher.listenTo(filterBar, 'clearAll', function() {
                    facetFilterForm.clearInput();
                    searchForm.doSearch('');
                });

                dispatcher.listenTo(listing, 'next', function() {
                    searchState.loadNextPage();
                });

                dispatcher.listenTo(searchState, 'next', function() {
                    listing.renderNext();
                });

                dispatcher.listenTo(searchState, 'search', function(query, total) {
                    if (total > 0) {
                        searchForm.showFoundMessage(total);
                        if (query) {
                            filters.add(
                                {type: 'search_query', query: query, name: quote(query)},
                                {merge: true}
                            );
                        }
                    } else {
                        searchForm.showNotFoundMessage(query);
                        filters.reset();
                    }
                    searchForm.hideLoadingIndicator();
                    listing.render();
                    refineSidebar.render();
                });

                dispatcher.listenTo(searchState, 'error', function() {
                    searchForm.showErrorMessage(searchState.errorMessage);
                    searchForm.hideLoadingIndicator();
                });

                dispatcher.listenTo(facetFilterForm.facetFilterInput, 'filter', function(filterWord) {
                    searchState.filterFacets(filterWord);
                    refineSidebar.render();
                });

                dispatcher.listenTo(facetFilterForm.facetFilterInput, 'resetFilter', function() {
                    searchState.resetFacets();
                    refineSidebar.render();
                });

                // kick off search on page refresh
                searchForm.doSearch(searchQuery);

                function removeFilter(type) {
                    facetFilterForm.clearInput();
                    searchForm.showLoadingIndicator();
                    filters.remove(type);
                    if (type === 'search_query') {
                        searchForm.doSearch('');
                    } else {
                        searchState.refineSearch(filters.getTerms());
                    }
                }

                function quote(string) {
                    return '"' + string + '"';
                }
            };
        });
}(define || RequireJS.define));
