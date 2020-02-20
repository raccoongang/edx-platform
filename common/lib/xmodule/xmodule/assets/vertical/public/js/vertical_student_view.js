/* JavaScript for Vertical Student View. */

// The horizontal marks blocks complete if they are completable by viewing or answer.
window.VerticalStudentView = function(runtime, element) {
    'use strict';
    RequireJS.require(['js/bookmarks/views/bookmark_button'], function(BookmarkButton) {
        var $element = $(element);
        var $bookmarkButtonElement = $element.find('.bookmark-button');
        markBlocksCompletedOnViewIfNeeded(runtime, element);
        return new BookmarkButton({
            el: $bookmarkButtonElement,
            bookmarkId: $bookmarkButtonElement.data('bookmarkId'),
            usageId: $element.data('usageId'),
            bookmarked: $element.parent('#seq_content').data('bookmarked'),
            apiUrl: $('.courseware-bookmarks-button').data('bookmarksApiUrl')
        });
    });
};


const completedBlocksKeys = new Set();

function markBlocksCompletedOnViewIfNeeded(runtime, containerElement) {
  const blockElements = $(containerElement).find(
    '.xblock-student_view[data-mark-completed-on-view-after-delay]',
  ).get();
  if (blockElements.length > 0) {
    const tracker = new ViewedEventTracker();

    blockElements.forEach((blockElement) => {
      const markCompletedOnViewAfterDelay = parseInt(
        blockElement.dataset.markCompletedOnViewAfterDelay, 10,
      );
      if (markCompletedOnViewAfterDelay >= 0) {
        tracker.addElement(blockElement, markCompletedOnViewAfterDelay);
      }
    });

    tracker.addHandler((blockElement, event) => {
      const blockKey = blockElement.dataset.usageId;
      if (blockKey && !completedBlocksKeys.has(blockKey)) {
        if (event.elementHasBeenViewed) {

          $.ajax({
            type: 'POST',
            url: runtime.handlerUrl(blockElement, 'publish_completion'),
            data: JSON.stringify({
              completion: 1.0,
            }),
          }).then(
            () => {
              completedBlocksKeys.add(blockKey);
              blockElement.dataset.markCompletedOnViewAfterDelay = 0;
            },
          );
        }
      }
    });
  }
}

/** Ensure that a function is only run once every `wait` milliseconds */
function throttle(fn, wait) {
  let time = 0;
  function delay() {
    // Do not call the function until at least `wait` seconds after the
    // last time the function was called.
    const now = Date.now();
    if (time + wait < now) {
      time = now;
      fn();
    }
  }
  return delay;
}


class ElementViewing {
  /**
   * A wrapper for an HTMLElement that tracks whether the element has been
   * viewed or not.
   */
  constructor(el, viewedAfterMs, callback) {
    this.el = el;
    this.viewedAfterMs = viewedAfterMs;
    this.callback = callback;

    this.topSeen = false;
    this.bottomSeen = false;
    this.seenForMs = 0;
    this.becameVisibleAt = undefined;
    this.hasBeenViewed = false;
  }

  getBoundingRect() {
    return this.el.getBoundingClientRect();
  }

  /** This element has become visible on screen.
   *
   * (may be called even when already on screen though)
   */
  handleVisible() {
    if (!this.becameVisibleAt) {
      this.becameVisibleAt = Date.now();
      // We're now visible; after viewedAfterMs, if the top and bottom have been
      // seen, this block will count as viewed.
      setTimeout(
        () => {
          this.checkIfViewed();
        },
        this.viewedAfterMs - this.seenForMs,
      );
    }
  }

  handleNotVisible() {
    if (this.becameVisibleAt) {
      this.seenForMs = Date.now() - this.becameVisibleAt;
    }
    this.becameVisibleAt = undefined;
  }

  markTopSeen() {
    // If this element has been seen for enough time, but the top wasn't visible, it may now be
    // considered viewed.
    this.topSeen = true;
    this.checkIfViewed();
  }

  markBottomSeen() {
    this.bottomSeen = true;
    this.checkIfViewed();
  }

  getTotalTimeSeen() {
    if (this.becameVisibleAt) {
      return this.seenForMs + (Date.now() - this.becameVisibleAt);
    }
    return this.seenForMs;
  }

  areViewedCriteriaMet() {
    return this.topSeen && this.bottomSeen && (this.getTotalTimeSeen() >= this.viewedAfterMs);
  }

  checkIfViewed() {
    // User can provide a "now" value for testing purposes.
    if (this.hasBeenViewed) {
      return;
    }
    if (this.areViewedCriteriaMet()) {
      this.hasBeenViewed = true;
      // Report to the tracker that we have been viewed
      this.callback(this.el, { elementHasBeenViewed: this.hasBeenViewed });
    }
  }
}


class ViewedEventTracker {
  /**
   * When the top or bottom of an element is first viewed, and the entire
   * element is viewed for a specified amount of time, the callback is called,
   * passing the element that was viewed, and an event object having the
   * following field:
   *
   * *   hasBeenViewed (bool): true if all the conditions for being
   *     considered "viewed" have been met.
   */
  constructor() {
    this.elementViewings = new Set();
    this.handlers = [];
    this.registerDomHandlers();
  }

  /** Add an element to track.  */
  addElement(element, viewedAfterMs) {
    this.elementViewings.add(
     new ElementViewing(
       element,
       viewedAfterMs,
       (el, event) => this.callHandlers(el, event),
      ),
    );
    this.updateVisible();
  }

  /** Register a new handler to be called when an element has been viewed.  */
  addHandler(handler) {
    this.handlers.push(handler);
  }

  /** Mark which elements are currently visible.
   *
   *  Also marks when an elements top or bottom has been seen.
   * */
  updateVisible() {
    this.elementViewings.forEach((elv) => {
      if (elv.hasBeenViewed) {
        return;
      }

      const now = Date.now(); // Use the same "now" for all calculations
      const rect = elv.getBoundingRect();
      let visible = false;

      if (rect.top > 0 && rect.top < window.innerHeight) {
        elv.markTopSeen(now);
        visible = true;
      }
      if (rect.bottom > 0 && rect.bottom < window.innerHeight) {
        elv.markBottomSeen(now);
        visible = true;
      }
      if (rect.top < 0 && rect.bottom > window.innerHeight) {
        visible = true;
      }

      if (visible) {
        elv.handleVisible(now);
      } else {
        elv.handleNotVisible(now);
      }
    });
  }

  registerDomHandlers() {
    window.onscroll = throttle(() => this.updateVisible(), 100);
    window.onresize = throttle(() => this.updateVisible(), 100);
    this.updateVisible();
  }

  /** Call the handlers for all newly-viewed elements and pause tracking
   *  for recently disappeared elements.
   */
  callHandlers(el, event) {
    this.handlers.forEach((handler) => {
      handler(el, event);
    });
  }
}
