// $('#tripForm').on('submit', function(e){
//     $('#exampleModal').modal('show');
//     e.preventDefault();
//     });


async function postData(user_id) {
    const form = document.getElementById('tripForm');
    var trip_id = form.trip_id.value
    var description = form.description.value
    var marker_colour = form.marker_colour.value
    var marker_id = form.marker_id.value
    var countries = form.countries.value
    let data = new FormData();
    data.append('user_id', user_id)
    data.append('trip_id', trip_id);
    data.append('description', description)
    data.append('marker_colour', marker_colour)
    data.append('marker_id', marker_id);
    data.append('countries', countries)

    let response = await fetch(`/home/trips/${user_id}/addtrip`, {
        method: 'POST', body: data});
    
    if (response.ok){
        if (response.status == 201) {
            // let json = await response.json()
            // bootstrap jquery
            //TODO create updatedModal and update addedModal to updatedModal
            $('#updatedModal').modal('show');
        } else if (response.status == 200) {
            // let json = await response.json()
            //bootstrap jquery
            $('#addedModal').modal('show');
            // preventDefault();
        }} else {
            let json = await response.json()
            console.log(json);
            var message = JSON.stringify(json);
            throw new Error(message);
        }
    
    
}

function callUpload(user_id){
    const form = document.getElementById('tripForm');
    var trip = form.trip_id.value
    let url = `/home/upload/${user_id}?trip_id=${trip}`
    window.location.href = url
}