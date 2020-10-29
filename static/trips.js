var map;
var markers;

function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 15.262, lng: 9.687 },
        zoom: 2,
        mapTypeId: 'hybrid',
        disableDefaultUI: true
    });

    setMarkers(map);
    }
    const getPin = (colour) => {
        return {
            path: "M 0,0 0,55 5,55 5,0 z M 10,0 45,0 30,10 45,20 10,20 10,0 z",
            fillColor: colour,
            fillOpacity: 0.8,
            scale: 0.5,
            strokeColor: "black",
            strokeWeight: 2,
            anchor: new google.maps.Point(0, 55)
        }
    };
    function setMarkers(map) {
        // Adds markers to the map.
        // var pins = {{ markers|tojson }};
        const pins = markers
        const bounds = new google.maps.LatLngBounds();
        pins.forEach(pin => {
            let lat_c = pin.lat;
            let lng_c = pin.lng;
            let position = { lat: parseFloat(lat_c), lng: parseFloat(lng_c) };
    //         var image = {
    //           url: pin.icon_uri,
    //           // This marker is 20 pixels wide by 32 pixels high.
    //           size: new google.maps.Size(24,24),
    //           // The origin for this image is (0, 0).
    //           origin: new google.maps.Point(0, 0),
    //           // The anchor for this image is the base of the flagpole at (0, 32).
    //           anchor: new google.maps.Point(1, 22)
    //         };
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: pin.name,
                icon: getPin(pin.colour),
                animation: google.maps.Animation.DROP
                });
            bounds.extend(position);
        });
        map.fitBounds(bounds);
}