function hoverByClass(classname) {
    var elms = document.getElementsByClassName(classname);
    for (var i = 0; i < elms.length; i++) {
        elms[i].onmouseover = function () {
            for (var k = 0; k < elms.length; k++) {
                elms[k].classList.add("highlight")
            }
        };
        elms[i].onmouseout = function () {
            for (var k = 0; k < elms.length; k++) {
                elms[k].classList.remove("highlight");
            }
        };
    }
}