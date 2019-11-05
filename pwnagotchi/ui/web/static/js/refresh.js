window.onload = function() {
    var image = document.getElementById("ui");
    function updateImage() {
        image.src = image.src.split("?")[0] + "?" + new Date().getTime();
    }
    setInterval(updateImage, 1000);
}