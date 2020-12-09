$('.results').doubleScroll();

window.addEventListener('load', function () {
    if(inIframe()) {
        var debugToolbar = document.getElementById("djDebug");
        if(debugToolbar) {
            debugToolbar.style.display = "none";
        }
    }
    var container = document.getElementById("container");
    linkifyElement(container);

    var togglers = document.getElementsByClassName("element-toggler");
        for(var i = 0; i < togglers.length; i++) {
            var toggler= togglers[i];
            toggler.onclick = function(e) {
                e.preventDefault();
                toggleVisibilityById(toggler.dataset.element);
            }
        }

});

function hideByClassName(className){
    var elements = document.getElementsByClassName(className);
    for (var i = 0; i < elements.length; i++){
        elements[i].style.display = "none";
    }
}

function toggleVisibilityById(id){
    var element = document.getElementById(id);
    if(element.classList.contains("hidden")) {
        element.classList.remove("hidden");
    } else {
        element.classList.add("hidden");
    }
}


function inIframe () {
    try {
        return window.self !== window.top;
    } catch (e) {
        return true;
    }
}

