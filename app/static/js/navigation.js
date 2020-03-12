isToggled = 0
function toggleNav() {
        if (isToggled == 0){
            $(".icon").addClass("close");
            $(".nav-window").show();
			isToggled = 1
            $(".container").addClass("open");

        } else {
             $(".icon").removeClass("close");
            $(".nav-window").hide();
			isToggled = 0
            $(".container").removeClass("open");
        }
}

window.onresize = function() {
    if (window.innerWidth >= 768) {
        if (isToggled == 1){
            toggleNav()
        }
    }
}