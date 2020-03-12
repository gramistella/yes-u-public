$(document).ready(function () {

        var confirmation_display_works=0;
        var to_delete = null;
        work_id = null;

        var display=0;
        playing_media = null;
        $( "#zoom-close" ).click(function() {
          if (display == 1){

                document.getElementById("zoom-media").className = 'hidden';
                $("body").removeClass("modal-open");
                if (playing_media != null){
                    document.getElementById(playing_media).pause()
                }
                display = 0;
           }
        });
        $( ".media>div" ).click(function() {
            if (display == 0){
                src_img = $(this).find('img').attr('src');
                src_video = $(this).find('video').find('source').attr('src');
                if (src_img == null){
                    $("#zoom-video").attr('src',src_video);
                    $("#zoom-video").show();
                    $("#zoom-img").hide();
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
        $( ".work-buttons > a.delete" ).click(function( event ) {

            if (confirmation_display_works == 0){
                    $("#confirmation-dialog-container").css("display", "unset");
                    $("body").addClass("modal-open");
                    confirmation_display = 1;
                    work_id =  $(event.target).parent(".work-buttons").parent().parent().parent().parent().attr('id');
                    work_id = work_id.split("_")[1];

             }
        });
        $( ".confirmation-dialog-buttons > a.delete" ).click(function(){

            $.ajax({
                url: '/works/delete',
                type: 'POST',
                data: JSON.stringify ({
                    'work_id': work_id
                }),

                contentType: "application/json",
                dataType: 'json',
                success: function(response){
                    location.reload()
                }
        });


        });
        $( ".confirmation-dialog-buttons > a.cancel" ).click(function(){
            $("#confirmation-dialog-container").css("display", "none");
            $("body").removeClass("modal-open");
            confirmation_display_works = 0;
        });

    });

