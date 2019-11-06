/* https://css-tricks.com/the-trick-to-viewport-units-on-mobile/*/

var lastViewportHeight;

function updateViewportSize() {
  // First we get the viewport height and we multiple it by 1% to get a value for a vh unit
  var vh = window.innerHeight * 0.01;
  if (!lastViewportHeight || lastViewportHeight !== vh) {
    // Then we set the value in the --vh custom property to the root of the document
    document.documentElement.style.setProperty("--vh", vh + "px");
    lastViewportHeight = vh;
  }
}

document.addEventListener("DOMContentLoaded", function() {
  updateViewportSize();
});