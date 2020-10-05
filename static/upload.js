

function createInput(value){
    var inputTag = document.createElement("img");
    inputTag.id=value
    inputTag.className="img-fluid rounded shadow-sm mx-auto d-block"
    inputTag.src='#'
    return inputTag
};

/*  ==========================================
    SHOW UPLOADED IMAGE
* ========================================== */
var picArea = document.getElementsByClassName('image-area mt-4')[0];
function readURL(input) {
    if (input.files && input.files[0]) {
        for (i=0; i< input.files.length; i++){
            var file = input.files[i];
            var newInput = createInput(file.name)
            newInput.file = file
            picArea.appendChild(newInput)
            var reader = new FileReader();
            reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(newInput);
            console.log(newInput.src)
            reader.readAsDataURL(file); 
        }
    }
}
//         var reader = new FileReader();

//         reader.onload = function (e) {
//             $('#imageResult')
//                 .attr('src', e.target.result);
//         };
//         console.log(input.files[0])
//         reader.readAsDataURL(input.files[0]);
//     }
// }

// $(function () {
//     $('#upload').on('change', function () {
//         readURL(input);
//     });
// });

/*  ==========================================
    SHOW UPLOADED IMAGE NAME
* ========================================== */
var input = document.getElementById( 'upload' );
var infoArea = document.getElementById( 'upload-label' );

input.addEventListener( 'change', showFileName );
function showFileName( event ) {
  var input = event.srcElement;

  var fileName = input.files[0].name;
  infoArea.textContent = 'File name: ' + fileName;
}