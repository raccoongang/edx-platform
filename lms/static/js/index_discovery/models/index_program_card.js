(function(define) {
    define(['backbone'], function(Backbone) {
        'use strict';

        return Backbone.Model.extend({
            defaults: {
                title: '',
                subtitle: '',
                courses: []
            }
        });
    });
}(define || RequireJS.define));
