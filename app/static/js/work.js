isWorkEditable = 0
attached_media = []

var editWork = function()
{
    if (isWorkEditable){

        $('#edit-button').text('Edit Work');
        $('#work > h4').text("");
        $('#work > h4').text($('#form-title > #title').val());
        $('#description > p').text($('#form-description > #body').val());
        isWorkEditable = 0;
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/backend', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({
         type: 3,
         work_id: $('meta[name=work_id]').attr("id"),
         title: $('#form-title > #title').val(),
         description: $('#form-description > #body').val(),
         attached_media: attached_media
        }));
        media_slider_public = document.getElementById('media-slider-public');
        while (media_slider_public.firstChild) {
                            media_slider_public.firstChild.remove();
                        }
        for (var i=0; i<attached_media.length; i++){
            ext = attached_media[i].split('.')[1];
            if (ext == 'mp4'){
                html = '<div><video id="single-video-'+i+'" src="'+attached_media[i]+'" style="width:310px;height:auto"></video>';
            } else {
                html = '<div><img id="single-media-'+i+'" src="'+attached_media[i]+'" style="width:310px;height:auto"></div>';
            }
            media_slider_public.insertAdjacentHTML("beforeend", html);
        }

        $('#work').show();
        $('#edit-form').hide();
        $('#form-description > #body').text("");
        $('.media-tip').text('');
    } else {
        $('#edit-button').text('Save edits');
        $('#work').hide();
        $('#edit-form').show();
        $('#form-title > #title').val("");
        $('#form-title > #title').val($('#work > h4').text());
        $('#form-description > #body').text($('#description > p').text());
        fetch(`/backend?t=1`).then((response) => {
            // Convert the response data to JSON
            response.json().then((data) => {
                    media_slider_public = document.getElementById('media-slider-public');
                    media_slider_private = document.getElementById('media-slider');
                    var raw_src = [];
                    media_slider_public_children = media_slider_public.children;
                    for (var i=0; i < media_slider_public_children.length; i++){
                        attached_media_src = media_slider_public_children[i].children[0].getAttribute('src')
                        if (attached_media_src == null){
                            attached_media_src = media_slider_public_children[i].children[0].children[0].getAttribute('src')
                        }
                        raw_src.push(attached_media_src);
                    }

                    uniqueArray = raw_src.filter(function(item, pos) {
                            return raw_src.indexOf(item) == pos;
                        });

                    if (attached_media.length == 0) {
                            for (var i=0; i < uniqueArray.length; i++){
                                attached_media.push(uniqueArray[i]);
                            }
                        }

                    console.log(attached_media);
                    while (media_slider_private.firstChild) {
                            media_slider_private.firstChild.remove();
                        }
                    for (var i=0; i < data.length ;i++){
                        var html = ""
                        console.log(data[i])
                        ext = data[i].split('.')[1];
                        if (ext == 'mp4'){
                            html = '<div><video id="single-video-'+i+'" src="'+data[i]+'" style="width:310px;height:auto"></video>';
                        } else {
                            html = '<div><img id="single-media-'+i+'" src="'+data[i]+'" style="width:310px;height:auto"></div>';
                        }

                        if (attached_media.includes(data[i])){
                            html = html.slice(0, 4) + ' class="selected-media"' + html.slice(4);
                        }

                        media_slider_private.insertAdjacentHTML("beforeend", html);
                    }
                })
            })
        $('.media-tip').text('Click to select the files you want to attach');
        isWorkEditable = 1;

    }
}

display = 0;
playing_media = null;

$(document).on("click","#media-slider > div", function (event) {
    if (isWorkEditable){
        if (event.target.parentElement.id != "media-slider"){
            if (event.target.parentElement.classList.contains("selected-media")){
                event.target.parentElement.classList.remove("selected-media");
                img_src = event.target.getAttribute('src');
                idx = attached_media.indexOf(img_src);
                attached_media.splice(idx,1);
            }
            else{
             attached_media.push(event.target.getAttribute('src'));
             event.target.parentElement.classList.add("selected-media");
            }
        }
    }
});

$(document).on("click","#media-slider-public > div", function (event) {

    if (display == 0){
        src_img = $(this).find('img').attr('src');
        src_video = $(this).children(0).children().attr('src')
        if (src_img == null){
            $("#zoom-video").attr('src',src_video);
            $("#zoom-video").show();
            $("#zoom-img").hide();
            console.log($(this).find('video').attr('src'));
            playing_media = $(this).find('video').attr('id');
        } else {
            $("#zoom-img").attr('src',src_img);
            $("#zoom-video").hide();
            $("#zoom-img").show();
        }
        document.getElementById("zoom-media").className = 'flex';
        $("body").addClass("modal-open");
        display = 1;
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