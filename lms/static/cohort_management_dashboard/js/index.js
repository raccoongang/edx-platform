(function (define) {
    'use strict';
    define([
        'jquery',
        'underscore',
        'text!cohort_management_dashboard/templates/student_table_body.underscore'
    ], function ($, _, studetTableBodyTemplate) {
        return function (options) {
            var $slectControl = $('.action-cohort-select');
            var cohorts = null;
            var cohortID = options.cohort_id;

            function reloadThisPage() {
                location.href = options.self_page_url.replace(options.template_cohort_id_key, cohortID);
            }

            function removeUser(username) {
                var requestUrl = options.remove_from_cohort_url.replace(options.template_cohort_id_key, cohortID);
                Promise.resolve($.ajax({
                    url: requestUrl,
                    type: 'POST',
                    data: {username: username}
                })).then(reloadThisPage);
            }

            function moveUser(username, newCohortID) {
                var requestUrl = options.add_to_cohort_url.replace(options.template_cohort_id_key, newCohortID);
                Promise.resolve($.ajax({
                    url: requestUrl,
                    type: 'POST',
                    data: {users: username}
                })).then(reloadThisPage);
            }

            function fillTableWithStudent(usersList) {
                $('.member-list tbody').html(_.template(studetTableBodyTemplate)({
                    users: usersList,
                    cohorts: cohorts,
                    currentCohortID: cohortID,
                }));
                $('.member-list tbody .remove-user').click(function (e) {
                    removeUser(e.target.dataset.username);
                });
                $('.member-list tbody .change-cohort-btn').click(function (e) {
                    moveUser(
                        e.target.dataset.username,
                        $(e.target.parentElement).find('select')[0].value
                    );
                });
            }

            function onCohortChanged(newCohortID, page, usersList) {
                var requestUrl = null;
                cohortID = newCohortID;
                if (page === undefined) {
                    // eslint-disable-next-line no-param-reassign
                    page = 1;
                }
                if (usersList === undefined) {
                    // eslint-disable-next-line no-param-reassign
                    usersList = [];
                }

                requestUrl = options.list_cohort_url.replace(options.template_cohort_id_key, cohortID);
                requestUrl += '?page=' + page;

                Promise.resolve($.ajax({
                    url: requestUrl,
                    type: 'GET'
                })).then(function (result) {
                    // eslint-disable-next-line no-param-reassign
                    usersList = usersList.concat(result.users);
                    if (result.page === result.num_pages) {
                        if (usersList.length === 0) {
                            location.href = options.empty_user_list_redirect;
                            return;
                        }
                        fillTableWithStudent(usersList);
                    } else {
                        onCohortChanged(newCohortID, page + 1, usersList);
                    }
                });
            }

            function bindCohortChangeLoster() {
                $slectControl.change(function (e) {
                    onCohortChanged(e.target.value);
                });
            }

            function displaySelectControl(cohortsList) {
                function emptyCohortFilter(cohort) {
                    return cohort.user_count > 0;
                }

                cohorts = cohortsList.cohorts;
                $.each(cohorts.filter(emptyCohortFilter), function (key, value) {
                    $slectControl.append($('<option></option>').attr('value', value.id).text(value.name));
                });
                cohortID = options.cohort_id;
                if (cohortID === undefined || cohortID === null || cohortID === 'None') {
                    cohortID = cohortsList.cohorts.filter(emptyCohortFilter)[0].id;
                }
                bindCohortChangeLoster();
                $slectControl.find('option[value="' + cohortID + '"]').prop('selected', true);
                onCohortChanged(cohortID);
            }

            function loadCohortsList() {
                Promise.resolve($.ajax({
                    url: options.cohorts_url,
                    type: 'GET'
                })).then(displaySelectControl);
            }

            loadCohortsList();
        };
    });
}).call(this, define || RequireJS.define);
