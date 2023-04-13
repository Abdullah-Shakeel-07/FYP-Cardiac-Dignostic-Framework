document.addEventListener("DOMContentLoaded", function() {
    var text = document.querySelector(".text");
    var textHeight = text.clientHeight;
    var windowHeight = window.innerHeight;
    var offset = textHeight - windowHeight;

    window.addEventListener("scroll", function() {
        var scrollY = window.scrollY;

        if (scrollY > offset) {
            text.classList.add("animate");
        } else {
            text.classList.remove("animate");
        }
    });
});