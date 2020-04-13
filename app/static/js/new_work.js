isUploadFormVisible = 0;

(function () {
    var a = document.getElementById("body"),
        limit = 7;//Define max lines limit

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

$(document).ready(function () {

    $('#upload-button').hide();
    $('#media-tip').text('Click to view the media files');
    refreshMedia();
});

Dropzone.autoDiscover = false;
$(function() {
    $('#dropper').dropzone({
        paramName: 'file',
        chunking: true,
        forceChunking: true,
        url: '/upload',
        method: 'post',
        maxFilesize: 1025, // megabytes
        chunkSize: 1000000 // bytes
    });
});

var uploadMedia = function()
{
    var dropperForm = document.getElementById("upload-form");
    if (isUploadFormVisible){
        dropperForm.className = 'hidden';
        isUploadFormVisible = 0;
        refreshMedia(false, applySelectionCallback, attached_media);
        console.log(attached_media);
        $("body").removeClass("modal-open");
    } else {
        dropperForm.className = '';
        isUploadFormVisible = 1;
        $("body").addClass("modal-open");
    }

}
attached_media = [];
isMediaEditable = 0;
var submitWork = function(){
    if (isMediaEditable == 0) {

        title = $('#form-title > #title').val();
        description = $('#form-description > #body').val();
        //console.log(attached_media);
        $.ajax({
                    url: '/works/new-work',
                    type: 'POST',
                    contentType: "application/json",
                    dataType: 'json',
                    data: JSON.stringify({
                        'title': title,
                        'description': description,
                        'attached_media': attached_media
                        }),
                        beforeSend: function(){
                            $('#loading-spinner').show();
                            $('#submit-button').hide();
                        },
                        success: function(response){
                            window.location.href = '/works/' + response;
                        }
                    });
    }
}

var editMedia = function(){
    if (isMediaEditable) {

        $("#submit-button").show();
        $('#media-tip').text('Click to view the media files');
        if (attached_media.length == 0){
                    $('#media-panel-title').text('All media files:');
                } else {
                    if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                }
        $('#upload-button').hide();
        $('#attach-button').text('Attach files:');
        isMediaEditable = 0;
    } else {
        isMediaEditable = 1;
        $("#submit-button").hide();

        $('#media-tip').text('Click to select the media files to attach');
        if (attached_media.length == 0){
                    $('#media-panel-title').text('Attach files:');
                } else {
                    if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                }
        $('#upload-button').show();
        $('#attach-button').text('Save');
    }
}
display = 0;
playing_media = null;
$(document).on("click","#media-slider > div", function (event) {

    if (isMediaEditable) {
        if (event.target.parentElement.id != "media-slider"){
            if (event.currentTarget.classList.contains("selected-media")){
                event.currentTarget.classList.remove("selected-media");
                img_src = event.target.getAttribute('src');
                idx = attached_media.indexOf(img_src);
                attached_media.splice(idx,1);
            }
            else{
                if (event.target.getAttribute('src') == '\\static\\resources\\pdf-placeholder-icon.png'){
                    pdf_name = $(this).find('div').find('p').text();
                    pdf_src = '\\static\\user_uploads\\' + pdf_name + '.pdf';
                    attached_media.push(pdf_src);
                } else if (event.target.getAttribute('src') != null){
                    attached_media.push(event.target.getAttribute('src'));
                } else {
                    attached_media.push($(event.target).find('source').attr('src'));
                }
                event.currentTarget.classList.add("selected-media");
            }
            if (attached_media.length == 0){
                $('#media-panel-title').text('Attach files:');
            } else if (attached_media.length == 1){
                $('#media-panel-title').text(attached_media.length + " file selected");
            } else {
                $('#media-panel-title').text(attached_media.length + " files selected");
            }
        }
    } else {
        if (display == 0){
            media_id = $(this).attr('id').substring(13);
            src_img = $(this).find('img').attr('src');
            src_img_pdf = $(this).find('div').find('img').attr('src');
            src_video = $(this).find('video').find('source').attr('src');
            if (src_video != null){
                $("#zoom-video").attr('src',src_video);
                $("#zoom-video").show();
                $("#zoom-img").hide();
                $("#zoom-pdf").hide();
                playing_media = $(this).find('video').attr('id');
            } else if (src_img_pdf != null){
                pdf_name = $(this).find('div').find('p').text();
                pdf_src = '/static/user_uploads/' + pdf_name + '.pdf';
                $("#zoom-pdf").attr('href',pdf_src);
                xheight = window.innerHeight/1.4;
                ywidth = ($(document).width()/100)*75;
                $('#zoom-pdf').media({height:xheight});
                $("#zoom-video").hide();
                $("#zoom-img").hide();
                $("#zoom-pdf").show();
                isShowingPdf = true;
            } else if (src_img != null){
                $("#zoom-img").attr('src',src_img);
                $("#zoom-video").hide();
                $("#zoom-pdf").hide();
                $("#zoom-img").show();
            }
            document.getElementById("zoom-media").className = 'flex';
            $("body").addClass("modal-open");
            display = 1;
        }
    }
});

$(document).on("click","#zoom-close",function() {
      if (display == 1){
            document.getElementById("zoom-media").className = 'hidden';
            $("body").removeClass("modal-open");
            if (playing_media != null){
                document.getElementById(playing_media).pause()
            }
            display = 0;
       }
    });
