(function(define) {
    define(['jquery',
            'backbone',
            'js/index_discovery/views/facet_filter/index_input'],
        function($, Backbone, FacetFilterInput) {
            'use strict';

            return Backbone.View.extend({
                el: '#search-facet-filter',
                events: {
                    'submit form': 'onSubmitForm'
                },

                initialize: function() {
                    this.facetFilterInput = new FacetFilterInput();
                },

                onSubmitForm: function(event) {
                    event.preventDefault();
                },

                clearInput: function() {
                    this.facetFilterInput.clear();
                }
            });
    });
}(define || RequireJS.define));
