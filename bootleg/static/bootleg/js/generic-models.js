$(document).ready(function() {
    initGenericAutoComplete();
});

function initGenericAutoComplete() {
    var input = $("input#id_q");
    if(!input.hasClass("generic-autocomplete")) {
        return;
    }
    var options = {
        url: function(query) {
            return input.data("autocomplete-url") + "?q=" + encodeURI(query);
        },
        list: {
            maxNumberOfElements: 20,
        },
        theme: "plate-dark",
    };
    input.easyAutocomplete(options);
}
