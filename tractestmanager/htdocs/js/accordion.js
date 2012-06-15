jQuery(document).ready(function($) {
    
    var btn_name;
    var btn_obj;
    
    $("form").submit(function() {
        url = getBaseURL()+'/trac/json_testaction?';
        // alert(btn);
        // json_testaction?user=testuser&id=1&status=failed&foo=bar&comment=fooobar&testrun=1        
        // alert( "id: "+btn_obj.parent().get(0).id );
        var id = btn_obj.parent().get(0).id;
        var txtarea = $('#'+id).find('textarea').val();
        var testrun = $('#'+id).find('.testrun').val();
        var authname = $('#'+id).parent().parent().find('#authname').val();
        $.get(url + 'user=' + authname + '&id=' + id + '&status=' + btn_name + '&comment=' + txtarea + '&testrun=' + testrun);
        return false;
    });

    $('input[type=submit]').click(function(){            
        btn_name = $(this).attr('name');
        btn_obj = $(this); 
    })

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
