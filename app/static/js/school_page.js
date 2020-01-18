$(document).ready(function () {
        var small={width: "300px",height: "116px"};
        var large={width: "600px",height: "232px"};
        var display=0;
        $( ".close" ).click(function() {
          if (display == 1){

                document.getElementById("zoom-media").className = 'hidden';
                 $("body").removeClass("modal-open");
                display=0;
           }
        });
        $( ".media>div" ).click(function() {
            if (display == 0){
                src = $(this).find('img').attr('src');
                $("#zoom-img").attr('src',src);
                document.getElementById("zoom-media").className = 'flex';
                 $("body").addClass("modal-open");

                display=1;
            }
        });

    });