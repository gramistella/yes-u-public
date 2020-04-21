isShowingPdf = false

$(document).ready(function () {

        var display=0;
        playing_media = null;

        $(document).on("click tap", "#zoom-close", function() {
          if (display == 1){

                if (isShowingPdf){
                    isShowingPdf = false;
                }
                document.getElementById("zoom-media").className = 'hidden';
                $("body").removeClass("modal-open");
                if (playing_media != null){
                    document.getElementById('zoom-video').pause()
                }
                display = 0;
           }
        });
        $(document).on("click tap","#media-slider > div", function(event) {
            if ($(event.target).prop('tagName') != 'A'){
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

                    if ( $('#zoom-media > a.button.delete').length ){
                        $('#zoom-media > a.button.delete').attr('onClick', 'deleteMedia('+ media_id +');');
                    }
                    document.getElementById("zoom-media").className = 'flex';
                    $("body").addClass("modal-open");
                    display = 1;
                }
            }
        });

    });
