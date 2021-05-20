[Unreleased]
~~~~~~~~~~~~

[Feature] - 2022-02-09
~~~~~~~~~~~~~~~~~~~~~~
* Add microsites support for the `enable_programs` command

  * fixed overriding for `ProgramsApiConfig` marketing path
  * `ProgramsApiConfig` doesn’t have the marketing path by default
  * removed the `--site-domain` arg, updating site configurations for all sites instead

[Fix] - 2022-01-28
* Avoid django loaders template caching
* Account activation email site logo theming fix
* Details: https://youtrack.raccoongang.com/issue/RGOeX-411

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

[Documentation|Enhancement] - 2021-02-24
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
* RG_CHANGELOG is added!
* gitlab base RG-LMS MergeRequest template is added.

* For the upcoming logs please use the following tags:
   * Feature
   * Enhancement
   * Fix
   * Documentation
