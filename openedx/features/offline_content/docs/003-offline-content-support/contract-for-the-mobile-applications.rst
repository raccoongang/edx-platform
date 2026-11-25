The contract for the mobile applications
========================================

What the mobile applications implement for `ADR-003`_: how they download archives, the bridge between an
archive's page and the application, the record of a stored handler call, the learner's state, and the replay.
It gathers decisions 5, 6 and 7 for the application teams and assumes the runtime interface in `offline_view for
xblock-poll`_. Message, field and endpoint names are placeholders until they are implemented.

Downloading
-----------

* **What changed.** ``GET /api/mobile/v1/download_courses/{username}`` returns, for each course, ``total_size``
  and a version of the course's offline content, an opaque string. The application requests the blocks
  (``/api/mobile/v4/course_info/blocks/``) of a course only when that version differs from the one it stored.
  There, ``offline_download {file_url, last_modified, file_size}`` of a block says which archives to fetch: an
  archive is current while ``last_modified`` equals the stored value. Both values are compared as strings and
  never parsed.
* **How to fetch.** ``file_url`` is an LMS URL and needs the credentials the application sends with its API
  calls. The answer is the file, or a redirect to a storage URL that is valid for a few minutes and needs no
  credentials. The application follows the redirect at once, does not send its token to that host, and does not
  keep the storage URL.
* **Refusals.** The endpoint checks, at the time of the download, that the learner may open the block. A refusal
  means the block is not available to this learner now.

Application versions already released download with a client that sends no credentials, so they cannot fetch
these archives.

The bridge
----------

The page's end of the bridge is the archive runtime. Blocks never use the bridge.

* **Page to application.** ``window.AndroidBridge.postMessage(json)`` on Android,
  ``window.webkit.messageHandlers.IOSBridge.postMessage(json)`` on iOS; ``json`` is one JSON object as a string.
* **Application to page.** One call of ``window.OfflineRuntime.receive(json)`` per message received. The
  application passes ``json`` as a string argument produced by a JSON encoder. It never pastes data into script
  text: a quote character in the data would end the string.
* **Every message is answered.** A message has a ``type`` and a ``request_id``, and the application answers it
  once, with the same ``request_id``. A message whose ``type`` the application does not know is answered with
  ``{"request_id": ..., "error": "unknown_message"}``, never ignored and never an exception. The runtime then
  reports that handlers are unavailable, and the block is read-only. It does the same when no answer arrives.

.. list-table::
   :header-rows: 1

   * - Message
     - The page sends
     - The application answers
   * - ``load_state``
     - ``usage_key``
     - ``state``, ``pending``, ``results`` (see below)
   * - ``call_handler``
     - ``usage_key``, ``handler``, ``suffix``, ``body``
     - ``stored: true`` once the record is saved

The record
----------

A handler call made offline is stored as one record. Several records of one block are kept, in order; a new one
never replaces an earlier one.

.. list-table::
   :header-rows: 1

   * - Field
     - Who sets it
     - What it is
   * - ``id``
     - the application
     - a UUID, created when the record is stored; the replay endpoint remembers it
   * - ``sequence``
     - the application
     - a number that grows with every record stored for the learner on this device
   * - ``usage_key``
     - the page
     - the block
   * - ``handler``, ``suffix``
     - the page
     - the handler's name and its suffix, which is usually empty
   * - ``body``
     - the page
     - the call's data as JSON text, kept exactly as received
   * - ``archive_version``
     - the application
     - ``last_modified`` of the archive the page was opened from

The page cannot number its calls, because it starts again every time it is opened. No URL and none of the
learner's headers are part of a record.

State
-----

A block marked in the blocks response as having state returns the learner's state as JSON from its state
handler, which the application calls as the learner on the LMS's XBlock handler route
(``/courses/{course_id}/xblock/{usage_key}/handler/{state handler}``).

* **When.** When the block's archive is downloaded, and after a replay, whose answer carries the fresh state.
* **What to keep.** The JSON as received, per learner and block.
* **Unknown is not empty.** ``load_state`` is answered with ``state: null`` when the application holds no copy
  for the block, and with the stored object otherwise. The application never makes up an empty state: the block
  shows a learner whose state is unknown differently from one who has not answered.

``load_state`` is answered with three values:

* ``state``: as above;
* ``pending``: the records of the block not yet replayed, oldest first, each as ``{handler, suffix, data}`` with
  ``data`` the parsed ``body``;
* ``results``: what the last replay of the block answered, each as ``{handler, suffix, data, status,
  response}``.

Replay
------

When the device is online the application sends its records, oldest first, to the batch replay endpoint, with
the learner's credentials.

* **Request.** ``{"records": [...]}``, each record with the fields above.
* **Answer.** ``{"results": [...]}``, one per record: ``id``, ``status`` (the HTTP status the block's handler
  answered with), ``response`` (the handler's JSON) and ``state`` (the block's state after the call).
* **A record that has a result is done,** whatever the status and whatever the response says. The application
  removes it from the queue, keeps its result for the block's next ``load_state`` and stores the state.
* **A request that fails is sent again** later with the same records and the same ids. The endpoint remembers the
  ids, so no call runs twice.
* **The application does not judge a result.** A block may refuse a call inside a successful response, in its
  own shape. The block's script reads ``results`` and tells the learner.

What goes away
--------------

The ``markProblemCompleted`` global, the ``{url, type, data}`` message, one stored submission per block, and the
replay of every stored submission to the problem's ``problem_check``.

.. _ADR-003: ../003-offline-content-generation-architecture.rst
.. _offline_view for xblock-poll: offline-view-for-xblock-poll.rst
