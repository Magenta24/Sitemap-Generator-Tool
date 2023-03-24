// This is a comment in JavaScript

// This code runs when the page finishes loading
window.onload = function() {
    var pic2 = new Image();
    pic2.src = "{% static 'images/diagram.svg' %}"
    console.log(pic2.src);

    var viewer = OpenSeadragon({
        id: "myViewer",
        prefixUrl: "openseadragon/images/",
        tileSources: {
            type: "image",
            url: pic2.src
        }
    });

    viewer.addHandler("zoom", function() {
        console.log("Zoom level: " + viewer.viewport.getZoom(true));
    });

    viewer.addHandler("pan", function() {
        console.log("Center coordinates: " + viewer.viewport.getCenter(true));
    });
};