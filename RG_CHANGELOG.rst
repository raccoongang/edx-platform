RG Changelog
############

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_, and this project adheres to customized Semantic Versioning e.g.: `nutmeg-rg.1`

[Unreleased]
************

Added
=====

* Palm version of the course search behaviour changes `RGOeX-25871 https://youtrack.raccoongang.com/issue/RGOeX-25871`_.
Excluded courses with the "about" or "none" visibility from the course discovery search results.

[olive-rg.1] 2023-03-30 (Olive RG release)
******************************************

Fixes
=====

* Certificate exception message visibility fix `RGOeX-25142 https://youtrack.raccoongang.com/issue/RGOeX-25142`_

  * This commit should be skipped when we start the sync process with the Quince branch if the `master PR <https://github.com/openedx/edx-platform/pull/31668>`_ will be merged by then

* Fix for the course overview editing field in the Studio
* Course search used wrong import, so search results were empty on the Discover New page.
  Fixed import, removed duplicated exclude_dictionary values

[nutmeg-rg.1] 2022-09-30 (Nutmeg RG release)
********************************************

Changed
=======

* RG-LMS gitlab MR template renamed to the Default template, some minor
  changes to the template were also added.

* Remove RG-specific settings that were moved to deployment `RGOeX-1713 <https://youtrack.raccoongang.com/issue/RGOeX-1713>`_

  * This reverts changes from the `RGOeX-687 <https://youtrack.raccoongang.com/issue/RGOeX-687>`_

Added
=====

* Add modified favicon redirect view to be able to use the themed version `RGOeX-771 <https://youtrack.raccoongang.com/issue/RGOeX-771>`_ `RGOeX-1564 <https://youtrack.raccoongang.com/issue/RGOeX-1564>`_

  * This requires modifications in nginx configurations because favicon url was redifined there for some reason

* Add ability to notify Credentials about received honor course certificate `RGOeX-1413 <https://youtrack.raccoongang.com/issue/RGOeX-1413>`_

  * Added the new WaffleFlag `course_modes.extend_certificate_relevant_modes_with_honor`
  * The new WaffleFlag is disabled by default
  * Use case for enabling the WaffleFlag - usage of programs that include honor courses

Fixes
=====

* Fix error for the CMS logistration `RGOeX-1597 <https://youtrack.raccoongang.com/issue/RGOeX-1597>`_

* Fix empty signature added after every certificate saving `RGOeX-1659 <https://youtrack.raccoongang.com/issue/RGOeX-1659>`_


[Maple Release] - 2022-04-29
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[Fix] - 2022-02-23
~~~~~~~~~~~~~~~~~~
* Activation email and Email Change email theming fix

  * pass the right site to the email context
  * https://youtrack.raccoongang.com/issue/RGOeX-933

[Feature] - 2022-02-15
~~~~~~~~~~~~~~~~~~
* Add default xblock to the requirements

  * https://youtrack.raccoongang.com/issue/RGOeX-935

[Fix] - 2022-02-15
~~~~~~~~~~~~~~~~~~
* Fix text mistakes on the cookie policy page

[Feature] - 2022-02-09
~~~~~~~~~~~~~~~~~~~~~~
* Add microsites support for the `enable_programs` command

  * fixed overriding for `ProgramsApiConfig` marketing path
  * `ProgramsApiConfig` doesn’t have the marketing path by default
  * removed the `--site-domain` arg, updating site configurations for all sites instead

[Fix] - 2022-02-02
~~~~~~~~~~~~~~~~~~
* Add settings needed for the Studio SSO logins

  * Details: https://youtrack.raccoongang.com/issue/RGOeX-687

[Fix] - 2022-01-28
~~~~~~~~~~~~~~~~~~
* Avoid django loaders template caching
* Account activation email site logo theming fix
  * Details: https://youtrack.raccoongang.com/issue/RGOeX-411
* Keep localize course dates after user logout
  * Details: https://youtrack.raccoongang.com/issue/RGOeX-609
  * Upstream MR to master https://github.com/openedx/edx-platform/pull/29772
  * Upstream MR to open-release/maple.master https://github.com/openedx/edx-platform/pull/29773

[Fix] - 2022-01-26
~~~~~~~~~~~~~~~~~~
* fix incorrect symbols on wiki create article page
* more info: https://youtrack.raccoongang.com/issue/RGOeX-662

[Feature] - 2022-01-26
~~~~~~~~~~~~~~~~~~~~~~
* cookies policy banner and static page /cookies.html
* more info: https://youtrack.raccoongang.com/issue/RGOeX-391

[Lilac Release] - 2021-06-17
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

[Fix] 2021-09-10
~~~~~~~~~~~~~~~~
* course discovery search error on devstack related to incorrect elasticsearch host in settings
* course discovery search error related to visibility filters
  * fixes 6d9f9352
* course discovery search sidebar filters
  * relates to update to elasticsearch7
  * bug cause: now elasticsearch returns `aggs` in the search results instead of `facets`

[Koa Release]
~~~~~~~~~~~~~

[Fix] 2021-06-15
~~~~~~~~~~~~~~~~
* pass required context to bulk enrollment emails

  * logo_url
  * homepage_url
  * dashboard_url

* add additional context for enrollment emails

  * contact_email
  * platform_name

[Feature] 2021-05-20
~~~~~~~~~~~~~~~~
‘enable_programs’ command is added.

[Fix] 2021-04-26
~~~~~~~~~~~~~~~~
‘Linked accounts’ tab is hidden if there are no SSO provider are installed

[Documentation|Enhancement] - 2021-02-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* RG_CHANGELOG is added!
* gitlab base RG-LMS MergeRequest template is added.

* For the upcoming logs please use the following tags:
   * Feature
   * Enhancement
   * Fix
   * Documentation
