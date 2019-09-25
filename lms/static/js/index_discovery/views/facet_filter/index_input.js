(function(define) {
    define(['jquery', 'backbone', 'gettext'],
        function($, Backbone, gettext) {
            'use strict';

            return Backbone.View.extend({
                el: '#facet-filter-input',
                events: {
                    'keyup': 'onKeyUp'
                },

                initialize: function() {
                    this.minimalSearchInputLength = 3;
                    this.filtering = false;
                },

                onKeyUp: function(event) {
                    event.preventDefault();
                    var inputValue = this.el.value;

                    if (inputValue.length >= this.minimalSearchInputLength) {
                        this.filtering = true;
                        this.trigger('filter', inputValue);
                    } else {
                        if (this.filtering) {
                            this.trigger('resetFilter');
                            this.filtering = false;
                        }
                    }
                },

                clear: function() {
                    this.el.value = '';
                }
            });
        });
}(define || RequireJS.define));
