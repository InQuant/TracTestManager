jQuery(document).ready(function($) {


    $('input:button').click(function(){
        var actionid = parseInt(this.parentNode.id);
        set_status(actionid, this.value);
        var trig = $(this.parentNode.previousElementSibling);
        var duration = 100;
        // close old container
        if ( trig.hasClass('trigger_active') ) {
            trig.next('.toggle_container').slideToggle(duration);
        } else {
            $('.trigger_active').next('.toggle_container').slideToggle(duration);
            trig.next('.toggle_container').slideToggle(duration);
        };
        if($(this.parentNode.parentNode.parentNode.nextElementSibling) != null){
            var trig = $(this.parentNode.parentNode.parentNode.nextElementSibling.children[0].children[1]);
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
    url               = '../../../json_testaction';
    // do the post request
    $.post(url, values, function(data){
        json = jQuery.parseJSON(data);
        $("#accordion" + $id)[0].children[1].style['background'] = status_color[json.status];
    });
};
