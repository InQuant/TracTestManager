jQuery(document).ready(function($) {
    
    //var _btn_name;
    //var _btn_obj;
    
    //$("form").submit(function() {
        //// Call an URL when the form is submitted
        //// 
        //var _id = _btn_obj.parent().get(0).id;
        //var _txtarea = $('#'+_id).find('textarea').val();
        //var _testrun = $('#'+_id).find('.testrun').val();
        //var _authname = $('#'+_id).parent().parent().find('#authname').val();
        //var _form_token = $('[name=__FORM_TOKEN]')[0].value;
        

        //$.post(url, { 
            //id: _id, 
            //txtarea: _txtarea,
            //testrun: _testrun,
            //authname: _authname,
            //__FORM_TOKEN: _form_token
            //},
            //function(data) {
                //// insert result-handling-code here
        //});

        //return false;
    //});

    //$('input[type=submit]').click(function(){            
        //_btn_name = $(this).attr('name');
        //_btn_obj = $(this); 
    //})
    
    $('form').submit(function(){
        var inputs = $("#" + this.id + ' :input');
        var values = {};
        inputs.each(function(){
            values[this.name] = $(this).val();
        });
        values['comment'] = $('#'+values['id']).find('textarea').val();
        url = getBaseURL()+'trac/json_testaction';
        $.post(url, values, function(data){
            console.log(data)
        });
        return false;
    });

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
