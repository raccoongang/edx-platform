
Transfer certificate signatures from Mongo to Credentials
#########################################################

Status
******
Proposed

Context
*******
As a part of `Old Mongo Deprecation work <https://github.com/openedx/public-engineering/issues/62>`_
we are planning to remove the support for c4x assets. After removing support for c4x assets in
StaticContentServer middleware, the certificate signatories for courses with deprecated IDs won't
be available because those signatures are stored in course assets.


Decision
********
To keep access to the certificate signatures will be used external signatures from credentials on WEB/PDF
certificate rendering.

* credentials API must be extended to provide endpoints for adding and retrieving signatures

  * `CourseCertificateViewSet` API should provide a possibility to optionaly update or create signatures for the course certificate.

* add a new `OpenEdxPublicSignal` that is emitted from Studio whenever certificate-related data is changed (e.g. certificate image upload, course import). The signature image can be exposed as a URL.

  1. create UserCredential
  2. transfer certificate
  3. upload signature img and transfer signature data

* added management command to copy signatures from Mongo to Credentials
* update certificate views for getting signatures from Credentials
* signal receiver will copy the signature image to Credentials Signature model

Mongo certificate structure:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.. code-block:: json

  {
    "certificates": {
      "certificates": [
        {
          "id": 853888039,
          "name": "Name of the certificate",
          "description": "Description of the certificate",
          "is_active": true,
          "version": 1,
          "signatories": [
            {
              "name": "Name",
              "title": "Title",
              "organization": "Organization",
              "signature_image_path": "/c4x/ooniversity/DJ101/asset/png-transparent-circle-white-circle-white-monochrome-black-thumbnail.png",
              "certificate": 853888039,
              "id": 1300534915
            }
          ],
          "course_title": "cert"
        }
      ]
    }
  }


Credentials CourseCertificate model:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
CourseCertificate fields:

* site
* is_active
* signatories

  * Signatory fields:

    * name
    * title
    * organization_name_override
    * image

* title
* course_id
* course_run
* certificate_available_date
* certificate_type
* user_credentials


Consequences
************
* After updating course or course certificate - signatures for that course will be saved in CourseCertificate from credentials.


Alternatives Considered
***********************
No alternatives were considered.


References
***************
- `Migrate signature assets from MongoDB GridFS to the Credentials IDA <https://github.com/openedx/credentials/issues/1765>`_
- `[DEPR]: DraftModuleStore (Old Mongo Modulestore) <https://github.com/openedx/public-engineering/issues/62>`_
- `Remove the ability to read and write static assets to Old Mongo <https://github.com/openedx/public-engineering/issues/77>`_

