(function(define) {
    'use strict';
    define(['backbone'], function(Backbone) {
        var CohortModel = Backbone.Model.extend({
            idAttribute: 'id',
            defaults: {
                name: '',
                user_count: 0,
                /**
                 * Indicates how students are added to the cohort. Will be "manual" (signifying manual assignment) or
                 * "random" (indicating students are randomly assigned).
                 */
                assignment_type: '',
                /**
                 * If this cohort is associated with a user partition group, the ID of the user partition.
                 */
                user_partition_id: null,
                /**
                 * If this cohort is associated with a user partition group, the ID of the group within the
                 * partition associated with user_partition_id.
                 */
                group_id: null,
                /**
                 * List of users' emails with admin access for particular cohort.
                 */
                cohort_admins: []
            },

            validate: function(attrs) {
                var newCohortAdmins = attrs.cohort_admins.slice(0);
                if (newCohortAdmins.indexOf(newCohortAdmins.pop()) !== -1) {
                    return 'Duplicate error';
                }
            },

            addCohortAdmin: function(user) {
                this.set({
                    cohort_admins: this.get('cohort_admins').concat(user)
                }, {
                    validate: true
                });
            },

            removeCohortAdmin: function(user) {
                this.set({
                    cohort_admins: this.get('cohort_admins').filter(function(value) {return value !== user;})
                });
            },
        });
        return CohortModel;
    });
}).call(this, define || RequireJS.define);
