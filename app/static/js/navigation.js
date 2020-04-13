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
window.ondragstart = function() {return false}

var coll = document.getElementsByClassName("collapsible");
var i;

for (i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function() {
    this.classList.toggle("active");
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
    } else {
      content.style.display = "block";
    }
  });
}