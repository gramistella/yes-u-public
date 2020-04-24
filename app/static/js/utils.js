var generate_media_html = function(ids, urls, idx, displayControls){
    html = '';
    ext = urls[idx].split('.')[1];
    if (ext == 'mp4'){

            html += '<video class="single-media" poster="\\static\\media_posters\\'+ urls[idx].slice(21,urls[idx].length-4) + '.png" ><source src="'+urls[idx]+'" type="video/mp4">Your browser does not support HTML5 video.</video>';
    }else if (ext == 'pdf'){
            pdf_name = urls[idx].substring(21);
            pdf_name = pdf_name.substring(0, pdf_name.length-4);
            html = '<div class="pdf-container"><img class="single-media" src="\\static\\resources\\pdf-placeholder-icon.png" ><p>'+ pdf_name +'</p></div>';
    }else{
            html = '<img class="single-media" src="'+urls[idx]+'" >';
        }

    html = '<div id="single-media-'+idx+'" href="#" onclick="openMedia(event);">'+ html +'</div>';
    return html;
};

var applySelectionCallback = function(attached_media){
    media_slider = document.getElementById('media-slider');
    children = media_slider.childNodes;
    for(i = 0; i < children.length; i++){
        selected_node = children[i];
        src_img = $(selected_node).find('img').attr('src');
        pdf_name = $(selected_node).find('div').find('p').text();
        src_pdf = '\\static\\user_uploads\\' + pdf_name + '.pdf';
        src_video = $(selected_node).find('video').find('source').attr('src');
        if (attached_media.includes(src_video) || attached_media.includes(src_pdf) || attached_media.includes(src_img)){
            if (!selected_node.classList.contains('pdf-container')){
                selected_node.classList.add("selected-media");
            }
        }
    }
};

var refreshMedia = function(displayControls = false, _callback = null, attached_media = null){
    media_slider = document.getElementById('media-slider');
    while (media_slider.firstChild) {
        media_slider.firstChild.remove();
    }
    console.log(refreshMedia.caller.toString());
    fetch(`/backend?t=1`).then((response) => {
        // Convert the response data to JSON
        console.log('fetched data');
        response.json().then((data) => {
                ids = data['ids'];
                urls = data['urls'];
                console.log(urls);

                for (var i=0; i < urls.length ;i++){
                    html = generate_media_html(ids, urls, i, displayControls);
                    media_slider.insertAdjacentHTML("beforeend", html);
                }
            }).then(() => {
                if (_callback != null){
                    if (attached_media != null){
                        _callback(attached_media);
                    } else {
                        console.log('Callback detected but no parameters provided.');
                    }
                }
            });
    });
};

function bytesToSize(bytes) {
   var sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
   if (bytes == 0) return '0 Byte';
   var i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)));
   return Math.round(bytes / Math.pow(1024, i), 2) + ' ' + sizes[i];
}