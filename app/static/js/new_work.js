
$(document).ready(function () {

    $('#upload-form').hide();
    $('#media-tip').text('Click to view your media');



    fetch(`/backend?t=1`).then((response) => {
        // Convert the response data to JSON
        response.json().then((data) => {
                media_slider = document.getElementById('media-slider');
                for (var i=0; i < data.length ;i++){
                    ext = data[i].split('.')[1];
                    if (ext == 'mp4'){
                            html = '<div><video id="single-video-'+i+'" src="'+data[i]+'" style="width:310px;height:auto"></video>';
                    }else{
                            html = '<div><img id="single-media-'+i+'" src="'+data[i]+'" style="width:310px;height:auto"></div>';
                        }
                    media_slider.insertAdjacentHTML("beforeend", html);
                }
            })
        })

});

attached_media = [];
isMediaEditable = 0;
var submitWork = function(){
    if (isMediaEditable == 0) {

        title = $('#form-title > #title').val();
        description = $('#form-description > #body').val();
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
                    success: function(response){
                        window.location.href = '/works/' + response;
                    }
                    });
    }
}

var editMedia = function(){
    if (isMediaEditable) {
        $("#submit-button").show();
        $('#media-tip').text('Click to view your media');
        if (attached_media.length == 0){
                    $('#media-panel-title').text('All media files:');
                } else {
                    if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                }
        $('#upload-form').hide();
        $('#attach-button').text('Attach files:');
        isMediaEditable = 0;
    } else {
        isMediaEditable = 1;
        $("#submit-button").hide();

        $('#media-tip').text('Click to select the files to attach');
        if (attached_media.length == 0){
                    $('#media-panel-title').text('Attach files:');
                } else {
                    if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                }
        $('#upload-form').show();
        $('#attach-button').text('Save');
    }
}
display = 0;
playing_media = null;
$(document).on("click","#media-slider > div", function (event) {

    if (isMediaEditable) {
        if (event.target.parentElement.id != "media-slider"){
            if (event.target.parentElement.classList.contains("selected-media")){
                event.target.parentElement.classList.remove("selected-media");
                img_src = event.target.getAttribute('src');
                idx = attached_media.indexOf(img_src);
                attached_media.splice(idx,1);
                if (attached_media.length == 0){
                    $('#media-panel-title').text('Attach files:');
                } else {
                    if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                }
            }
            else{
             attached_media.push(event.target.getAttribute('src'));
             event.target.parentElement.classList.add("selected-media");
             if (attached_media.length == 1){
                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {
                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
            }
        }
    } else {
        if (display == 0){
            src_img = $(this).find('img').attr('src');
            src_video = $(this).find('video').attr('src');
            if (src_img == null){
                $("#zoom-video").attr('src',src_video);
                $("#zoom-video").show();
                $("#zoom-img").hide();
                console.log($(this).find('video').attr('src'));
                playing_media = src_video;
            } else {
                $("#zoom-img").attr('src',src_img);
                $("#zoom-video").hide();
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
