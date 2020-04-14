isDescriptionEditable = 0;
isUploadFormVisible = 0;
confirmation_display_works = 0;
confirmation_display_media = 0;
work_id = 0;
media_id = 0;

window.addEventListener("dragover",function(e){
  e = e || event;
  e.preventDefault();
},false);
window.addEventListener("drop",function(e){
  e = e || event;
  e.preventDefault();
},false);

Dropzone.autoDiscover = false;
$(function() {
    $('#dropper').dropzone({
        paramName: 'file',
        chunking: true,
        forceChunking: true,
        url: '/upload',
        method: 'post',
        maxFilesize: 1025, // megabytes
        chunkSize: 1000000, // bytes

        totaluploadprogress: function(file, progress, bytesSent) {
            console.log(progress);
            //$(".dz-progress > dz-upload").style.width = progress + "%";
        }
    });
});

$('#dropper').on("totaluploadprogress", function(progress) {
    console.log(progress);
    if ($(".dz-progress > dz-upload").style.width <= progress){
        $(".dz-progress > dz-upload").style.width = progress + "%";
    }
});


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
    descriptionInput = document.getElementById("description-input");
    description = $("#description-text").text();
    if (isDescriptionEditable){

        description = descriptionInput.value;
        $('#description-text').text(description);
        $('#edit-button').text('Edit description');
        $.ajax({
            url: '/backend',
            type: 'POST',
            data: JSON.stringify ({
                'type': 1,
                'description': description
            }),

            contentType: "application/json",
            dataType: 'json',
            success: function(response){
                isDescriptionEditable = 0;
                $('#edit-form').hide();
                $('#description-input').text('');
                $('#description-input').hide();
                $('#description-text').show();
            },
            fail: function(response){
                location.reload();
            }
        });
    } else {
        $('#edit-button').text('Save edits');
        $('#description-text').hide();
        $('#description-input').val(description);
        $('#description-input').show();
        isDescriptionEditable = 1;
    }
}

var uploadMedia = function()
{
    dropperForm = document.getElementById("upload-form");
    if (isUploadFormVisible){
        dropperForm.className = 'hidden';
        isUploadFormVisible = 0;
        $("body").removeClass("modal-open");
        refreshMedia(true);
    } else {
        dropperForm.className = '';
        isUploadFormVisible = 1;
        $("body").addClass("modal-open");
    }

}

var deleteMedia = function(id){
    if (confirmation_display_media == 0){
            document.getElementById("zoom-media").className = 'hidden';
            $("#confirmation-dialog-container").css("display", "unset");
            $("#confirmation-dialog-container").find('div').find('p').text(' Are you sure you want to delete this media?')
            $("body").addClass("modal-open");
            confirmation_display_media = 1;
            media_id = id
     }
}

$( ".work-buttons > a.delete" ).click(function( event ) {

    if (confirmation_display_works == 0){
            $("#confirmation-dialog-container").css("display", "unset");
            $("#confirmation-dialog-container").find('div').find('p').text(' Are you sure you want to delete this work?')
            $("body").addClass("modal-open");
            confirmation_display_works = 1;
            work_id =  $(event.target).parent(".work-buttons").parent().parent().parent().parent().attr('id');
            work_id = work_id.split("_")[1];

     }
});
$( ".confirmation-dialog-buttons > a.delete" ).click(function(){
    if (confirmation_display_media == 0){
        $.ajax({
            url: '/works/delete',
            type: 'POST',
            data: JSON.stringify ({
                'work_id': work_id
            }),

            contentType: "application/json",
            dataType: 'json',
            beforeSend: function(){
                $('#loading-spinner').show();
                $('#confirmation-info').hide();
            },
            success: function(response){
                location.reload();
            }
        });
    }else{
        $.ajax({
            url: '/media/delete',
            type: 'POST',
            data: JSON.stringify ({
                'media_id': media_id
            }),

            contentType: "application/json",
            dataType: 'json',
            beforeSend: function(){
                $('#loading-spinner').show();
                $('#confirmation-info').hide();
            },
            success: function(response){
                location.reload()
            }
        });
    }
});
$( ".confirmation-dialog-buttons > a.cancel" ).click(function(){
    $("#confirmation-dialog-container").css("display", "none");
    $("body").removeClass("modal-open");
    if (confirmation_display_media == 0){
        confirmation_display_works = 0;
    } else {
        confirmation_display_media = 0;
        document.getElementById("zoom-media").className = 'flex';
    }
});