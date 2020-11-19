var map;
var markers;
var trips;

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
            strokeWeight: 1,
            anchor: new google.maps.Point(0, 55)
        }
    };
    function setMarkers(map) {
        // Adds markers to the map.
        // var pins = {{ markers|tojson }};
        const pins = markers
        const bounds = new google.maps.LatLngBounds();
        pins.forEach(pin => {
            // pin.lat/pin.lng equal to NaN or undifined or [] or "" would allow belot to run
            if ( pin.lat !== null & pin.lng !== null ) {
                let lat_c = pin.lat;
                let lng_c = pin.lng;
                let position = { lat: parseFloat(lat_c), lng: parseFloat(lng_c) };

                const infowindow = new google.maps.InfoWindow({
                    content: `<img style="width: 100%; border-radious: 1px; border-color: black;" src="/photos/${user_id}/${pin.filename}" onclick="window.location.href">
                    <span>${pin.city}</span>`,
                });
                const marker = new google.maps.Marker({
                    position: position,
                    map: map,
                    title: pin.name,
                    icon: getPin(pin.colour),
                    animation: google.maps.Animation.DROP
                    });
                marker.addListener("click", () => {
                    infowindow.open(map, marker);
                    });
                bounds.extend(position);
            }
        });
    
    //         var image = {
    //           url: pin.icon_uri,
    //           // This marker is 20 pixels wide by 32 pixels high.
    //           size: new google.maps.Size(24,24),
    //           // The origin for this image is (0, 0).
    //           origin: new google.maps.Point(0, 0),
    //           // The anchor for this image is the base of the flagpole at (0, 32).
    //           anchor: new google.maps.Point(1, 22)
    //         };
            

        

    const legend = document.getElementById("legend");
    console.log('trips:', trips)
    trips.forEach((trip) => {
        let icon = getPin(colour=trip[1]);
        const name = trip[0];
        const rowItem = document.createElement('div')
        rowItem.setAttribute('class', 'rowItem')
        const svgNS = "http://www.w3.org/2000/svg"; 
        let svg = document.createElementNS(svgNS, "svg");
        svg.setAttributeNS(null, "height","30");
        svg.setAttributeNS(null,"width", "30");
        // el.setAttributeNS('xmlns', 'http://www.w3.org/2000/svg')
        let pathSVG = document.createElementNS(svgNS,"path");
        pathSVG.setAttributeNS(null,"d", icon.path) ;
        pathSVG.setAttributeNS(null,"fill", icon.fillColor);
        pathSVG.setAttributeNS(null,"stroke", icon.strokeColor);
        pathSVG.setAttributeNS(null,"stroke-width", icon.strokeWeight);
        pathSVG.setAttributeNS(null,"scale", 0.5);
        let tripId = document.createElement('span')
        tripId.setAttribute('class', 'tripId')
        tripId.innerHTML = trip[0]
        svg.appendChild(pathSVG);
        rowItem.appendChild(svg)
        rowItem.appendChild(tripId)
        legend.appendChild(rowItem);  
    }) 
       
    map.controls[google.maps.ControlPosition.RIGHT_BOTTOM].push(legend);

    map.fitBounds(bounds);
}