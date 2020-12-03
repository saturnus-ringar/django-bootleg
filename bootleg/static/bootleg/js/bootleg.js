window.onerror = function(msg, url, line) {
    var params = "msg=" + encodeURIComponent(msg) + '&url=' + encodeURIComponent(url) + "&line=" + line;
    var xhr = new XMLHttpRequest();
    xhr.open('POST', Context.jsErrorURL, true);
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
    initGenericAutoComplete();
    autoFocus();
});

$("input.dateinput").each(function() {
    // TODO: get DATE_FORMAT from django-settings
    try {
        new Pikaday({
            field: $(this)[0],
            format: Context.dateFormat
        })
    } catch (error) {
        // the pikaday library might not be loaded
    }
});

$("input.datetimeinput").each(function() {
    try {
        // TODO: get DATE_FORMAT from django-settings
        new Pikaday({
            field: $(this)[0],
            format: Context.dateTimeFormat
        })
    } catch (error) {
        // the pikaday library might not be loaded
    }
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

// add loader on the search form
$("#bootleg_q_form").submit(function() {
    showElement($("#q_loader"));
});


function showElement(element) {
    element.removeClass("hidden");
}

function autoFocus() {
    // focus on the first empty text input in #bootleg_form
    $('#bootleg_form input').each(function(){
        if($(this).val() == '') {
            this.focus();
            return false;
        }
    });
}

function initSelect2s() {
    $('.select').select2();
}

function initGenericAutoComplete() {
    var input = $("input#id_q");
    if(!input.hasClass("generic-autocomplete")) {
        return;
    }
    var options = {
        adjustWidth: false,
        url: function(query) {
            return input.data("autocomplete-url") + "?q=" + encodeURI(query);
        },
        list: {
            maxNumberOfElements: 50,
        },
    };
    input.easyAutocomplete(options);
    $(".easy-autocomplete").addClass("w-75");
}

function highlightSearchResults() {
    $(".table-container").highlight(getURLParameter("q"));
}

function hasFixedNavbar() {
    if($("nav").hasClass("fixed-top")) {
        return true;
    }
    return false;
}

function getNavbarOffset() {
    if(hasFixedNavbar()) {
        return $("nav").height() + 40;
    }
    return 0;
}

$("a.anchor").on("click", function() {
    $([document.documentElement, document.body]).animate({
        scrollTop: $($(this).data("target")).offset().top - getNavbarOffset()
    }, 500);
});


$("a.confirmation-link").on("click", function(e) {
    if(!confirm($(this).data("confirmation-text"))) {
        e.preventDefault();
        return false
    }
});


function getURLParameter(name) {
    return decodeURIComponent((RegExp('[?|&]' + name + '=' + '(.+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}
