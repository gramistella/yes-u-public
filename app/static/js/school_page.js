isShowingPdf = false;
var display=0;
playing_media = null;
debug_this = null;
var openMedia = function(){
    event.preventDefault();
    if (display == 1){
        if (isShowingPdf){
                    isShowingPdf = false;
        }
        document.getElementById("zoom-media").className = 'hidden';
        $("body").removeClass("modal-open");
        if (playing_media != null){
            document.getElementById('zoom-video').pause();
        }
        display = 0;
    } else {

        if ($(event.target).prop('tagName') != 'A'){
            console.log($(event.target));
            media_id = $(event.currentTarget).attr('id').substring(13);
            src_img = $(event.currentTarget).find('img').attr('src');
            src_img_pdf = $(event.currentTarget).find('div').find('img').attr('src');
            src_video = $(event.currentTarget).find('video').find('source').attr('src');
            if (src_video != null){
                $("#zoom-video").attr('src',src_video);
                $("#zoom-video").show();
                $("#zoom-img").hide();
                $("#zoom-pdf").hide();
                playing_media = $(this);
            } else if (src_img_pdf != null){
                pdf_name = $(event.currentTarget).find('div').find('p').text()
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

            if ( $('#zoom-media > a.button.delete').length ){
                $('#zoom-media > a.button.delete').attr('onClick', 'deleteMedia(event, '+ media_id +');');
            }
            document.getElementById("zoom-media").className = 'flex';
            $("body").addClass("modal-open");
            display = 1;
        }
    }
};