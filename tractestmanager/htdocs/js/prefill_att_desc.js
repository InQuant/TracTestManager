$(document).ready(function(){
    pat = new RegExp(/(?:\?|&)([^#&=]+=[^#&=]+)/gi);
    var myArray;
    var match;
    while ((match = pat.exec(location.href)) !== null)
    {
        foo = match[1].split('=');
        if(foo[0] == 'description'){
            var description = $('#attachment :input[name=description]');
            description.val(decodeURI(foo[1]));
        }
    }
});
