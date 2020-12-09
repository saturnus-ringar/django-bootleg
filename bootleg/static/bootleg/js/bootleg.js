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

$.ajaxSetup({
    error : function(x,e) {
        if(x.status == 0) {
            alert(Text.unknownError);
        } else if(x.status == 404) {
            alert(Text.urlNotFound);
        } else if(x.status == 500) {
            alert(Text.internalServerError);
        } else if(e == 'parsererror') {
            alert(Text.jsonParseError);
        } else if(e == 'timeout') {
            alert(Text.requestTimeout);
        } else if(x.status != 400) {
            alert(Text.unknownError);
        }
    }
});


$(document).ready(function() {
    initSelect2s();
    highlightSearchResults();
    initGenericAutocomplete();
    initGenericAutocompletes();
    autoFocus();
});

$("input.dateinput").each(function() {
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

function autoFocus() {
    // focus on the first empty text input in #bootleg_form
    $("#bootleg_form *").filter(':input').each(function(){
        if($(this).val() == "") {
            this.focus();
            return false;
        }
    });
}

function initSelect2s() {
    $('.select').select2();
}

function initGenericAutocomplete() {
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

function initGenericAutocompletes() {
    var inputTypes = ["number", "text"]
    $("#bootleg_model_filter_form input").each(function() {
        if(inputTypes.includes($(this).prop("type"))) {
            if($(this).hasClass("datetimeinput")) {
                return;
            }
            var model = $("#bootleg_model_filter_form").data("model");
            var field = $(this).attr("name");
            var options = {
                url: function (query) {
                    // TODO: don't hardcode the URL
                    return "/json/" + model + "/" + field + "?q=" + encodeURI(query);
                },
                list: {
                    maxNumberOfElements: 50,
                },
            };
            $(this).easyAutocomplete(options);
        }
    });
}

function highlightSearchResults() {
    var query = getURLParameter("q");
    for(var key in getParams(window.location.href)) {
        $(this).highlight(getURLParameter(key));
        var value = getURLParameter(key);
        $(".table-container tbody tr").each(function() {
            $(this).find("td").each(function() {
                var fieldName = $(this).data("field-name");
                if(fieldName != "") {
                    if(query != "") {
                        $(this).highlight(query);
                    }
                    if($(this).data("field-name") == key && $(this).data("object-id") == value) {
                        $(this).highlight($(this).text());
                    }
                }
            })
         });
    }
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

function scrollToElement(targetId, extraOffset=0) {
    $([document.documentElement, document.body]).animate({
        scrollTop: $(targetId).offset().top - getNavbarOffset() + extraOffset
    }, 500);
}

// scroll-to-anchor-links
$("a.anchor").on("click", function() {
    clearActiveInListGroup();
    $(this).addClass("active");
    $([document.documentElement, document.body]).animate({
        scrollTop: scrollToElement($(this).data("target"))
    }, 500);
});

// element removers
$(document).on("click", '.element-remover', function(e) {
   e.preventDefault();
   $($(this).data("element-id")).remove();
});

// object view loaders in them tables
$(".object-view-loader").on("click", function(e) {
    e.preventDefault();
    var objectId = $(this).data("object-id");
    var tr = $("tr#object_row_" + objectId);
    var objectViewID = "object_view_" + objectId;
    if($("#" + objectViewID).length == 0) {
        var newTR = $('<tr id="' + objectViewID + '"></tr>');
        var newTD = $('<td class="no-border" colspan="100"></td>').hide();
        tr.after(newTR);
        newTR.append(newTD);
        newTD.load($(this).data("url"), function () {
            newTD.fadeIn();
            scrollToElement("#object_top_"+ objectId, extraOffset=-50);
        });
    } else {
        $("#" + objectViewID).remove();
    }
});

function clearActiveInListGroup() {
     $('.list-group a').each(function() {
         $(this).removeClass("active");
     });
}


// confirmation links
$("a.confirmation-link").on("click", function() {
    if(!confirm($(this).data("text"))) {
        return false
    }
});

// changes on the selects in the generic model filter form
$("#bootleg_model_filter_form select").change(function() {
    handleGenericModelFilter();
});

$("#bootleg_model_filter_form input:checkbox").change(function() {
    handleGenericModelFilter();
});

// bootleg generic filter form
$("#bootleg_model_filter_form").submit(function(e) {
    e.preventDefault();
    handleGenericModelFilter();
});

// generic model search submit
$("#bootleg_q_form").submit(function(e) {
    e.preventDefault();
    handleGenericModelFilter();
});

function handleGenericModelFilter() {
    MainLoader.start();
    var serialized = getSerializedForms(["#bootleg_model_filter_form", "#bootleg_q_form"]);
    window.location.href = serialized
}

var MainLoader = {

    spinnerOpts: {
        lines: 13,
        length: 28,
        width: 5,
        radius: 20,
        scale: 0.5,
        corners: 1,
        color: "#000",
        opacity: 0.25,
        rotate: 0,
        direction: 1,
        speed: 1,
        trail: 60,
        fps: 20,
        zIndex: 2e9,
        className: "spinner",
        top: "50%",
        left: "50%",
        shadow: false,
        hwaccel: false,
        position: "absolute"
    },

    spinner: new Spinner(this.spinnerOpts),

    start : function() {
        $('<div id="overlay"></div>').hide().appendTo("body").show(0, function() {
            MainLoader.spinner.spin(document.body);
        });
    },

    stop : function() {
        $("#overlay").hide(0, function() {
            MainLoader.spinner.stop();
            $(this).remove();
        });
    }
};


function getSerializedForms(formIds) {
    var serialized = "?"
    for(i = 0; i < formIds.length; i++) {
        var formData = getSerializedFormWithoutEmptyValues(formIds[i]);
        if(formData) {
            if(i > 0 && serialized.length > 1) {
                serialized += "&" + formData
            } else {
                serialized += formData
            }
        }
    }
    return serialized;
}

function getSerializedFormWithoutEmptyValues(formId) {
    // http://stackoverflow.com/questions/608730/how-do-i-use-jquerys-form-serialize-but-exclude-empty-fields
    var form = $(formId);
    if(form.length > 0) {
        var serialized = $(formId).serialize();
        var cleaned = serialized.replace(/[^&]+=\.?(&|$)/g, '');
        return cleaned.replace(/&$/, ''); // remove traling &
    }
    return null;
}

function getURLParameter(name) {
    return decodeURIComponent((RegExp('[?|&]' + name + '=' + '(.+?)(&|#|;|$)').exec(location.search) || [, ""])[1].replace(/\+/g, '%20')) || null;
}

// https://gomakethings.com/getting-all-query-string-values-from-a-url-with-vanilla-js/
var getParams = function (url) {
	var params = {};
	var parser = document.createElement('a');
	parser.href = url;
	var query = parser.search.substring(1);
	var vars = query.split('&');
	for (var i = 0; i < vars.length; i++) {
		var pair = vars[i].split('=');
		params[pair[0]] = decodeURIComponent(pair[1]);
	}
	return params;
};