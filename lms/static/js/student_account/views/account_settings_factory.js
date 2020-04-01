(function(define, undefined) {
    'use strict';
    define([
        'gettext', 'jquery', 'underscore', 'backbone', 'logger',
        'js/student_account/models/user_account_model',
        'js/student_account/models/user_preferences_model',
        'js/student_account/views/account_settings_fields',
        'js/student_account/views/account_settings_view',
        'edx-ui-toolkit/js/utils/string-utils',
        'js/student_profile/views/learner_profile_fields',

        'js/views/message_banner'
    ], function(gettext, $, _, Backbone, Logger, UserAccountModel, UserPreferencesModel,
                 AccountSettingsFieldViews, AccountSettingsView, StringUtils,
                 LearnerProfileFieldsView,  MessageBannerView) {
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
            socialPlatforms,
            accountSettingsData,
            profile_image_upload_url,
            profile_image_remove_url,
            profile_image_max_bytes,
            profile_image_min_bytes
        ) {
            var accountSettingsElement, userAccountModel, userPreferencesModel, aboutSectionsData,
                accountsSectionData, ordersSectionData, accountSettingsView, showAccountSettingsPage,
                showLoadingError, orderNumber, getUserField, userFields, timeZoneDropdownField, countryDropdownField,
                emailFieldView, platformData, socialFields, mobytizeFields;

            accountSettingsElement = $('.wrapper-account-settings');
            userAccountModel = new UserAccountModel(
                _.extend(
                    accountSettingsData
                ),
                {parse: true}
            );
            userAccountModel.url = userAccountsApiUrl;

            userPreferencesModel = new UserPreferencesModel();
            userPreferencesModel.url = userPreferencesApiUrl;

            if (allowEmailChange) {
                emailFieldView = {
                    view: new AccountSettingsFieldViews.EmailFieldView({
                        model: userAccountModel,
                        title: gettext('Email Address'),
                        valueAttribute: 'email',
                        helpMessage: StringUtils.interpolate(
                            gettext('The email address you use to sign in. Communications from {platform_name} and your courses are sent to this address.'),  // eslint-disable-line max-len
                            {platform_name: platformName}
                        ),
                        persistChanges: true
                    })
                };
            } else {
                emailFieldView = {
                    view: new AccountSettingsFieldViews.ReadonlyFieldView({
                        model: userAccountModel,
                        title: gettext('Email Address'),
                        valueAttribute: 'email',
                        helpMessage: StringUtils.interpolate(
                            gettext('The email address you use to sign in. Communications from {platform_name} and your courses are sent to this address.  To change the email address, please contact {contact_email}.'),  // eslint-disable-line max-len
                            {platform_name: platformName, contact_email: contactEmail}
                        )
                    })
                };
            }
            var tabSections = {};
            aboutSectionsData = [
                {
                    title: gettext('Basic Account Information'),
                    subtitle: gettext('These settings include basic information about your account. You can also specify additional information and see your linked social accounts on this page.'),  // eslint-disable-line max-len
                    fields: [
                        {
                            view: new AccountSettingsFieldViews.ReadonlyFieldView({
                                model: userAccountModel,
                                title: gettext('Username'),
                                valueAttribute: 'username',
                                helpMessage: StringUtils.interpolate(
                                    gettext('The name that identifies you throughout {platform_name}. You cannot change your username.'),  // eslint-disable-line max-len
                                    {platform_name: platformName}
                                )
                            })
                        },
                        {
                            view: new AccountSettingsFieldViews.TextFieldView({
                                model: userAccountModel,
                                title: gettext('Full Name'),
                                valueAttribute: 'name',
                                helpMessage: gettext(
                                    'The name that is used for ID verification and appears on your certificates. Other learners never see your full name. Make sure to enter your name exactly as it appears on your government-issued photo ID, including any non-Roman characters.'  // eslint-disable-line max-len
                                ),
                                persistChanges: true
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
                                    gettext('The language used throughout this site. This site is currently available in a limited number of languages.'),  // eslint-disable-line max-len
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
                                title: gettext('Country or Region'),
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

            // Add the social link fields
            socialFields = {
                title: gettext('Social Media Links'),
                fields: []
            };

            for (var socialPlatform in socialPlatforms) {
                platformData = socialPlatforms[socialPlatform];
                socialFields.fields.push(
                    {
                        view: new AccountSettingsFieldViews.SocialLinkTextFieldView({
                            model: userAccountModel,
                            title: gettext(platformData[1]),
                            valueAttribute: 'social_links',
                            helpMessage: gettext(
                                'Enter your ') + platformData[1] + gettext(' username or the URL to your ') +
                                platformData[1] + gettext(' page. Delete the URL to remove the link.')
                            ,
                            platform: platformData[0],
                            persistChanges: true
                        })
                    }
                );
            }



            aboutSectionsData.push(socialFields);
            // Add the mobytize_id and mobytizetoken fields
            mobytizeFields = {
                title: gettext('Mobytize data'),
                fields: [   {
                    view: new AccountSettingsFieldViews.TextFieldView({
                        model: userAccountModel,
                        title: gettext('mobytize_id'),
                        valueAttribute: 'mobytize_id',
                        helpMessage: gettext(
                            'mobytize_id'  // eslint-disable-line max-len
                        ),
                        persistChanges: true
                    })
                },
                {
                    view: new AccountSettingsFieldViews.TextFieldView({
                        model: userAccountModel,
                        title: gettext('mobytize_token'),
                        valueAttribute: 'mobytize_token',
                        helpMessage: gettext(
                            'mobytize_token'  // eslint-disable-line max-len
                        ),
                        persistChanges: true
                    })
                }]
            };
            aboutSectionsData.push(mobytizeFields);
            tabSections['aboutTabSections'] = aboutSectionsData;

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

            if(authData.providers != undefined){
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
                tabSections['accountsTabSections'] = accountsSectionData;
            }
            if(ordersHistoryData.length > 0){
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
                tabSections['ordersTabSections'] = ordersSectionData;
            }

            var messageView = new MessageBannerView({
                el: $('.message-banner')
            });
            var profileImageFieldView = new LearnerProfileFieldsView.ProfileImageFieldView({
                model: userAccountModel,
                valueAttribute: 'profile_image',
                editable: true,
                messageView: messageView,
                imageMaxBytes: profile_image_max_bytes,
                imageMinBytes: profile_image_min_bytes,
                imageUploadUrl: profile_image_upload_url,
                imageRemoveUrl: profile_image_remove_url
            });
            var passwordFieldView = new AccountSettingsFieldViews.PasswordFieldView({
                model: userAccountModel,
                title: gettext('Reset Your Password'),
                screenReaderTitle: gettext('Reset Your Password'),
                valueAttribute: 'password',
                emailAttribute: 'email',
                passwordResetSupportUrl: passwordResetSupportUrl,
                linkTitle: gettext('Reset Your Password'),
                linkHref: fieldsData.password.url,
                helpMessage: StringUtils.interpolate(
                    gettext('When you select "Reset Your Password", a message will be sent to the email address for your {platform_name} account. Click the link in the message to reset your password.'),  // eslint-disable-line max-len
                    {platform_name: platformName}
                )
            })

            accountSettingsView = new AccountSettingsView({
                model: userAccountModel,
                accountUserId: accountUserId,
                el: accountSettingsElement,
                tabSections: tabSections,
                userPreferencesModel: userPreferencesModel,
                profileImageFieldView: profileImageFieldView,
                passwordFieldView: passwordFieldView
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
