(function(define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'logger',
        'js/student_account/models/user_account_model',
        'js/student_account/models/user_preferences_model',
        'js/student_account/views/account_settings_fields',
        'js/student_account/views/account_settings_view',
        'edx-ui-toolkit/js/utils/string-utils'
    ], function(gettext, $, _, Backbone, Logger, UserAccountModel, UserPreferencesModel,
                 AccountSettingsFieldViews, AccountSettingsView, StringUtils) {
        return function(
            fieldsData,
            ordersHistoryData,
            authData,
            passwordResetSupportUrl,
            userAccountsApiUrl,
            userPreferencesApiUrl,
            accountUserId,
            platformName,
            contactEmail,
            allowEmailChange,
            isWsFederationLogin
        ) {
            var accountSettingsElement, userAccountModel, userPreferencesModel, aboutSectionsData,
                accountsSectionData, ordersSectionData, accountSettingsView, showAccountSettingsPage,
                showLoadingError, orderNumber, getUserField, userFields, timeZoneDropdownField, countryDropdownField,
                emailFieldView, passwordFieldView;

            accountSettingsElement = $('.wrapper-account-settings');

            userAccountModel = new UserAccountModel();
            userAccountModel.url = userAccountsApiUrl;

            userPreferencesModel = new UserPreferencesModel();
            userPreferencesModel.url = userPreferencesApiUrl;

            if (allowEmailChange) {
                emailFieldView = {
                    view: new AccountSettingsFieldViews.EmailFieldView({
                        model: userAccountModel,
                        title: gettext('عنوان البريد الإلكتروني'),
                        valueAttribute: 'email',
                        helpMessage: StringUtils.interpolate(
                            gettext('البريد الإلكتروني الذي تستخدمه لتسجيل دخولك. تُرسَل جميع المراسلات من {platform_name} ومساقاتك إلى هذا العنوان.'),  // eslint-disable-line max-len
                            {platform_name: platformName}
                        ),
                        persistChanges: true
                    })
                };
            } else {
                emailFieldView = {
                    view: new AccountSettingsFieldViews.ReadonlyFieldView({
                        model: userAccountModel,
                        title: gettext('عنوان البريد الإلكتروني'),
                        valueAttribute: 'email',
                        helpMessage: StringUtils.interpolate(
                            gettext('The email address you use to sign in. Communications from {platform_name} and your courses are sent to this address.  To change the email address, please contact {contact_email}.'),  // eslint-disable-line max-len
                            {platform_name: platformName, contact_email: contactEmail}
                        )
                    })
                };
            }

            aboutSectionsData = [
                {
                    title: gettext('Basic Account Information'),
                    subtitle: gettext('تتضمّن هذه الإعدادات معلومات أساسية عن حسابك، ويمكنك أيضًا إدخال معلومات إضافية ورؤية حسابات التواصل الاجتماعي خاصتك المربوطة مع حسابك.'),  // eslint-disable-line max-len
                    fields: [
                        {
                            view: new AccountSettingsFieldViews.ReadonlyFieldView({
                                model: userAccountModel,
                                title: gettext('Username'),
                                valueAttribute: 'username',
                                helpMessage: StringUtils.interpolate(
                                    gettext('الإسم الذي يعرّف عنك في {platform_name}. لا يمكنك تغيير إسم المستخدم الخاص بك.'),  // eslint-disable-line max-len
                                    {platform_name: platformName}
                                )
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.ReadonlyFieldView({
                                model: userAccountModel,
                                title: gettext('Full Name'),
                                valueAttribute: 'name',
                                helpMessage: gettext(
                                    'الإسم المستخدم للتأكّد من الهوية والذي سيظهر على الشهادات. لن يرى المتعلّمون الآخرون إسمك الكامل نهائيًّا.'  // eslint-disable-line max-len
                                )
                            })
                        },
                        emailFieldView,
                        {
                            view: new AccountSettingsFieldViews.LanguagePreferenceFieldView({
                                model: userPreferencesModel,
                                title: gettext('Language'),
                                valueAttribute: 'pref-lang',
                                required: true,
                                refreshPageOnSave: true,
                                helpMessage: StringUtils.interpolate(
                                    gettext('اللغة المستخدمة في كافة أقسام هذا الموقع. يتوفّر هذا الموقع حاليًا بعدد محدود من اللغات.'),  // eslint-disable-line max-len
                                    {platform_name: platformName}
                                ),
                                options: fieldsData.language.options,
                                persistChanges: true
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.DropdownFieldView({
                                model: userAccountModel,
                                required: true,
                                title: gettext('الدولة أو المنطقة'),
                                valueAttribute: 'country',
                                options: fieldsData.country.options,
                                persistChanges: true
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.TimeZoneFieldView({
                                model: userPreferencesModel,
                                required: true,
                                title: gettext('Time Zone'),
                                valueAttribute: 'time_zone',
                                helpMessage: gettext('Select the time zone for displaying course dates. If you do not specify a time zone, course dates, including assignment deadlines, will be displayed in your browser\'s local time zone.'), // eslint-disable-line max-len
                                groupOptions: [{
                                    groupTitle: gettext('All Time Zones'),
                                    selectOptions: fieldsData.time_zone.options,
                                    nullValueOptionLabel: gettext('Default (Local Time Zone)')
                                }],
                                persistChanges: true
                            })
                        }
                    ]
                },
                {
                    title: gettext('Additional Information'),
                    fields: [
                        {
                            view: new AccountSettingsFieldViews.DropdownFieldView({
                                model: userAccountModel,
                                title: gettext('Education Completed'),
                                valueAttribute: 'level_of_education',
                                options: fieldsData.level_of_education.options,
                                persistChanges: true
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.DropdownFieldView({
                                model: userAccountModel,
                                title: gettext('Gender'),
                                valueAttribute: 'gender',
                                options: fieldsData.gender.options,
                                persistChanges: true
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.DropdownFieldView({
                                model: userAccountModel,
                                title: gettext('Year of Birth'),
                                valueAttribute: 'year_of_birth',
                                options: fieldsData.year_of_birth.options,
                                persistChanges: true
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.LanguageProficienciesFieldView({
                                model: userAccountModel,
                                title: gettext('Preferred Language'),
                                valueAttribute: 'language_proficiencies',
                                options: fieldsData.preferred_language.options,
                                persistChanges: true
                            })
                        }
                    ]
                }
            ];

            if (!isWsFederationLogin) {
                aboutSectionsData[0].fields.splice(3, 0, {
                    view: new AccountSettingsFieldViews.PasswordFieldView({
                        model: userAccountModel,
                        title: gettext('Password'),
                        screenReaderTitle: gettext('Reset Your Password'),
                        valueAttribute: 'password',
                        emailAttribute: 'email',
                        passwordResetSupportUrl: passwordResetSupportUrl,
                        linkTitle: gettext('Reset Your Password'),
                        linkHref: fieldsData.password.url,
                        helpMessage: StringUtils.interpolate(
                            gettext('عند اختيارك "إعادة ضبط كلمة المرور"، ستصل رسالة لبريدك الإلكتروني المسجّل لدى حساب {platform_name}. لتغيير كلمة المرور، افتح الرسالة من بريدك وانقر على الرابط الموجود فيها.'),  // eslint-disable-line max-len
                            {platform_name: platformName}
                        )
                    })
                });
            }

            // set TimeZoneField to listen to CountryField
            getUserField = function(list, search) {
                return _.find(list, function(field) {
                    return field.view.options.valueAttribute === search;
                }).view;
            };
            userFields = _.find(aboutSectionsData, function(section) {
                return section.title === gettext('Basic Account Information');
            }).fields;
            timeZoneDropdownField = getUserField(userFields, 'time_zone');
            countryDropdownField = getUserField(userFields, 'country');
            timeZoneDropdownField.listenToCountryView(countryDropdownField);

            accountsSectionData = [
                {
                    title: gettext('Linked Accounts'),
                    subtitle: StringUtils.interpolate(
                        gettext('You can link your social media accounts to simplify signing in to {platform_name}.'),
                        {platform_name: platformName}
                    ),
                    fields: _.map(authData.providers, function(provider) {
                        return {
                            view: new AccountSettingsFieldViews.AuthFieldView({
                                title: provider.name,
                                valueAttribute: 'auth-' + provider.id,
                                helpMessage: '',
                                connected: provider.connected,
                                connectUrl: provider.connect_url,
                                acceptsLogins: provider.accepts_logins,
                                disconnectUrl: provider.disconnect_url,
                                platformName: platformName
                            })
                        };
                    })
                }
            ];

            ordersHistoryData.unshift(
                {
                    title: gettext('ORDER NAME'),
                    order_date: gettext('ORDER PLACED'),
                    price: gettext('TOTAL'),
                    number: gettext('ORDER NUMBER')
                }
            );

            ordersSectionData = [
                {
                    title: gettext('My Orders'),
                    subtitle: StringUtils.interpolate(
                        gettext('This page contains information about orders that you have placed with {platform_name}.'),  // eslint-disable-line max-len
                        {platform_name: platformName}
                    ),
                    fields: _.map(ordersHistoryData, function(order) {
                        orderNumber = order.number;
                        if (orderNumber === 'ORDER NUMBER') {
                            orderNumber = 'orderId';
                        }
                        return {
                            view: new AccountSettingsFieldViews.OrderHistoryFieldView({
                                totalPrice: order.price,
                                orderId: order.number,
                                orderDate: order.order_date,
                                receiptUrl: order.receipt_url,
                                valueAttribute: 'order-' + orderNumber,
                                lines: order.lines
                            })
                        };
                    })
                }
            ];

            accountSettingsView = new AccountSettingsView({
                model: userAccountModel,
                accountUserId: accountUserId,
                el: accountSettingsElement,
                tabSections: {
                    aboutTabSections: aboutSectionsData,
                    accountsTabSections: accountsSectionData,
                    ordersTabSections: ordersSectionData
                },
                userPreferencesModel: userPreferencesModel
            });

            accountSettingsView.render();

            showAccountSettingsPage = function() {
                // Record that the account settings page was viewed.
                Logger.log('edx.user.settings.viewed', {
                    page: 'account',
                    visibility: null,
                    user_id: accountUserId
                });
            };

            showLoadingError = function() {
                accountSettingsView.showLoadingError();
            };

            userAccountModel.fetch({
                success: function() {
                    // Fetch the user preferences model
                    userPreferencesModel.fetch({
                        success: showAccountSettingsPage,
                        error: showLoadingError
                    });
                },
                error: showLoadingError
            });

            return {
                userAccountModel: userAccountModel,
                userPreferencesModel: userPreferencesModel,
                accountSettingsView: accountSettingsView
            };
        };
    });
}).call(this, define || RequireJS.define);
