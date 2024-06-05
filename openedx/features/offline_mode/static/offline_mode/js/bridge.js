function sendMessageToiOS(message) {
  window?.webkit?.messageHandlers?.iOSBridge?.postMessage(message);
}

function sendMessageToAndroid(message) {
  window?.AndroidBridge?.postMessage(message);
}

function receiveMessageFromiOS(message) {
  console.log("Message received from iOS:", message);
}

function receiveMessageFromAndroid(message) {
  console.log("Message received from Android:", message);
}

if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.iOSBridge) {
  window.addEventListener("messageFromiOS", function (event) {
    receiveMessageFromiOS(event.data);
  });
}
if (window.AndroidBridge) {
  window.addEventListener("messageFromAndroid", function (event) {
    receiveMessageFromAndroid(event.data);
  });
}
const originalAjax = $.ajax;
$.ajax = function (options) {
  sendMessageToiOS(options);
  sendMessageToiOS(JSON.stringify(options));
  sendMessageToAndroid(options);
  sendMessageToAndroid(JSON.stringify(options));
  console.log(options, JSON.stringify(options));
  return originalAjax.call(this, options);
};
