var isWorkEditable = 0;
var attached_media = [];

(function () {
    var a = document.getElementById("body"),
    limit = 12;//Define max lines limit

    if (a != null){
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
    }
})();

var editWork = function()
{
    if (isWorkEditable){

        $('#edit-button').text('Edit');
        $('#work > h4').text("");
        $('#work > h4').text($('#form-title > #title').val());
        $('#description > p').text($('#form-description > #body').val());

        isWorkEditable = 0;
        var unique_attached_media = attached_media.reduce(function(a,b){
            if (a.indexOf(b) < 0 ) a.push(b);
                return a;
        },[]);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/backend', true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify({
            type: 3,
            work_id: $('meta[name=work_id]').attr("id"),
            title: $('#form-title > #title').val(),
            description: $('#form-description > #body').val(),
            attached_media: unique_attached_media
        }));
        media_slider_public = document.getElementById('media-slider-public');
        while (media_slider_public.firstChild) {
            media_slider_public.firstChild.remove();
        }

        ids = [];
        urls = attached_media;

        for (var i=0; i<attached_media.length; i++){
            html = generate_media_html(ids, urls, i, true);
            media_slider_public.insertAdjacentHTML("beforeend", html);
        }

        $('#work').show();
        $('#edit-form').hide();
        $('#form-description > #body').text("");
        if (attached_media.length == 0){
            $('#public-media-tip').text("No media to show");
        } else {
            $('#public-media-tip').text("Click media to open");
        }
    } else {
        $('#edit-button').text('Save edits');
        $('#media-tip').text('Click to select the media files to attach');
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
                    ids = data['ids'];
                    urls = data['urls'];
                    var raw_src = [];
                    media_slider_public_children = media_slider_public.children;
                    for (var i=0; i < media_slider_public_children.length; i++){
                        attached_img_src = media_slider_public_children[i].children[0].getAttribute('src');
                        attached_video = media_slider_public_children[i].getElementsByTagName('video');
                        attached_pdf = media_slider_public_children[i].getElementsByTagName('p');
                        media_to_push = null;
                        //.log(attached_img_src);
                        if (attached_img_src != null && attached_img_src != '/static/resources/play-button.png'){
                            media_to_push = attached_img_src;

                        } else if (attached_video.length != 0){

                            var s = $(attached_video[0]).find('Source:first').attr('src')
                            var n = s.indexOf('#');
                            media_to_push = s.substring(0, n != -1 ? n : s.length);

                        } else if (attached_pdf.length != 0){
                            pdf_name = attached_pdf[0].textContent;
                            pdf_src = '/static/user_uploads/' + pdf_name + '.pdf';
                            media_to_push = pdf_src;
                        }
                        if (media_to_push != null){
                            raw_src.push(media_to_push);
                        } else {
                            console.log('Media to push is null!');

                        }
                    }

                    uniqueArray = raw_src.filter(function(item, pos) {
                            return raw_src.indexOf(item) == pos;
                        });

                    if (attached_media.length == 0) {
                            for (var i=0; i < uniqueArray.length; i++){
                                attached_media.push(uniqueArray[i]);
                            }
                        }

                    while (media_slider_private.firstChild) {
                            media_slider_private.firstChild.remove();
                        }

                    console.log(attached_media);
                    for (var i=0; i < urls.length ;i++){

                        html = generate_media_html(ids, urls, i);
                        replaced_string = urls[i].replace(/\/\//g, "/");

                        if (attached_media.includes(replaced_string)){
                            html = html.slice(0, 24) + 'class="selected-media"' + html.slice(24);
                        }

                        media_slider_private.insertAdjacentHTML("beforeend", html);
                    }
                    if (attached_media.length == 0){

                        $('#media-panel-title').text('Attach files:');
                    } else if (attached_media.length == 1){

                        $('#media-panel-title').text(attached_media.length + " file selected");
                    } else {

                        $('#media-panel-title').text(attached_media.length + " files selected");
                    }
                })
            })
        isWorkEditable = 1;

    }
}

display = 0;
playing_media = null;

$(document).on("click tap","#media-slider > div", function (event) {

    if (isWorkEditable){

        if (!event.currentTarget.classList.contains("selected-media")){
            event.currentTarget.classList.add("selected-media");
            src_img = $(this).find('img').attr('src');
            src_img_pdf = $(this).find('div').find('img').attr('src');
            src_video = $(this).find('video').find('source').attr('src');
            media_src = null;

            if (src_img != null && src_img_pdf == null){
                media_src = src_img;
            } else if (src_video != null){

                media_src = src_video;
            } else if (src_img_pdf != null){
                pdf_name = event.currentTarget.firstChild.children[1].textContent
                pdf_src = '/static/user_uploads/' + pdf_name + '.pdf';
                media_src = pdf_src;
            }
            if (!attached_media.includes(media_src)){
                attached_media.push(media_src);

            }
        }
        else {
            event.currentTarget.classList.remove("selected-media");
            src_img = $(this).find('img').attr('src');
            src_img_pdf = $(this).find('div').find('img').attr('src');
            src_video = $(this).find('video').find('source').attr('src');
            media_src = null;

            if (src_img != null && src_img_pdf == null){
                media_src = src_img;
            } else if (src_video != null){
                media_src = src_video;
            } else if (src_img_pdf != null){
                pdf_name = event.currentTarget.firstChild.children[1].textContent
                pdf_src = '/static/user_uploads/' + pdf_name + '.pdf';
                media_src = pdf_src;
            }
            if (attached_media.includes(media_src)){
                idx = attached_media.indexOf(media_src);
                attached_media.splice(idx,1);
            }

        }
        if (attached_media.length == 0){
            $('#media-panel-title').text('Attach files:');
        } else if (attached_media.length == 1){
            $('#media-panel-title').text(attached_media.length + " file selected");
        } else {
            $('#media-panel-title').text(attached_media.length + " files selected");
        }
    }
});

$(document).on("click tap","#media-slider-public > div", function (event) {

    if (display == 0){
        src_img = $(this).find('img').attr('src');
        src_img_pdf = $(this).find('div').find('img').attr('src');
        src_video = $(event.currentTarget).find('video').find('source').attr('src');
        if (src_video != null){
            $("#zoom-video").attr('src',src_video);
            $("#zoom-video").show();
            $("#zoom-img").hide();
            $("#zoom-pdf").hide();
            playing_media = $(this);
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
});


$(document).on("click tap","#zoom-close",function() {
      if (display == 1){
            document.getElementById("zoom-media").className = 'hidden';
            $("body").removeClass("modal-open");
            if (playing_media != null){
                document.getElementById('zoom-video').pause()
            }
            display = 0;
       }
    });