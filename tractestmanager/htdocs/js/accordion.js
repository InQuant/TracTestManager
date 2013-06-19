jQuery(document).ready(function($) {
    // initalize Accordion (hide all containers except first)
    $('.toggle_container').hide();
    $(".toggle_container").first().show()

    // Show / hide container when clicking on the step's headline
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

    // handle the button clicks (skipped / passed /failed)
    $('input:button').click(function(){
        var actionid = parseInt(this.parentNode.id);
        set_status(actionid, this.value);
        return false;
    });

    // handle the checkbox ()
    /*
    $('input:checkbox').click(function(){
        //document.getElementById("create_ticket").value= "yes";
        if (this.checked == true) {
            this.value= "yes";
        } else {
            this.value= "no";
        }
        return false;
    });
    */
});

var set_status_success =  function(data){
    //callback when setting the status was successful
    json = jQuery.parseJSON(data);
    var toggle_container_id = parseInt(json.toggle_container_id);

    // change clolor of step according to json.status
    $("#accordion" + toggle_container_id)[0].children[1].style['background'] = status_color[json.status];
    var duration = 100;

    // hide current container
    var toggle_container = $("#" + toggle_container_id);
    toggle_container.slideToggle(duration);

    // show next container
    var next_toggle_container = $("#" + (toggle_container_id + 1));
    if(next_toggle_container != null){
        if(next_toggle_container[0].style.display != "block"){
            next_toggle_container.slideToggle(duration);
        }
    };
};


var set_status_error =  function(data){
    //callback when setting the status wasn't successful
    json = jQuery.parseJSON(data.responseText);
    alert(json.message);
};


var set_status = function($id, $value){
    var inputs = $("#accordion" + $id + ' :input');
    var values = {};
    values["toggle_container_id"] = $id;

    values["option"]= false;
    inputs.each(function(){
        values[this.name] = $(this).val();
        if (this.name == "option" && this.checked == true ) {
            if (this.value == "create_ticket") {
                values["option"]= "create_ticket";
            } else {
                values["option"]= "create_attachment";
            }
        }
    });

    if(values["comment"] && $value == "passed"){
        values['status']  = "passed with comment";
    }
    else{
        values['status']  = $value;
    }
    url               = '../../../json_testaction';
    // do the post request
    $.ajax({
      type: 'POST',
      url: url,
      data: values,
      success: set_status_success,
      error: set_status_error,
      async:false
    });
};
