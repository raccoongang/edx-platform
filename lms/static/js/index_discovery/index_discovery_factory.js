(function(define) {
    'use strict';

    define(
        ['jquery',
        'backbone',
        'js/index_discovery/models/index_search_state',
        'js/index_discovery/collections/index_filters',
        'js/index_discovery/views/index_search_form',
        'js/index_discovery/views/facet_filter/index_form',
        'js/index_discovery/views/index_programs_listing',
        'js/index_discovery/views/index_courses_listing',
        'js/index_discovery/views/index_course_card',
        'js/index_discovery/views/index_filter_bar',
        'js/index_discovery/views/index_refine_sidebar'],
        function(
            $,
            Backbone,
            IndexSearchState,
            IndexFilters,
            IndexSearchForm,
            IndexFacetFilterForm,
            IndexProgramsListing,
            IndexCoursesListing,
            IndexCourseCard,
            IndexFilterBar,
            IndexRefineSidebar
        ) {
            /**
            * Sort a group of courses as per custom rules.
            *
            * Workaround for FLS-499.
            */
            const reorderCourses = function() {
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
            }

            return function(meanings, searchQuery, userLanguage, userTimezone) {
                var dispatcher = _.extend({}, Backbone.Events);
                var searchState = new IndexSearchState();
                var filters = new IndexFilters();
                var searchForm = new IndexSearchForm();
                var facetFilterForm = new IndexFacetFilterForm();
                var filterBar = new IndexFilterBar({collection: filters});
                var refineSidebar = new IndexRefineSidebar({
                    collection: searchState.discovery.facetOptions,
                    meanings: meanings
                });
                var programListingModel = searchState.discovery;

                programListingModel.userPreferences = {
                    userLanguage: userLanguage,
                    userTimezone: userTimezone
                };

                programListingModel.coursesListing = {
                    cardViewClass: IndexCourseCard,
                    viewClass: IndexCoursesListing,
                };

                var listing = new IndexProgramsListing({model: programListingModel});

                dispatcher.listenTo(searchForm, 'search', function(query) {
                    filters.reset();
                    searchForm.showLoadingIndicator();
                    searchState.performSearch(query, filters.getTerms());
                    //reorderCourses();
                });

                dispatcher.listenTo(refineSidebar, 'selectOption', function(type, query, name) {
                    searchForm.showLoadingIndicator();
                    if (filters.get(type)) {
                        removeFilter(type);
                    } else {
                        filters.add({type: type, query: query, name: name});
                        searchState.refineSearch(filters.getTerms());
                    }
                    //reorderCourses();
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

                dispatcher.listenTo(searchState, 'search', function(query, coursesTotal, programsTotal) {
                    var searchResultsCount = coursesTotal + programsTotal;

                    if (searchResultsCount > 0) {
                        searchForm.showFoundMessage(searchResultsCount);
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
                    reorderCourses();
                });

                dispatcher.listenTo(searchState, 'error', function() {
                    searchForm.showErrorMessage(searchState.errorMessage);
                    searchForm.hideLoadingIndicator();
                });

                dispatcher.listenTo(facetFilterForm.facetFilterInput, 'filter', function(filterWord) {
                    searchState.filterFacets(filterWord);
                    refineSidebar.render();
                    reorderCourses();
                });

                dispatcher.listenTo(facetFilterForm.facetFilterInput, 'resetFilter', function() {
                    searchState.resetFacets();
                    refineSidebar.render();
                    reorderCourses();
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
