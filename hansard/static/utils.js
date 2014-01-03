var labelFromParty = function(party) {
    var label = "default";
    // hack: Use bootstrap labels for evil and profit!
    // I'm very okay that the colours work out as nicely as they do
    if (party === "LPC") {
        label = "danger";
    } else if (party === "CPC") {
        label = "primary";
    } else if (party === "NDP") {
        label = "warning";
    } else if (party === "BQ") {
        label = "info";
    } else if (party === "GP") {
        label = "success";
    }
    return label;
}

var getParameterByName = function(name, href) {
    name = name.replace(/[\[]/,"\\\[").replace(/[\]]/,"\\\]");
    var regexS = "[\\?&]"+name+"=([^&#]*)";
    var regex = new RegExp( regexS );
    var results = regex.exec( href );
    if( results == null ) {
        return "";
    } else {
        return decodeURIComponent(results[1].replace(/\+/g, " "));
    }
}