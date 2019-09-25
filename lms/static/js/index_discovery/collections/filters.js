(function(define) {
    define([
        'backbone',
        'js/index_discovery/models/filter'
    ], function(Backbone, IndexFilter) {
        'use strict';

        return Backbone.Collection.extend({
            model: IndexFilter,
            getTerms: function() {
                return this.reduce(function(terms, filter) {
                    terms[filter.id] = filter.get('query');
                    return terms;
                }, {});
            }
        });
    });
}(define || RequireJS.define));
