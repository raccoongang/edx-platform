offline_view for xblock-poll
============================

A proposal for how ``offline_view`` should work, using the survey in ``xblock-poll`` as the worked example. It
supports `ADR-003`_. Method and handler names below are placeholders.

Why offline_view should be the basis for other views
----------------------------------------------------

If ``offline_view`` is a separate rendering with its own JavaScript, every block that supports it has two
frontends to maintain, and they will drift. The alternative is to make ``offline_view`` the one rendering of a
block's content, and build ``public_view`` and ``student_view`` on top of it.

Mechanically, that means splitting a block's page into three parts:

1. **Content.** A fragment rendered from content and settings fields only. No user, no request, no clock, no
   handler URLs. This is ``offline_view``. It is the same for everyone, so it can be rendered once at publish
   time and cached or archived.
2. **State.** The learner's data, served as JSON by a handler. The block's JavaScript fetches it after load and
   applies it to the page (check the radios, disable Submit, show the count).
3. **Interactions.** Calls to the block's handlers, made through the ``runtime`` object the JavaScript is
   given, never through ``$.ajax`` or a mobile-specific global.

The block's JavaScript is then identical everywhere. What differs is the runtime behind it:

.. list-table::
   :header-rows: 1

   * - Where
     - Fetching state
     - Calling a handler
   * - LMS, enrolled learner
     - JSON from the server
     - HTTP request, real response
   * - LMS, anonymous
     - empty
     - refused, with a sign-in prompt
   * - Mobile archive, offline
     - the copy the application downloaded, plus calls not yet synced
     - queued by the application, "pending" response

``student_view`` becomes ``offline_view`` plus anything staff-only. ``public_view`` can return
``offline_view`` if the block's author decides the content is fit for non-enrolled visitors. That is a
per-block choice, not an automatic fallback.

The mobile "JS bridge" is an internal detail of the archive runtime. Blocks never see it.

Runtime changes
---------------

Backend
~~~~~~~

* **Render with no user.** The generator renders ``offline_view`` through a runtime with no request and no
  user. Reading a user-scoped field during that render should raise, not return a default, so that a view which
  depends on user state fails at generation time and not silently.
* **No handler URLs in the fragment.** ``handler_url`` should also raise during an ``offline_view`` render. The
  JavaScript refers to handlers by name, and the runtime resolves them.
* **Declining.** A block that cannot render without a user for its current settings raises
  ``xblock.exceptions.ViewDeclined``, and the generator records the block as unsupported with the reason.
* **Resources.** The packager resolves ``runtime.local_resource_url(...)`` resources from the block's package,
  as the LMS resource view does. Blocks should not need a different resource list for ``offline_view`` than for
  their other views.
* **State handler convention.** One agreed handler name through which a block returns its user state as JSON.
  Runtimes may call it on the block's behalf, for example when the application downloads state for a whole
  course.
* **Replay.** Queued calls from a device are replayed through the normal handler dispatch, as the learner, in
  order. The device stores a record of each call (usage key, handler name and suffix, JSON body, archive
  version, sequence, id), not URLs, and keeps the result of each replay for the block (ADR-003, decision 7).

Frontend
~~~~~~~~

Two additions to the JavaScript runtime object, implemented by the LMS runtime, the Studio preview runtime, the
iframe runtime in ``openedx.core.djangoapps.xblock``, and the new archive runtime; a third,
``runtime.handlerMode(element)``, is defined in `Read-only offline_view for problem`_ and the survey needs it too:

.. code-block:: js

    runtime.loadState(element)
    // -> Promise<{state: {...} | null,              // null: no copy of the state (unknown, not empty)
    //             pending: [{handler, data}, ...],  // calls stored and not yet replayed
    //             results: [{handler, data, status, response}, ...]}>  // what the last replay answered

    runtime.callHandler(element, handlerName, data, suffix)  // data is sent as JSON; suffix is optional
    // -> Promise<{status: "ok", response: {...}}
    //          | {status: "pending"}        // queued, no server answer yet
    //          | {status: "unavailable"}>   // e.g. anonymous

Online runtimes implement these as plain HTTP calls and always return empty ``pending`` and ``results`` lists.
The archive runtime answers ``loadState`` from the downloaded copy, and turns ``callHandler`` into a bridge
message for the application to store.

``handlerUrl`` stays for existing blocks. Blocks that want to run on older platforms can fall back to
``$.ajax(runtime.handlerUrl(...))`` when ``callHandler`` is missing.

Implementing it in xblock-poll
------------------------------

The survey is close already: its JavaScript uses ``runtime.handlerUrl`` for every call, it fetches
``student_voted`` on load before deciding what to show, and results are rendered client-side from JSON.

Python (``poll/poll.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Add ``SurveyBlock.offline_view``. It renders ``survey.html`` with a context built only from content and
   settings: questions, answers, feedback, ``max_submissions``, ``private_results``, block name and ids. The
   user-dependent context values go away: ``choices``, ``can_vote``, ``submissions_count``,
   ``can_view_private_results``.
2. Remove the matching user-dependent markup from ``survey.html``: the ``checked`` attribute, the
   ``data-can-vote`` attribute, and the conditions on the thanks message and feedback container. Those start
   in their "has not voted" form.
3. Add the state handler, returning ``choices``, ``submissions_count``, ``can_vote`` and whether the user may
   view private results. The existing ``student_view_user_state`` handler is the starting point, but it returns
   the full tally even when results are private, which should not go to a device.
4. Make ``student_view`` return ``offline_view`` plus the staff-only results and export buttons. Make
   ``public_view`` return ``offline_view``.

JavaScript (``poll/public/js/poll.js``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. On init, replace the ``student_voted`` call with ``runtime.loadState(element)``. Apply ``state``, then apply
   each entry in ``pending`` the same way a fresh vote is applied.
2. Move the logic that currently reads ``data-can-vote`` and the server-rendered ``checked`` radios into one
   ``applyState(state)`` function.
3. Replace each ``$.ajax({url: runtime.handlerUrl(...)})`` with ``runtime.callHandler(...)``.
4. Handle the three results of a vote:

   * ``ok``: as today.
   * ``pending``: show the thanks message, increment the count locally, disable inputs if the limit is reached,
     and say that results will be available online.
   * ``unavailable``: prompt to sign in.

5. ``get_results`` and the CSV export need the server. The script asks ``runtime.handlerMode(element)`` first
   and, when handlers are not live, shows a short message and makes no call. Otherwise a voter with public
   results stores one ``get_results`` record on every offline open, and each replay publishes a
   ``view_results`` event.
6. Show what a replay did not accept. A vote replayed after the limit was reached, or after the questions
   changed, is refused by the handler with ``success: false`` in a successful response. On load, the script
   reads ``results`` from ``loadState`` and tells the learner which answer was not accepted.

The poll block shares ``PollUtil`` and the script with the survey, but it has its own view, its own state
handler and its own initialisation in the script. It gets the same four Python steps and the same script
changes. The applications must also know its block type: Android has none for it today.

What this leaves open
---------------------

* How much of this applies to the problem block, whose JavaScript ignores the runtime and whose server
  re-renders HTML on every interaction. `Read-only offline_view for problem`_ covers its first step.

.. _ADR-003: ../003-offline-content-generation-architecture.rst
.. _Read-only offline_view for problem: read-only-offline-view-for-problem.rst
