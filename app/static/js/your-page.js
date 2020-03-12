isDescriptionEditable = 0;

(function () {
    var a = document.getElementById("description-input"),
        limit = 4;//Define max lines limit

    function limitLines() {
        var l = a.value.replace(/\r\n/g, "\n").replace(/\r/g, "").split(/\n/g);//split lines
        if (l.length > limit) {
            a.value = l.slice(0, limit).join("\n");
        }
    }

    function paste() {//onpaste needs timeout
        setTimeout(limitLines, 1);
    }

    limitLines(); //Like onload

    a.onkeyup = limitLines;
    a.onpaste = paste;
})();

var editDescription = function()
{
     var input = document.getElementById("description-input");

    if (isDescriptionEditable){

        var description = input.value;
        $('#description-text').text(description);
        $('#edit-button').text('Edit description');
        var xhr = new XMLHttpRequest();
        xhr.open("POST", 'http://127.0.0.1:5000/backend', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({
         type: 1,
         description: description
        }));
        isDescriptionEditable = 0;

        $('#edit-form').hide();
        $('#description-input').text('');
        $('#description-input').hide();
        $('#description-text').show();

    } else {
        $('#edit-button').text('Save edits');
        $('#description-text').hide();
        $('#description-input').show();
        isDescriptionEditable = 1;

    }
}

$("#media").change(function() {
  filename = this.files[0].name
  console.log(filename);
  document.getElementById("media-label").innerText = filename
});