Read-only offline_view for problem
==================================

A proposal for the read-only ``offline_view`` of the problem block in this scope ("Phase 2"), built so that the
next scope ("Phase 3", interactive offline problems) extends it and does not replace it. It supports `ADR-003`_
and assumes the runtime changes in `offline_view for xblock-poll`_. Names are placeholders.

Why read-only should not be a separate rendering
------------------------------------------------

The quick way to get a read-only problem is a second template with the inputs disabled and no buttons. That
leaves three renderings of a problem (online, read-only, and later interactive offline), and the read-only one
is discarded in Phase 3.

The alternative: ``offline_view`` uses the same templates and the same JavaScript as ``student_view``, rendered
for a learner with no state. Read-only is then something the JavaScript does when the runtime tells it handlers
cannot be called. Mechanically:

1. **Content.** The problem rendered from its XML and settings with empty state and a fixed seed. The markup is
   what a learner sees on first visit, including the Submit button.
2. **State.** None in Phase 2. The page never shows attempts, saved answers or correctness.
3. **Interactions.** None in Phase 2. The JavaScript asks the runtime whether handlers are available. If not,
   it disables the inputs and buttons and shows a note that answers are accepted online.

Phase 3 changes step 3 only: the JavaScript learns to queue a submission and show it as pending. The content
render and the archive format stay as they are.

Runtime changes
---------------

Beyond what the survey needs:

Backend
~~~~~~~

* **A user-less sandbox.** Python-scripted problems run their script when the problem is built, so the
  generating runtime must provide the sandbox service on the CMS workers. Everything else the render needs
  (i18n, URL replacement, the cache) is already user-independent.
* **The packager reads** ``data-content``. ``problem_ajax.html`` carries the problem's body as the value of that
  attribute, where a pass over the page's elements does not see it. The packager parses the attribute and
  collects and rewrites the assets and links inside it, and collects the script a formula input asks the page to
  load (ADR-003, decision 4).
* **Nothing else.** The rules from the survey proposal apply as written: reading a user-scoped field or calling
  ``handler_url`` during an ``offline_view`` render raises.

Frontend
~~~~~~~~

* **A way to ask what handlers can do, before the learner types anything.** For example
  ``runtime.handlerMode(element)``, returning ``"live"``, ``"queued"`` or ``"none"``. The LMS and Studio
  runtimes return ``"live"``. The archive runtime returns ``"queued"``. An anonymous runtime returns
  ``"none"``.
* **The LMS page globals the problem script uses.** The block's bundle contains its own loader, collapsible and
  input scripts and ``edx.HtmlUtils``, and expects the rest from the page: ``jQuery``, ``_``, ``gettext``,
  ``ngettext``, ``edx.StringUtils``, ``$.postWithPrefix``, ``Logger`` and ``MathJax``. Of these ``ngettext``,
  ``edx.StringUtils`` and ``_`` are needed before the first paint completes: an error at the progress line stops
  the rest of it. On interaction the script also uses ``globalTooltipManager`` and, once problems can be
  submitted, ``SR`` and ``$.ajaxWithPrefix``. The archive page has to supply them. This list should be written
  down in these two parts, taken from the built bundle, and tested with every supported input type, because it
  will otherwise drift.

Implementing it in the problem block
------------------------------------

