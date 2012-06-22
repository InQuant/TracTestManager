jQuery(document).ready(function($) {


    $('input:button').click(function(){
        var actionid = parseInt(this.parentElement.id);
        set_status(actionid, this.value);
        var trig = $(this.parentElement.previousElementSibling);
        var duration = 100;
        // close old container
        if ( trig.hasClass('trigger_active') ) {
            trig.next('.toggle_container').slideToggle(duration);
        } else {
            $('.trigger_active').next('.toggle_container').slideToggle(duration);
            trig.next('.toggle_container').slideToggle(duration);
        };
        if($(this.parentElement.parentElement.parentElement.nextElementSibling) != null){
            var trig = $(this.parentElement.parentElement.parentElement.nextElementSibling.children[0].children[1]);
            if (trig != null){
                // the next one is opened, only close me
                if ( trig.next('.toggle_container')[0].style.display != "block" ){
                    trig.next('.toggle_container').slideToggle(duration);
                };
            };
        };
        return false;
    });

    // Accordion
    $('.trigger').not('.trigger_active').next('.toggle_container').hide();
    $("[class^=trigger]:first").next('.toggle_container').slideToggle(0);
    
    $('.trigger').click( function() {
        var trig = $(this);
        var duration = 100;
        if ( trig.hasClass('trigger_active') ) {
            trig.next('.toggle_container').slideToggle(duration);
        } else {
            $('.trigger_active').next('.toggle_container').slideToggle(duration);
            trig.next('.toggle_container').slideToggle(duration);
        };
        return false;
    });                       
});

var set_status = function($id, $value){
    var inputs = $("#accordion" + $id + ' :input');
    var values = {};
    inputs.each(function(){
        values[this.name] = $(this).val();
    });
    t_area            = $('#accordion'+values['action']).find('textarea')[0];
    if(t_area.value && $value == "passed"){
        values['comment'] = t_area.value;
        values['status']  = "passed with comment";
    }
    else{
        values['status']  = $value;
    }
    url               = getBaseURL()+'trac/json_testaction';
    // do the post request
    $.post(url, values, function(data){
        json = jQuery.parseJSON(data);
        $("#accordion" + $id)[0].children[1].style['background'] = status_color[json.status];
    });
};

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

