var svgUrl = "{% static 'images/diagram.svg' %}";
var dzcOutputUrl = "{% static 'images/' %}";
var dzcOutputFilename = 'diagram_dzi.dzi';

// Get the aspect ratio of the SVG image
var svgAspectRatio = 0;
var svgImage = new Image();
svgImage.src = svgUrl;


svgImage.onload = function() {
  svgAspectRatio = svgImage.width / svgImage.height;

    var viewer = OpenSeadragon({
        id: "myViewer",
        prefixUrl: "{% static 'openseadragon-bin-4.0.0/images/' %}",
        tileSources: {
            type: 'legacy-image-pyramid',
            levels: [{
                url: svgUrl,
                width: 10000 * svgAspectRatio, // Set the width to match the SVG aspect ratio
                height: 10000,
            }]
        }
    });

    viewer.viewport

    viewer.addHandler("zoom", function() {
        console.log("Zoom level: " + viewer.viewport.getZoom(true));
    });

    viewer.addHandler("pan", function() {
        console.log("Center coordinates: " + viewer.viewport.getCenter(true));
    });


    viewer.addHandler('open', function() {

        // Get the SVG element
        var svg = viewer.world.getItemAt(0).content.firstChild;

        // Get the bounding box of the image and set the viewBox attribute
        var bbox = svg.getBBox();
        svg.setAttribute('viewBox', bbox.x + ' ' + bbox.y + ' ' + bbox.width + ' ' + bbox.height);

        OpenSeadragon.Utils.getDZI({
            tileSource: viewer.world.getTileSource(),
            callback: function(dzi) {
                dzi.dziUri({
                    callback: function(dziUri) {
                        var dzcJson = {
                            Image: {
                                xmlns: 'http://schemas.microsoft.com/deepzoom/2008',
                                Url: dziUri.replace('.dzi', '_files'),
                                Format: 'png',
                                Overlap: '0',
                                TileSize: '128',
                                Size: {
                                    Width: dzi.width,
                                    Height: dzi.height
                                }
                            }
                        };
                        var dzcOutput = OpenSeadragonDzc.createDzc(dzcJson);
                        OpenSeadragonDzc.saveDzc(dzcOutput, dzcOutputUrl, dzcOutputFilename);
                    }
                });
            }
        });
    });
};