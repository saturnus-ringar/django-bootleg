window.onerror = function(msg, url, line) {
    var params = "msg=" + encodeURIComponent(msg) + '&url=' + encodeURIComponent(url) + "&line=" + line;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', "/xhr/javascript-error/", true);
    xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
    xhr.send(params);
};

window.onload = function() {
    if (!window.jQuery) {
        alert("jquery is required for the bootleg-javascript to run.");
    }
}

$(document).ready(function() {
    initSelect2s();
    highlightSearchResults();
    autoFocus();
});

// create loading-spinners on buttons when forms are submitted
$("form").submit(function() {
    var submitButton = $(this).find("input[type=\'submit\']");
    submitButton.prop("disabled", true);
    if(submitButton.hasClass("loading-button")) {
        submitButton.html(submitButton.after('<span class="spinner-border text-primary spinner-border-sm ml-2" ' +
            'role="status" aria-hidden="true"></span>'));
    }
});

// add a loader-button on the password reset button
if($("form[id='Forgot password']").length > 0) {
    $("form[id='Forgot password'] button[type=submit]").addClass("loading-button")
}

function autoFocus() {
    $('.autofocus').each(function() {
        if(!$(this).val()) {
            $(this).focus();
        }
    });
}

function initSelect2s() {
    $('.select').select2();
}

function highlightSearchResults() {
    $(".table-container").highlight(getURLParameter("q"));
}

function getURLParameter(name) {
    return decodeURIComponent((RegExp('[?|&]' + name + '=' + '(.+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}
