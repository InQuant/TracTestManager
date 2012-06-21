jQuery(document).ready(function($) {

    // Accordion
    $('.trigger').not('.trigger_active').next('.toggle_container').hide();
    // show the first container - buggy!
    // $("[class^=toggle_container]:first").show();
    
    $('.trigger').click( function() {
        var trig = $(this);
        var duration = 100;
        if ( trig.hasClass('trigger_active') ) {
            trig.next('.toggle_container').slideToggle(duration);
            trig.removeClass('trigger_active');
            trig.css("background","white");                
        } else {
            $('.trigger_active').next('.toggle_container').slideToggle(duration);
            $('.trigger_active').removeClass('trigger_active');                
            trig.next('.toggle_container').slideToggle(duration);
            trig.css("background","#eee");
            trig.addClass('trigger_active');
        };
        return false;
    });                       
});

function getBaseURL() {
    var url = location.href;  // entire url including querystring - also: window.location.href;
    var baseURL = url.substring(0, url.indexOf('/', 14));


    if (baseURL.indexOf('http://localhost') != -1) {
        // Base Url for localhost
        var url = location.href;  // window.location.href;
        var pathname = location.pathname;  // window.location.pathname;
        var index1 = url.indexOf(pathname);
        var index2 = url.indexOf("/", index1 + 1);
        var baseLocalUrl = url.substr(0, index2);

        return baseLocalUrl + "/";
    }
    else {
        // Root Url for domain name
        return baseURL + "/";
    }

}

var set_status = function($id, $value){
    var inputs = $("#accordion" + $id + ' :input');
    var values = {};
    inputs.each(function(){
        values[this.name] = $(this).val();
    });
    t_area            = $('#accordion'+values['action']).find('textarea')[0];
    if(t_area.value){
        values['comment'] = t_area.value;
    }
    values['status']  = $value;
    url               = getBaseURL()+'trac/json_testaction';
    // do the post request
    $.post(url, values, function(data){
        console.log(data)
    });
};