Python (``xblock_problem/block.py``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Add a user-less problem constructor.** Today the ``lcp`` property reads the user service and writes
   ``seed`` and ``score`` into user state while rendering. Add a separate method that builds a
   ``LoncapaProblem`` with ``state={}``, ``seed=1``, no anonymous id, no xqueue and no handler URL.
   ``max_score`` builds one with the same arguments but cannot be the model: it uses ``minimal_init`` and no
   template renderer, so its problem can count points and cannot be rendered. The method starts from
   ``new_lcp``: it keeps the sandbox, the cache, the template renderer and i18n, and drops the user service
   lookups, the queue and the handler URL.
2. **Parameterise the render.** ``get_html`` and ``get_problem_html`` read ``self.lcp`` and user fields
   directly and through eleven helpers (the progress, the three button checks, ``closed``, ``is_submitted``,
   ``is_correct`` and the like). Change them to take a small state object as an argument: it passes through
   thirteen methods, fourteen with the submit notification, and holds four values, the problem, ``attempts``,
   ``has_saved_answers`` and ``score``. ``student_view`` passes nothing and reads the learner as today;
   ``offline_view`` passes the user-less problem and an empty state. Both go through ``problem_ajax.html``,
   ``problem.html`` and the input templates unchanged. Three things on this path are not learner state. Whether
   the viewer is staff comes from the runtime, which has no user when it generates. The clock decides Submit and
   Show Answer at publish time, which is harmless while the page is read-only. And the error path rewrites the
   learner's state: with a state object given it raises, so that generation records a failure.
3. **Add** ``offline_view``. It declines, before rendering, when:

   * ``rerandomize`` is anything but "never";
   * the problem's script reads the learner's identity (``anonymous_student_id``): such a problem differs per
     learner while its randomization is "never";
   * a response type is outside the supported set. The six already marked ``multi_device_support`` (choice,
     multiple choice, option, numerical, string, formula) are the starting list;
   * an input type needs the server to display or to respond to typing (MATLAB, JS input, chemical equation,
     code graded through xqueue). Formula input is a judgement call: it works without its live preview, and its
     previewer script is a platform file that the packager collects.

4. **Omit the handler URL.** ``problem_ajax.html`` writes it into ``data-url``. In ``offline_view`` the
   attribute is absent.

``student_view`` keeps its current behaviour exactly: same markup, same single request. Existing usages are
unaffected.

JavaScript (``assets/static/js/display.js``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Use the** ``runtime`` **argument.** The constructor currently ignores it. Read
   ``runtime.handlerMode(element)`` once, defaulting to ``"live"`` when the method is missing so the block
   still works on older platforms.
2. **Add a read-only mode.** When the mode is not ``"live"``, after the normal render and input setup: disable
   every input and action button, skip the bindings that call the server, and show the "answers are accepted
   online" note. The first paint already comes from the ``data-content`` attribute and makes no request.
3. **Leave the live path alone.** The existing ``$.postWithPrefix`` calls stay for Phase 2. Moving them to
   ``runtime.callHandler`` is Phase 3 work.
4. **Give the script loader an** ``onerror``. Input setup, the bindings and the read-only step run in the
   loader's callback, and only ``onload`` completes a script the markup asks for. A script that fails to load
   would leave the problem without its inputs set up, not disabled and without the note.

The Phase 2 script treats ``"queued"`` the same as ``"none"``, because it cannot yet show a pending submission.
Archives built in Phase 2 therefore stay read-only until they are regenerated with the Phase 3 script.

What this leaves for Phase 3
----------------------------

* **Pending submissions.** Restoring a queued answer into each supported input type on reload, and showing
  "submitted, not yet graded" in place of correctness.
* ``student_view`` **literally on top of** ``offline_view``. The ``problem_get`` handler already returns the
  state-rendered HTML and the script already knows how to swap it in. That is the route to serving the cached
  fragment online and hydrating it, at the cost of one request on load.
* **Buttons that depend on time or attempts.** Show Answer, Reset, and the Submit cutoff after the due date
  cannot be decided at publish time. The archive needs either state from the application or a rule that the
  server's answer on replay is final.
* **Moving server calls to the runtime.** Capa uses one handler with a dispatch suffix
  (``xmodule_handler/problem_check``) that reads form fields. The record of ADR-003, decision 7, carries a
  suffix and a JSON body, so capa needs that handler to accept JSON, or named JSON handlers.

.. _ADR-003: ../003-offline-content-generation-architecture.rst
.. _offline_view for xblock-poll: offline-view-for-xblock-poll.rst
