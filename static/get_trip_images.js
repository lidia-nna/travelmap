// let trip_id;
// let user_id;

// const cards = document.querySelectorAll('.card');

// cards.forEach(card => { 
//   card.addEventListener('click', function(e, trip_id, user_id) {
//     if (this === e.target){
//       getImages(trip_id, user_id)
//     }
//   })
  
// });
// $('.card > .bin-holder').click(function(e){ e.stopPropagation(); });

const getImages = (tid, uid) => {
    try {
        window.location.href=`/home/photos/${user_id}/${trip_id}`;
    } catch (error) {
        error => `Error ${error.status}: ${error.textContent}`; 
    }   
};


const deleteTrip = async (user_id, trip_id ) => {
  let request = await fetch(`/home/trips/${user_id}?trip_id=${trip_id}`, {
    method: 'delete'
  })
  response = await request.json();
  if (request.status != 200) {
      console.log(response)
  } else {
  window.location.reload()
  }}

// const toggleImage = (thumbnail, user_id) => {
//     const imageEl = document.getElementById(thumbnail)
//     const orgImage = thumbnail.replace('_thumbnail', '');
//     const thumbnailSrc = `http://127.0.0.1:5000/photos/${user_id}/${thumbnail}`;
//     const orgImageSrc = `http://127.0.0.1:5000/photos/${user_id}/${orgImage}`;
//     imageEl.src = (imageEl.src === thumbnailSrc)? orgImageSrc : thumbnailSrc;  

// }


function openModal() {
    document.getElementById("myModal").style.display = "block";
  }

function closeModal() {
    document.getElementById("myModal").style.display = "none";
}

var slideIndex = 1;
showSlides(slideIndex);

// Next/previous controls
function plusSlides(n) {
    slideIndex = Number(slideIndex) + n
  showSlides(slideIndex);
}

// Thumbnail image controls
function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
    // console.log('SlideIndex at the call:', slideIndex)
    // console.log('N at the call:', n)
  var i;
  var slides = document.getElementsByClassName("mySlides");
//   var dots = document.getElementsByClassName("demo");
//   var captionText = document.getElementById("caption");
  console.log('n:', n)
  if (n > slides.length) { slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  console.log('slideIndex:', slideIndex)
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
//   for (i = 0; i < dots.length; i++) {
//     dots[i].className = dots[i].className.replace(" active", "");
//   }
  slides[slideIndex-1].style = "display: flex; height: 70vh; justify-content: center;";
  console.log(slideIndex)
//   slides[slideIndex-1].style.height = "50%";


//   dots[slideIndex-1].className += " active";
//   captionText.innerHTML = dots[slideIndex-1].alt;
}



const deleteData = async (user_id, image_id ) => {
  let request = await fetch(`/home/upload/${user_id}?image_id=${image_id}`, {
    method: 'delete'
  })
  response = await request.json();
  if (request.status != 200) {
      console.log(response)
  } else {
  window.location.reload()
  }}
