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
        timeout: 0,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods' : 'POST'
        },
        uploadprogress: function(file, progress, bytesSent) {

            var width = $(file.previewElement).find('span.dz-upload').width();
            var parentWidth = $(file.previewElement).find('span.dz-upload').offsetParent().width(); // this will return parent element's width which also can be replaced with docuent to get viewport width
            var current_percent = Math.round(100*width/parentWidth);
            var progress_percent = Math.round(100*bytesSent/file.size);

            if (progress_percent > current_percent){
                $(file.previewElement).find('span.dz-upload').css('width', progress_percent+'%');
                console.log('Upload @ ' + progress_percent + '%');
            }
        }
    });
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
    event.preventDefault();
    descriptionInput = document.getElementById("description-input");
    description = $("#description-text").text();
    if (isDescriptionEditable){

        description = descriptionInput.value;
        $('#description-text').text(description);
        $('#edit-desc-button').text('Edit description');
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
        $('#edit-desc-button').text('Save edits');
        $('#description-text').hide();
        $('#description-input').val(description);
        $('#description-input').show();
        isDescriptionEditable = 1;
    }
};
function uploadMedia() {
    event.preventDefault();
    if(!isUploadFormVisible){
        dropperForm = document.getElementById("upload-form");
        dropperForm.className = '';
        isUploadFormVisible = 1;
        $("body").addClass("modal-open");

    } else {
        dropperForm = document.getElementById("upload-form");
        dropperForm.className = 'hidden';
        isUploadFormVisible = 0;
        $("body").removeClass("modal-open");
        refreshMedia(true);
    }

};

var deleteMedia = function(event, id){
    event.preventDefault();
    if (confirmation_display_media == 0){
            document.getElementById("zoom-media").className = 'hidden';
            $("#confirmation-dialog-container").css("display", "unset");
            $("#confirmation-dialog-container").find('div').find('p').text(' Are you sure you want to delete this media?');
            $("body").addClass("modal-open");
            confirmation_display_media = 1;
            media_id = id;

     }
};

var deleteWork = function(id){
    event.preventDefault();
    if (confirmation_display_works == 0){
            $("#confirmation-dialog-container").css("display", "unset");
            $("#confirmation-dialog-container").find('div').find('p').text(' Are you sure you want to delete this work?');
            $("body").addClass("modal-open");
            confirmation_display_works = 1;
            work_id =  $(event.target).parent(".work-buttons").parent().parent().parent().parent().attr('id');
            work_id = work_id.split("_")[1];

     }
};

var confirmDialog = function(){
    event.preventDefault();
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
                location.reload();
            }
        });
    }
};
var cancelDialog = function(){
    event.preventDefault();
    $("#confirmation-dialog-container").css("display", "none");
    $("body").removeClass("modal-open");
    if (confirmation_display_works == 1){
        confirmation_display_works = 0;
    } else {
        confirmation_display_media = 0;
        document.getElementById("zoom-media").className = 'flex';
    }

};