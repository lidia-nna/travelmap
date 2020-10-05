// var map;
// var markers;

function initMap() {
map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 15.262, lng: 9.687},
    zoom: 2,
    mapTypeId: 'hybrid',
    disableDefaultUI: true
});
// setMarkers(map);
// }

// function setMarkers(map) {
//     // Adds markers to the map.

//     // Marker sizes are expressed as a Size of X,Y where the origin of the image
//     // (0,0) is located in the top left of the image.

//     // Origins, anchor positions and coordinates of the marker increase in the X
//     // direction to the right and in the Y direction down.
//     console.log(markers)
//     var shape = {
//       coords: [1, 1, 1, 20, 18, 20, 18, 1],
//       type: 'poly'
//     };
//     // var pins = {{ markers|tojson }};
//     var pins = markers
//     var bounds = new google.maps.LatLngBounds();

//     for (i = 0; i < pins.length; i++) {
//         var pin = pins[i];
//         var lat_c = pin.lat;
//         var lng_c = pin.lng;
//         var position = { lat: parseFloat(lat_c), lng: parseFloat(lng_c) };
//         var image = {
//           url: pin.icon_uri,
//           // This marker is 20 pixels wide by 32 pixels high.
//           size: new google.maps.Size(24,24),
//           // The origin for this image is (0, 0).
//           origin: new google.maps.Point(0, 0),
//           // The anchor for this image is the base of the flagpole at (0, 32).
//           anchor: new google.maps.Point(1, 22)
//         };
//         var marker = new google.maps.Marker({
//             position: position,
//             map: map,
//             title: pin.name,
//             icon: image,
//             shape: shape,
//             animation: google.maps.Animation.DROP
//             });
//         bounds.extend(position);
//     }
//     map.fitBounds(bounds);
}