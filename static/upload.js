


/*  ==========================================
    SHOW UPLOADED IMAGE
* ========================================== */
var picArea = document.getElementsByClassName('image-area mt-4')[0];
    console.log('picArea: ', picArea)


function createInput(value){
    console.log('Running createInput! for',value)
    var inputTag = document.createElement("img");
    inputTag.id=value
    inputTag.className="img-fluid rounded shadow-sm mx-auto d-block"
    inputTag.src='#'
    console.log('InputTag:', inputTag)
    return inputTag
};

function readURL(input) {   
    var ChildNodes = picArea.childNodes
    var childNumber = ChildNodes.length
    console.log('childnumber:', childNumber)
    console.log('ChildNodes:',ChildNodes)
    console.log('picArea.childNodes', picArea.childNodes)
    while (picArea.firstChild){
        picArea.removeChild(picArea.firstChild)
    }
    // TODO investigate why the below doesn't work and while loop does
    // if (childNumber > 0) {
    //     for (i=0; i<childNumber;i++){
    //         const beforeRem = picArea
    //         console.log('Before removal, this is picArea', beforeRem)
    //         console.log('Child:',ChildNodes[i])
    //         picArea.removeChild(ChildNodes[i])
    //         const afterRem = picArea
    //         console.log('After removal, this is picArea', afterRem)
    //     }
    // }
    // console.log('First Child:',picArea.firstChild)
    // console.log('Last Child:',picArea.lastChild)
    // ChildNodes.forEach(Child => picArea.removeChild(Child))
    if (input.files && input.files[0]) {
        for (i=0; i< input.files.length; i++){
            var file = input.files[i];
            var newInput = createInput(file.name)
            newInput.file = file
            picArea.append(newInput)
            var reader = new FileReader();
            reader.onload = (function(aImg) { return function(e) { aImg.src = e.target.result; }; })(newInput);
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