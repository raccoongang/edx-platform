function sendMessageToIOS(message) {
  window?.webkit?.messageHandlers?.IOSBridge?.postMessage(message);
}

function sendMessageToAndroid(message) {
  window?.AndroidBridge?.postMessage(message);
}

function markProblemCompletedIOS(message) {
  markProblemCompleted(message);
}

function markProblemCompletedAndroid(message) {
  markProblemCompleted(message);
}

function markProblemCompleted(message) {
  const data = JSON.parse(message).data;

  const prob = $(".xblock-student_view");
  prob.find('.submit-attempt-container .submit').attr({disabled: "disabled"});
  prob.find('.notification-gentle-alert .notification-message').html("Answer submitted.");
  prob.find('.notification-gentle-alert').show();


  data.split("&").forEach(function (item) {
    const [input, answer] = item.split('=', 2);
    prob.find('input[id$="' + answer + '"], input[id$="' + input + '"]').each(function () {
      $(this).attr({disabled: "disabled"})
      if (this.type === "checkbox" || this.type === "radio") {
        this.checked = true;
      } else {
        this.value = answer;
      }
    })
  })
}

if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.IOSBridge) {
  window.addEventListener("messageFromIOS", function (event) {
    markProblemCompletedIOS(event.data);
  });
}

if (window.AndroidBridge) {
  window.addEventListener("messageFromAndroid", function (event) {
    markProblemCompletedAndroid(event.data);
  });
}

const originalAjax = $.ajax;
$.ajax = function (options) {
  if (options.url && options.url.endsWith("problem_check")) {
    sendMessageToIOS(JSON.stringify(options));
    sendMessageToAndroid(JSON.stringify(options));
  }
  return originalAjax.call(this, options);
}
