const getImages = (trip_id, user_id) => {
    try {
        window.location.href=`http://127.0.0.1:5000/photos/${user_id}/${trip_id}`
        // const response = await fetch(`http://127.0.0.1:5000/home/${user_id}/photos/${trip_id}`;
        // if (response.status===200) {
        //     window.location.href = response.url
        //     console.log(response)
        //     return response
        // }
        // else {
        //     console.log('Not redirected')
        // }
    } catch (error) {
        error => `Error ${error.status}: ${error.textContent}` 
    }   
}

const toggleImage = (thumbnail, user_id) => {
    const imageEl = document.getElementById(thumbnail)
    const orgImage = thumbnail.replace('_thumbnail', '');
    const thumbnailSrc = `http://127.0.0.1:5000/photos/${user_id}/${thumbnail}`;
    const orgImageSrc = `http://127.0.0.1:5000/photos/${user_id}/${orgImage}`;
    imageEl.src = (imageEl.src === thumbnailSrc)? orgImageSrc : thumbnailSrc;  

}


