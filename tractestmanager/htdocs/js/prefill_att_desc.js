$(document).ready(function(){
    pat = new RegExp(/(?:\?|&)([^#&=]+=[^#&=]+)/gi);
    var myArray;
    var match;
    while ((match = pat.exec(location.href)) !== null)
    {
        foo = match[1].split('=');
        if(foo[0] == 'testman_cnum'){
            var cnum = $('<input>').attr({
                type: 'hidden',
                name: 'testman_cnum',
                value: foo[1]
            }).appendTo('#attachment');
        }
    }
});
